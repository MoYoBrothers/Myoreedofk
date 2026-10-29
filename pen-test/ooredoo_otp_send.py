#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
 My Ooredoo (Algeria) v1.5.17 — FULL OTP LOGIN SCRIPT  [v3 — send + verify]
===============================================================================
 Target app   : My Ooredoo — com.algeria.selfcare.app.android v1.5.17 (1461)
 Source       : static reverse-engineering of 'My Ooredoo_1.5.17.apks'
                (jadx + Blutter Dart-AOT reversal + APK signing-block parse)
 Reconstructed functions (Dart AOT, libapp.so):
     ApiCalls::requestOTPbyMSISDN @ 0xb905b8  -> SMS OTP dispatch
     ApiCalls::loginWithOTP       @ 0xe3e88c  -> OTP verification grant
     ApiCalls::getAccessTokenByOtp @ 0xe3d204 -> OTP verification grant (dup)
     ApiCalls::getNonceValidation  @ 0x95c71c  -> checkpoint anti-replay nonce
     ApiCalls::setChecksumHeaders @ 0x92ab94   -> x-signature
     ApiCalls::setDeviceDataGatherForKeycloak @ 0x95c568 -> X-Platform-Info
     ApiCalls::setDeviceFingerprintHeader @ 0x92a480 -> X-Device-Fingerprint
     SignatureHelper::generateXSignature @ 0x1156ccc
     OnboardingMobileMainCubit::getAccessTokenByOTP closure @ 0xe3d730
       -> success = ApiResponse.success AND body["access_token"] is String
 Purpose      : replicate the COMPLETE app login:
                  (1) request the SMS OTP for a MSISDN,
                  (2) WAIT for the user to type the received code,
                  (3) submit it to the Keycloak token endpoint,
                  (4) print "LOGGED IN SUCCESSFULLY" (with the acquired
                      tokens) or "LOGIN FAILED".
 Output       : full request/response wire transcript (console + log file),
                decoded JWT session info, and — on success — the token set
                saved to a JSON file for pentest documentation.

 FLOW (verified against Dart AOT disassembly):
   STEP 1  POST {BASE}/api/ooredoo-bff/checkpoint/token      <- anti-replay
            harvest x-nonce-id / x-chronos-id from response headers
   STEP 2  POST {BASE}/api/auth/realms/myooredoo/protocol/openid-connect/token
            body: client_id=myooredoo-app & grant_type=password
                  & username=<MSISDN 213XXXXXXXXX> [& resend=true]
            -> triggers SMS OTP dispatch.
            NOTE (field-observed): this call may answer 401/403-empty while
            the SMS IS STILL DISPATCHED — treat non-2xx as "submitted",
            then watch the phone for the code.
   [WAIT]  user types the received OTP code (or 'r' = resend, Enter = abort)
   STEP 3  fresh checkpoint nonce (the app re-runs getNonceValidation()
            before EVERY token call — loginWithOTP @ 0xe3e900)
   STEP 4  POST {BASE}/api/auth/realms/myooredoo/protocol/openid-connect/token
            body: client_id=myooredoo-app & grant_type=password
                  & username=<MSISDN> & otp=<CODE>         <- @ 0xe3eb24
            (fallback variant: password=<CODE> via --password-param)
            -> HTTP 200 + {"access_token": "...", "refresh_token": "..."}
               == LOGIN SUCCESSFUL (same criteria as the app cubit).
               Keycloak "Invalid user credentials" / empty 40x == failure.

 LEGAL: for use ONLY in controlled/authorized security-testing environments
 against numbers you own or are authorized to test. No liability for misuse.
===============================================================================
"""

import argparse
import base64
import hashlib
import hmac as hmac_mod
import json
import logging
import os
import secrets
import sys
import time
import uuid
from datetime import datetime

try:
    import requests
    import urllib3
except ImportError:  # pragma: no cover
    sys.stderr.write("[!] 'requests' is required:  pip install requests\n")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Static configuration recovered from the APK (Dart string pool / asm / dex)
# ---------------------------------------------------------------------------
BASE_URL = "https://apis.ooredoo.dz"                      # EnvironmentSettings::getCurrentEnv @ 0x926110
EP_NONCE = "/api/ooredoo-bff/checkpoint/token"            # ApiCalls::getNonceValidation @ 0x95ca00
EP_TOKEN = "/api/auth/realms/myooredoo/protocol/openid-connect/token"  # requestOTPbyMSISDN @ 0xb90658
CLIENT_ID = "myooredoo-app"                               # @ 0xb9084c
APP_VERSION = "1.5.17"                                    # x-version header
USER_AGENT = "Dart/3.11 (dart:io)"                        # Dart http default UA
COUNTRY_CODE = "213"                                       # observed wire format: username=213xxxxxxx

# --- x-signature: computed from the GENUINE My Ooredoo 1.5.17 base.apk ------
# checksum   = String.valueOf(CRC32("classes.dex"))   = 3138619328
# signature = android.util.Base64(SHA-256(signing cert), flag 0)
#           = "KLYDvjaYq0SFAMqFTaEzMX0kQVR402qzUftEhMp6jyU=\n"
APK_CHECKSUM = "3138619328"
APK_SIGNATURE = "KLYDvjaYq0SFAMqFTaEzMX0kQVR402qzUftEhMp6jyU="
X_SIGNATURE = hashlib.sha256(
    (APK_CHECKSUM + APK_SIGNATURE + "\n").encode()
).hexdigest()  # Android Base64 flag-0 appends a trailing newline before hashing
# raw (no-newline) variant, kept for experimentation:
X_SIGNATURE_RAW = hashlib.sha256(
    (APK_CHECKSUM + APK_SIGNATURE).encode()
).hexdigest()

APP_HEADERS = {
    "platform": "android",
    "X-Platform-Origin": "mobile-android",
    "x-version": APP_VERSION,
    "x-force-update": "true",
}

LOG = logging.getLogger("ooredoo-login")


# ---------------------------------------------------------------------------
# MSISDN normalization — local 05XXXXXXXX -> Keycloak 213XXXXXXXXX
# ---------------------------------------------------------------------------
def normalize_msisdn(raw: str) -> str:
    """
    The token endpoint expects the international MSISDN form (report §3:
    'username=213xxxxxxx'). Accepts:
      0549908213 / 549908213 / +213549908213 / 00213549908213 / 213549908213
    and returns '213549908213'.
    """
    digits = "".join(c for c in raw if c.isdigit())
    if not digits:
        raise ValueError("no digits in MSISDN")
    if digits.startswith("00213"):                       # int'l dial prefix
        digits = digits[2:]
    if digits.startswith(COUNTRY_CODE) and len(digits) >= 12:
        return digits
    if digits.startswith("0"):                           # national trunk '0'
        digits = digits[1:]
    if len(digits) == 9:                                  # national significant number
        digits = COUNTRY_CODE + digits
    elif not digits.startswith(COUNTRY_CODE):
        # fall back: prepend country code anyway (operator DZ)
        digits = COUNTRY_CODE + digits.lstrip("0")
    return digits


# ---------------------------------------------------------------------------
# Persistent pseudo-device (stable X-Instance-Id / device-id across runs)
# ---------------------------------------------------------------------------
def load_or_create_device(state_file: str) -> dict:
    """Settings.getUUID() + device_info_plus androidId analogue."""
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass
    dev = {
        "uuid": str(uuid.uuid4()),                       # Settings::getUUID  @ 0x92aa58
        "device_id": secrets.token_hex(8),               # androidId — 16 hex chars
    }
    try:
        with open(state_file, "w", encoding="utf-8") as fh:
            json.dump(dev, fh, indent=2)
    except Exception:
        pass
    return dev


def platform_info_header(device: dict) -> str:
    """ApiCalls::setDeviceDataGatherForKeycloak @ 0x95c568 -> X-Platform-Info
    (JsonCodec.encode of {platform, is-physical-device, device-id})."""
    return json.dumps(
        {"platform": "android", "is-physical-device": True, "device-id": device["device_id"]},
        separators=(",", ":"), sort_keys=False,
    )


def device_fingerprint_header(device: dict, stored_msisdn: str, timestamp_ms: str) -> str:
    """SignatureHelper::generateDeviceFingerprint @ 0x92a630:
       HMAC-SHA256(key = utf8(ts), msg = utf8(msisdn + uuid + ts)).hexdigest()
    setDeviceFingerprintHeader passes stored Settings msisdn — which is EMPTY
    before the first successful login, so '' by default here."""
    msg = (stored_msisdn + device["uuid"] + timestamp_ms).encode()
    key = timestamp_ms.encode()
    return hmac_mod.new(key, msg, hashlib.sha256).hexdigest()


# ---------------------------------------------------------------------------
# Logging helpers — pentest-grade, full-wire documentation
# ---------------------------------------------------------------------------
def setup_logging(logfile: str | None, verbose: bool) -> logging.Logger:
    LOG.setLevel(logging.DEBUG)
    LOG.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", "%H:%M:%S")
    con = logging.StreamHandler(sys.stdout)
    con.setLevel(logging.DEBUG if verbose else logging.INFO)
    con.setFormatter(fmt)
    LOG.addHandler(con)
    fh = logging.FileHandler(logfile, mode="w", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
    LOG.addHandler(fh)
    LOG.info("Log file: %s", os.path.abspath(logfile))
    return LOG


def banner() -> None:
    LOG.info("=" * 76)
    LOG.info("My Ooredoo 1.5.17 — FULL OTP LOGIN (send + verify) replication")
    LOG.info("Reconstructed: requestOTPbyMSISDN @ 0xb905b8, loginWithOTP @ 0xe3e88c  [v3]")
    LOG.info("=" * 76)


def log_request(prep: requests.PreparedRequest) -> None:
    LOG.info("-" * 76)
    LOG.info(">> REQUEST  %s %s", prep.method, prep.url)
    for k, v in (prep.headers or {}).items():
        LOG.info(">> H  %s: %s", k, v)
    body = prep.body or ""
    if isinstance(body, bytes):
        try:
            body = body.decode("utf-8", "replace")
        except Exception:
            body = repr(body)
    if body:
        LOG.info(">> BODY  %s", body)


def log_response(resp: requests.Response) -> None:
    """FULL response display: status line, every header, and parsed body."""
    LOG.info("-- RESPONSE  HTTP %s %s  (%d bytes, %.0f ms)",
             resp.status_code, resp.reason, len(resp.content or b""),
             resp.elapsed.total_seconds() * 1000)
    for k, v in resp.headers.items():
        LOG.info("-- H  %s: %s", k, v)
    text = resp.text if resp.text else "(empty body)"
    try:
        LOG.info("-- BODY (pretty JSON):\n%s", json.dumps(json.loads(text), indent=2, ensure_ascii=False))
    except (ValueError, TypeError):
        LOG.info("-- BODY (raw):\n%s", text)
    LOG.info("-" * 76)


def do_request(session: requests.Session, prep: requests.PreparedRequest,
               timeout: float) -> requests.Response:
    log_request(prep)
    try:
        resp = session.send(prep, timeout=timeout)
    except requests.exceptions.SSLError as exc:
        LOG.error("[!] TLS error: %s", exc)
        raise SystemExit(2)
    except requests.exceptions.ConnectTimeout:
        LOG.error("[!] Connection timeout after %.1fs", timeout)
        raise SystemExit(2)
    except requests.exceptions.ConnectionError as exc:
        LOG.error("[!] Connection error: %s", exc)
        raise SystemExit(2)
    log_response(resp)
    return resp


def parse_extra_headers(items: list[str] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for it in items or []:
        if ":" not in it:
            LOG.warning("[!] ignoring malformed --extra-header: %r", it)
            continue
        k, v = it.split(":", 1)
        out[k.strip()] = v.strip()
    return out


# ---------------------------------------------------------------------------
# Device header bundle (x-signature + platform info + fingerprint)
# ---------------------------------------------------------------------------
def device_headers(device: dict, stored_msisdn: str) -> dict[str, str]:
    ts = str(int(time.time() * 1000))                    # DateTime._getCurrentMicros -> ms
    return {
        "x-signature": X_SIGNATURE,
        "X-Platform-Info": platform_info_header(device),
        "X-Timestamp": ts,
        "X-Instance-Id": device["uuid"],
        "X-Device-Fingerprint": device_fingerprint_header(device, stored_msisdn, ts),
    }


# ---------------------------------------------------------------------------
# STEP 1 — checkpoint nonce (ApiCalls::getNonceValidation)
# ---------------------------------------------------------------------------
def get_nonce(session: requests.Session, base: str, msisdn: str,
              extra: dict[str, str], device: dict, timeout: float) -> tuple[str, str]:
    """
    POST {base}/api/ooredoo-bff/checkpoint/token
      x-path   = the protected call path, x-method = POST
      harvests x-nonce-id / x-chronos-id from the RESPONSE HEADERS.
    """
    url = base + EP_NONCE
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
        "x-msisdn": msisdn,
        "x-path": EP_TOKEN,
        "x-method": "POST",
        "X-Correlation-ID": str(uuid.uuid1()),          # Uuid::v1 @ 0x92afa0
        **APP_HEADERS,
        **device_headers(device, stored_msisdn=""),
        **extra,
    }
    prep = session.prepare_request(requests.Request("POST", url, headers=headers, data={}))

    LOG.info("[STEP 1] checkpoint nonce — anti-replay pre-flight")
    resp = do_request(session, prep, timeout)

    nonce_id = resp.headers.get("x-nonce-id", "")
    chronos_id = resp.headers.get("x-chronos-id", "")
    if resp.ok and nonce_id:
        LOG.info("[+] nonce acquired  x-nonce-id=%s  x-chronos-id=%s",
                 nonce_id, chronos_id or "(absent)")
    else:
        LOG.warning("[!] checkpoint gave HTTP %s / nonce=%r — continuing "
                    "(app tolerates empty nonce @ 0xb908f8).", resp.status_code, nonce_id)
    return nonce_id, chronos_id


# ---------------------------------------------------------------------------
# STEP 2 — the OTP send (ApiCalls::requestOTPbyMSISDN)
# ---------------------------------------------------------------------------
def request_otp(session: requests.Session, base: str, msisdn: str,
                nonce_id: str, chronos_id: str, resend: bool,
                extra: dict[str, str], device: dict, timeout: float) -> requests.Response:
    """
    POST {base}/api/auth/realms/myooredoo/protocol/openid-connect/token
    Body (@ 0xb90840-0xb908b8): client_id, grant_type=password, username,
    resend=true (resend variant only).
    """
    url = base + EP_TOKEN
    form = {
        "client_id": CLIENT_ID,
        "grant_type": "password",
        "username": msisdn,                              # 213XXXXXXXXX form
    }
    if resend:
        form["resend"] = "true"                           # @ 0xb908a0

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "User-Agent": USER_AGENT,
        "x-msisdn": msisdn,
        "x-nonce-id": nonce_id,
        "x-chronos-id": chronos_id,
        "X-Correlation-ID": str(uuid.uuid1()),
        **APP_HEADERS,
        **device_headers(device, stored_msisdn=""),
        **extra,
    }
    prep = session.prepare_request(requests.Request("POST", url, headers=headers, data=form))

    LOG.info("[STEP 2] OTP request — grant-construction of requestOTPbyMSISDN%s",
             " (resend)" if resend else "")
    return do_request(session, prep, timeout)


# ---------------------------------------------------------------------------
# STEP 4 — OTP verification / login (ApiCalls::loginWithOTP @ 0xe3e88c,
#          identical twin: ApiCalls::getAccessTokenByOtp @ 0xe3d204)
# ---------------------------------------------------------------------------
def login_with_otp(session: requests.Session, base: str, msisdn: str, otp: str,
                   nonce_id: str, chronos_id: str, extra: dict[str, str],
                   device: dict, timeout: float, password_param: bool) -> requests.Response:
    """
    POST {base}/api/auth/realms/myooredoo/protocol/openid-connect/token
    Body (@ 0xe3ead4-0xe3eb2c):
        client_id=myooredoo-app, grant_type=password, username=<msisdn>,
        otp=<CODE>            <- custom form param, AOT-confirmed @ 0xe3eb24
    Headers (@ 0xe3eb34-0xe3ecb0): x-nonce-id/x-chronos-id harvested from the
    fresh getNonceValidation() response, x-msisdn, x-force-update, x-version,
    x-signature, X-Platform-Info, X-Timestamp, X-Instance-Id,
    X-Device-Fingerprint, platform, X-Platform-Origin.
    (X-JWS is only attached on Huawei devices via HuaweiAttestService — skipped.)
    """
    url = base + EP_TOKEN
    form = {
        "client_id": CLIENT_ID,
        "grant_type": "password",
        "username": msisdn,                              # 213XXXXXXXXX form
        ("password" if password_param else "otp"): otp,  # @ 0xe3eb24 ("otp")
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "User-Agent": USER_AGENT,
        "x-msisdn": msisdn,
        "x-nonce-id": nonce_id,
        "x-chronos-id": chronos_id,
        "X-Correlation-ID": str(uuid.uuid1()),
        **APP_HEADERS,
        **device_headers(device, stored_msisdn=""),
        **extra,
    }
    prep = session.prepare_request(requests.Request("POST", url, headers=headers, data=form))

    LOG.info("[STEP 4] OTP verification — grant-construction of loginWithOTP"
             " (param '%s')", "password" if password_param else "otp")
    return do_request(session, prep, timeout)


# ---------------------------------------------------------------------------
# JWT payload decode (no external deps) — proves the session is real
# ---------------------------------------------------------------------------
def decode_jwt_payload(token: str) -> dict | None:
    try:
        seg = token.split(".")[1]                        # header.payload.signature
        seg += "=" * (-len(seg) % 4)                     # fix base64 padding
        return json.loads(base64.urlsafe_b64decode(seg).decode("utf-8", "replace"))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Token-set persistence (pentest documentation)
# ---------------------------------------------------------------------------
def save_tokens(path: str, msisdn: str, tokens: dict) -> None:
    doc = {
        "msisdn": msisdn,
        "captured_at": datetime.now().isoformat(timespec="seconds"),
        "app": "My Ooredoo 1.5.17 (reconstructed loginWithOTP flow)",
        "tokens": tokens,
    }
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)
        LOG.info("[+] token set saved to: %s", os.path.abspath(path))
    except Exception as exc:
        LOG.warning("[!] could not save tokens (%s)", exc)


# ---------------------------------------------------------------------------
# Final verdict — the requested "logged in successfully or no"
# ---------------------------------------------------------------------------
def verdict_login(resp: requests.Response, password_param_used: bool) -> dict | None:
    """
    Returns the token-dict on SUCCESS (app criterion: 2xx AND access_token is
    a String — OnboardingMobileMainCubit closure @ 0xe3d730), else None.
    """
    body: dict = {}
    try:
        body = resp.json()
    except ValueError:
        body = {}
    access = body.get("access_token")

    LOG.info("=" * 76)
    if 200 <= resp.status_code < 300 and isinstance(access, str) and access:
        LOG.info("[+] ==============================")
        LOG.info("[+]     LOGGED IN SUCCESSFULLY    ")
        LOG.info("[+] ==============================")
        LOG.info("[i] verdict basis : HTTP %s + access_token present in body "
                 "(same criteria as OnboardingMobileMainCubit @ 0xe3d730)",
                 resp.status_code)
        if password_param_used:
            LOG.warning("[i] NOTE: success came via the fallback 'password' param, "
                        "not the AOT-confirmed 'otp' param.")
        LOG.info("[+] token_type    : %s", body.get("token_type", "(absent)"))
        LOG.info("[+] expires_in    : %s s", body.get("expires_in", "(absent)"))
        LOG.info("[+] scope         : %s", body.get("scope", "(absent)"))
        at = body.get("access_token", "")
        rt = body.get("refresh_token", "")
        LOG.info("[+] access_token  : %s%s", at[:38] + "…", "" if len(at) <= 38 else "")
        LOG.info("[+] refresh_token : %s%s", rt[:38] + "…", "" if len(rt) <= 38 else "")
        if body.get("refresh_expires_in") is not None:
            LOG.info("[+] refresh_expires_in: %s s", body["refresh_expires_in"])
        payload = decode_jwt_payload(at)
        if payload:
            LOG.info("[+] access_token JWT payload (decoded):")
            LOG.info("%s", json.dumps(payload, indent=2, ensure_ascii=False))
            exp = payload.get("exp")
            if isinstance(exp, (int, float)):
                remain = int(exp - time.time())
                LOG.info("[+] session validity: expires in %d min %d s (exp=%s)",
                         remain // 60, remain % 60, datetime.fromtimestamp(exp).isoformat())
        LOG.info("=" * 76)
        return body
    # ------------------------------- failure -------------------------------
    if 200 <= resp.status_code < 300:
        LOG.error("[!] LOGIN FAILED — HTTP %s but no access_token in body.", resp.status_code)
    elif resp.status_code == 401:
        LOG.error("[!] LOGIN FAILED — HTTP 401 (Keycloak: invalid credentials / wrong OTP).")
    elif resp.status_code == 403:
        LOG.error("[!] LOGIN FAILED — HTTP 403 (empty-body rejection, same signal the "
                  "OTP-dispatch step returns; no tokens were granted).")
    elif resp.status_code == 400:
        LOG.error("[!] LOGIN FAILED — HTTP 400 (malformed grant; see body above).")
    else:
        LOG.error("[!] LOGIN FAILED — HTTP %s.", resp.status_code)
    LOG.error("[i] If the OTP was correct but you still see this, capture the real app "
              "via proxy and replay its x-signature via --extra-header.")
    LOG.info("=" * 76)
    return None


# ---------------------------------------------------------------------------
# Interactive OTP input with resend support
# ---------------------------------------------------------------------------
def prompt_otp(max_resends: int = 5) -> str | None:
    """
    Waits for the user to type the received SMS OTP code.
      'r'      -> resend the OTP (up to max_resends times)
      'Enter'  -> abort
    Returns the digits, or None on abort.
    """
    while True:
        try:
            raw = input("[?] Enter the OTP code you received by SMS "
                        "('r' = resend, Enter = abort): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if raw == "":
            return None
        if raw.lower() == "r":
            return "RESEND"
        code = "".join(c for c in raw if c.isdigit())
        if 3 <= len(code) <= 10:
            return code
        LOG.warning("[!] '%s' doesn't look like an OTP code (3-10 digits). Try again "
                    "or press Enter to abort.", raw)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    p = argparse.ArgumentParser(
        description="My Ooredoo 1.5.17 — FULL OTP login: send the SMS OTP, wait for "
                    "the code, verify it, and report LOGGED IN / LOGIN FAILED.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("msisdn", nargs="?", help="MSISDN to log in with. Local (0549908213), "
                   "international (213549908213) or +213 forms accepted; normalized "
                   "automatically. Prompted if omitted.")
    p.add_argument("--otp", help="non-interactive: the SMS OTP code to verify "
                   "(skips the interactive wait; send-step still runs first)")
    p.add_argument("--resend", action="store_true",
                   help="mark the initial OTP request as a re-send (resend=true)")
    p.add_argument("--password-param", action="store_true",
                   help="verify with password=<CODE> instead of the AOT-confirmed "
                        "otp=<CODE> form param (also auto-falls-back on 40x)")
    p.add_argument("--no-fallback", action="store_true",
                   help="disable the automatic password-param retry after an "
                        "otp-param rejection")
    p.add_argument("--base-url", default=BASE_URL, help="API base URL (lab/mock override)")
    p.add_argument("--proxy", help="HTTP(S) proxy, e.g. http://127.0.0.1:8080 (Burp)")
    p.add_argument("--extra-header", action="append", metavar="K:V",
                   help="additional header, repeatable — overrides synthesized ones "
                        "(x-signature, X-JWS, X-Native-Integrity-Token, ...)")
    p.add_argument("--no-nonce", action="store_true", help="skip checkpoint pre-flights")
    p.add_argument("--timeout", type=float, default=15.0, help="per-request timeout (s)")
    p.add_argument("--insecure", action="store_true", help="do not verify TLS (Burp)")
    p.add_argument("--state-file", default=".ooredoo_device_state.json",
                   help="pseudo-device state (uuid + android-id) persistence")
    p.add_argument("--x-sig-raw", action="store_true",
                   help="use the no-newline x-signature variant instead of the "
                        "Android-Base64(flag 0) one")
    p.add_argument("--fingerprint-msisdn", default="",
                   help="stored Settings-MSISDN used inside X-Device-Fingerprint "
                        "(app uses '' before first login)")
    p.add_argument("--logfile", help="custom log file path")
    p.add_argument("-v", "--verbose", action="store_true", help="debug output on console")
    args = p.parse_args()

    global X_SIGNATURE
    if args.x_sig_raw:
        X_SIGNATURE = X_SIGNATURE_RAW

    msisdn = (args.msisdn or "").strip()
    if not msisdn:
        try:
            msisdn = input("[?] Enter phone number (MSISDN): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
    if not msisdn:
        print("[!] no MSISDN provided — aborting.")
        return
    try:
        norm = normalize_msisdn(msisdn)
    except ValueError as exc:
        print(f"[!] {exc} — aborting.")
        return

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    setup_logging(args.logfile or f"ooredoo_login_{norm}_{stamp}.log", args.verbose)
    banner()
    LOG.info("Input MSISDN : %s  ->  normalized: %s", msisdn, norm)
    LOG.info("Base URL     : %s", args.base_url)
    LOG.info("x-signature  : %s%s", X_SIGNATURE[:16] + "…", " (raw variant)" if args.x_sig_raw else "")
    if args.proxy:
        LOG.info("Proxy        : %s", args.proxy)
    if args.insecure:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        LOG.warning("TLS verification DISABLED (interception mode)")

    device = load_or_create_device(args.state_file)
    LOG.info("Pseudo-device: instance-id=%s  device-id=%s  (state: %s)",
             device["uuid"], device["device_id"], os.path.abspath(args.state_file))

    extra = parse_extra_headers(args.extra_header)
    if extra:
        LOG.info("Extra headers: %s", extra)

    session = requests.Session()
    session.proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else None
    session.verify = not args.insecure

    # -------------------------------------------------------------------------
    # STEP 1 + 2 — anti-replay nonce, then OTP dispatch
    # -------------------------------------------------------------------------
    def send_otp(resend: bool) -> requests.Response:
        if args.no_nonce:
            LOG.info("[STEP 1] skipped by --no-nonce (empty nonce ids)")
            nonce_id, chronos_id = "", ""
        else:
            try:
                nonce_id, chronos_id = get_nonce(session, args.base_url, norm,
                                                 extra, device, args.timeout)
            except SystemExit:
                raise
            except Exception as exc:
                LOG.warning("[!] checkpoint pre-flight failed (%s) — continuing with empty nonce", exc)
                nonce_id, chronos_id = "", ""
        return request_otp(session, args.base_url, norm, nonce_id, chronos_id,
                           resend, extra, device, args.timeout)

    resp_otp = send_otp(args.resend)

    LOG.info("=" * 76)
    if 200 <= resp_otp.status_code < 300:
        LOG.info("[+] OTP SENT — HTTP %s. Waiting for you to type the code.", resp_otp.status_code)
    elif resp_otp.status_code in (401, 403):
        # Field-verified on 2026-10-29 against production: HTTP 403/empty-body is
        # still followed by the SMS being dispatched to the MSISDN.
        LOG.warning("[*] OTP dispatch answered HTTP %s/empty — BUT this exact signal "
                   "has been FIELD-VERIFIED to still send the SMS. Check your phone; "
                   "type 'r' to resend if nothing arrives.", resp_otp.status_code)
    elif resp_otp.status_code == 429:
        LOG.warning("[*] HTTP 429 — rate-limited. You can still type a code from a "
                   "previous SMS, or wait and press 'r' to resend.")
    else:
        LOG.warning("[*] OTP dispatch answered HTTP %s. You may still type a code if "
                    "an SMS arrives.", resp_otp.status_code)

    # -------------------------------------------------------------------------
    # WAIT — user types the received OTP
    # -------------------------------------------------------------------------
    resends_left = 5
    if args.otp:
        otp_code = "".join(c for c in args.otp if c.isdigit())
        if not (3 <= len(otp_code) <= 10):
            LOG.error("[!] --otp must be 3-10 digits — aborting.")
            return
        LOG.info("[i] non-interactive mode: using provided OTP code.")
    else:
        otp_code = prompt_otp()
        while otp_code == "RESEND":
            if resends_left <= 0:
                LOG.error("[!] resend limit reached — type the code you have or abort.")
            else:
                resends_left -= 1
                send_otp(resend=True)
            otp_code = prompt_otp()
        if otp_code is None:
            LOG.info("[!] aborted by user before OTP entry.")
            LOG.info("=" * 76)
            return

    LOG.info("[+] OTP code accepted from input: %s", otp_code)

    # -------------------------------------------------------------------------
    # STEP 3 — FRESH nonce (loginWithOTP re-runs getNonceValidation @ 0xe3e900)
    # -------------------------------------------------------------------------
    if args.no_nonce:
        LOG.info("[STEP 3] skipped by --no-nonce (empty nonce ids)")
        nonce_id, chronos_id = "", ""
    else:
        try:
            LOG.info("[STEP 3] fresh checkpoint nonce for the verification grant")
            nonce_id, chronos_id = get_nonce(session, args.base_url, norm,
                                             extra, device, args.timeout)
        except SystemExit:
            raise
        except Exception as exc:
            LOG.warning("[!] checkpoint pre-flight failed (%s) — continuing with empty nonce", exc)
            nonce_id, chronos_id = "", ""

    # -------------------------------------------------------------------------
    # STEP 4 — verify the OTP (loginWithOTP), with optional password-param fallback
    # -------------------------------------------------------------------------
    resp_login = login_with_otp(session, args.base_url, norm, otp_code,
                               nonce_id, chronos_id, extra, device,
                               args.timeout, password_param=args.password_param)

    tokens = verdict_login(resp_login, password_param_used=args.password_param)

    if tokens is None and not args.password_param and not args.no_fallback \
            and 400 <= resp_login.status_code < 500 and resp_login.status_code != 429:
        LOG.info("[i] auto-fallback: retrying the verification grant once with "
                 "password=<CODE> instead of otp=<CODE> …")
        try:
            nonce_id, chronos_id = ("", "") if args.no_nonce else get_nonce(
                session, args.base_url, norm, extra, device, args.timeout)
        except Exception as exc:
            LOG.warning("[!] fallback nonce pre-flight failed (%s)", exc)
            nonce_id, chronos_id = "", ""
        resp_fb = login_with_otp(session, args.base_url, norm, otp_code,
                                nonce_id, chronos_id, extra, device,
                                args.timeout, password_param=True)
        tokens = verdict_login(resp_fb, password_param_used=True)

    # -------------------------------------------------------------------------
    # persistence + exit code
    # -------------------------------------------------------------------------
    if tokens is not None:
        save_tokens(f"ooredoo_tokens_{norm}_{stamp}.json", norm, tokens)
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] interrupted")
        sys.exit(130)
