#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
 My Ooredoo (Algeria) v1.5.17 — OTP LOGIN + SESSION CLIENT  [v4 — session]
===============================================================================
 Target app   : My Ooredoo — com.algeria.selfcare.app.android v1.5.17 (1461)
 Source       : static reverse-engineering of 'My Ooredoo_1.5.17.apks'
                (jadx + Blutter Dart-AOT reversal + APK signing-block parse)

 Reconstructed functions (Dart AOT, libapp.so):
   ApiCalls::requestOTPbyMSISDN   @ 0xb905b8  -> SMS OTP dispatch
   ApiCalls::loginWithOTP         @ 0xe3e88c  -> OTP verification grant (otp=)
   ApiCalls::getAccessTokenByOtp  @ 0xe3d204  -> (twin of loginWithOTP)
   ApiCalls::getNonceValidation   @ 0x95c71c  -> checkpoint anti-replay nonce
   ApiCalls::refreshAccessToken   @ 0xb70330  -> grant_type=refresh_token
   ApiCalls::logout               @ 0xc3bb00  -> openid-connect/logout
   ApiCalls::_getCommonHeaders    @ 0x92a350  -> authenticated-call header suite
   ApiCaller::* (Bearer header)   @ 0x95a070  -> Authorization: Bearer <token>
   ApiCalls::setChecksumHeaders   @ 0x92ab94  -> x-signature
   ApiCalls::setDeviceDataGatherForKeycloak @ 0x95c568 -> X-Platform-Info
   ApiCalls::setDeviceFingerprintHeader     @ 0x92a480 -> X-Device-Fingerprint
   OnboardingMobileMainCubit (validateUser) @ 0xe3b0fc-0xe3b134:
       resetMsisdn -> validateUser -> Settings::setMSISDN  <- KEY: the MSISDN
       is persisted BEFORE the OTP-verify screen, so the verify grant's
       X-Device-Fingerprint = HMAC-SHA256(ts, msisdn+uuid+ts) — v3 computed it
       with '' and got 401 "Invalid User Credentials"; v4 fixes this (FP-MODE).

 SESSION PRESERVATION (v4 headline feature):
   * after LOGGED IN SUCCESSFULLY the process enters an interactive SESSION
     SHELL: the tokens live in memory for the whole session and every command
     (status/ping/call/refresh/resend/relog/logout) runs with the app's full
     authenticated header suite (Authorization: Bearer …);
   * the session is ALSO persisted to the state file (mirroring the app's
     Settings storage of access/refresh tokens): rerun the script and it
     resumes the session without a new OTP (or silently refreshes the access
     token via grant_type=refresh_token if it expired);
   * `logout` posts the Keycloak logout endpoint (client_id+refresh_token)
     and clears the persisted session.

 FLOW:
   STEP 1  POST /api/ooredoo-bff/checkpoint/token            <- anti-replay
   STEP 2  POST .../openid-connect/token  (username grant)    <- SMS dispatch
           NOTE (field-observed): dispatch may answer 401/403-empty while the
           SMS is STILL dispatched — treated as "submitted".
   [WAIT]  user types the received code ('r'=resend). Retry loop on failure —
           always use the code from the LATEST SMS.
   STEP 3  fresh checkpoint nonce (loginWithOTP re-runs getNonceValidation)
   STEP 4  POST .../openid-connect/token  (username + otp=<CODE>) <- login
           success = 2xx + access_token (cubit closure @ 0xe3d730)
   SESSION  interactive shell + persisted tokens + refresh/resume/logout.

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
BASE_URL = "https://apis.ooredoo.dz"
EP_NONCE = "/api/ooredoo-bff/checkpoint/token"
EP_TOKEN = "/api/auth/realms/myooredoo/protocol/openid-connect/token"
EP_LOGOUT = "/api/auth/realms/myooredoo/protocol/openid-connect/logout"
EP_AUTHPING = "/api/ooredoo-bff/users/authping"
CLIENT_ID = "myooredoo-app"
APP_VERSION = "1.5.17"
USER_AGENT = "Dart/3.11 (dart:io)"
COUNTRY_CODE = "213"

# --- x-signature: computed from the GENUINE My Ooredoo 1.5.17 base.apk ------
APK_CHECKSUM = "3138619328"                               # CRC32(classes.dex)
APK_SIGNATURE = "KLYDvjaYq0SFAMqFTaEzMX0kQVR402qzUftEhMp6jyU="
X_SIGNATURE = hashlib.sha256(
    (APK_CHECKSUM + APK_SIGNATURE + "\n").encode()
).hexdigest()  # Android Base64 flag-0 appends a trailing newline before hashing
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
    digits = "".join(c for c in raw if c.isdigit())
    if not digits:
        raise ValueError("no digits in MSISDN")
    if digits.startswith("00213"):
        digits = digits[2:]
    if digits.startswith(COUNTRY_CODE) and len(digits) >= 12:
        return digits
    if digits.startswith("0"):
        digits = digits[1:]
    if len(digits) == 9:
        digits = COUNTRY_CODE + digits
    elif not digits.startswith(COUNTRY_CODE):
        digits = COUNTRY_CODE + digits.lstrip("0")
    return digits


# ---------------------------------------------------------------------------
# Persistent state: pseudo-device + saved session (mirrors app Settings)
# ---------------------------------------------------------------------------
def load_state(state_file: str) -> dict:
    if os.path.exists(state_file):
        try:
            with open(state_file, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict) and "uuid" in data:
                data.setdefault("session", None)
                return data
        except Exception:
            pass
    return {"uuid": str(uuid.uuid4()), "device_id": secrets.token_hex(8),
            "session": None}                                # Settings::getUUID etc.


def save_state(state_file: str, state: dict) -> None:
    try:
        with open(state_file, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2)
    except Exception as exc:
        LOG.warning("[!] could not persist state (%s)", exc)


def session_from_tokens(msisdn: str, tokens: dict) -> dict:
    return {
        "msisdn": msisdn,
        "access_token": tokens.get("access_token", ""),
        "refresh_token": tokens.get("refresh_token", ""),
        "expires_at": jwt_exp(tokens.get("access_token")) or (
            time.time() + float(tokens.get("expires_in") or 300)),
        "refresh_expires_at": jwt_exp(tokens.get("refresh_token")) or (
            time.time() + float(tokens.get("refresh_expires_in") or 1800)),
        "captured_at": datetime.now().isoformat(timespec="seconds"),
        "scope": tokens.get("scope", ""),
    }


# ---------------------------------------------------------------------------
# JWT helpers (no external deps)
# ---------------------------------------------------------------------------
def decode_jwt_payload(token: str) -> dict | None:
    try:
        seg = token.split(".")[1]
        seg += "=" * (-len(seg) % 4)
        return json.loads(base64.urlsafe_b64decode(seg).decode("utf-8", "replace"))
    except Exception:
        return None


def jwt_exp(token: str) -> float | None:
    if not token:
        return None
    payload = decode_jwt_payload(token)
    exp = (payload or {}).get("exp")
    return float(exp) if isinstance(exp, (int, float)) else None


def token_seconds_left(token: str, fallback_exp: float | None = None) -> float | None:
    exp = jwt_exp(token)
    if exp is None:
        exp = fallback_exp
    return None if exp is None else exp - time.time()


# ---------------------------------------------------------------------------
# Logging helpers — pentest-grade, full-wire documentation
# ---------------------------------------------------------------------------
def setup_logging(logfile: str | None, verbose: bool) -> None:
    LOG.setLevel(logging.DEBUG)
    LOG.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", "%H:%M:%S")
    con = logging.StreamHandler(sys.stdout)
    con.setLevel(logging.DEBUG if verbose else logging.INFO)
    con.setFormatter(fmt)
    LOG.addHandler(con)
    if logfile:
        fh = logging.FileHandler(logfile, mode="w", encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
        LOG.addHandler(fh)
        LOG.info("Log file: %s", os.path.abspath(logfile))


def banner() -> None:
    LOG.info("=" * 76)
    LOG.info("My Ooredoo 1.5.17 — OTP LOGIN + SESSION CLIENT (send/verify/keep)")
    LOG.info("Reconstructed: requestOTPbyMSISDN @ 0xb905b8, loginWithOTP @ 0xe3e88c  [v4]")
    LOG.info("=" * 76)


def log_request(prep: requests.PreparedRequest) -> None:
    LOG.info("-" * 76)
    LOG.info(">> REQUEST  %s %s", prep.method, prep.url)
    for k, v in (prep.headers or {}).items():
        shown = v
        if k.lower() == "authorization" and len(v) > 60:
            shown = v[:44] + "…(redacted in log)"
        LOG.info(">> H  %s: %s", k, shown)
    body = prep.body or ""
    if isinstance(body, bytes):
        try:
            body = body.decode("utf-8", "replace")
        except Exception:
            body = repr(body)
    if body:
        LOG.info(">> BODY  %s", body)


def log_response(resp: requests.Response) -> None:
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
#
# FP-MODE (X-Device-Fingerprint stored-msisdn binding — see v4 header notes):
#   auto   : "" for the dispatch pair (field-verified working), MSISDN for
#            the verify grant and all authenticated session traffic (app has
#            Settings::setMSISDN persisted by then — OnboardingMobileMainCubit
#            @ 0xe3b134)
#   empty  : always "" (v3 behavior)
#   msisdn : always the MSISDN
# ---------------------------------------------------------------------------
def device_headers(device: dict, fp_msisdn: str) -> dict[str, str]:
    ts = str(int(time.time() * 1000))
    msg = (fp_msisdn + device["uuid"] + ts).encode()
    key = ts.encode()
    return {
        "x-signature": X_SIGNATURE,
        "X-Platform-Info": json.dumps(
            {"platform": "android", "is-physical-device": True,
             "device-id": device["device_id"]},
            separators=(",", ":"), sort_keys=False),
        "X-Timestamp": ts,
        "X-Instance-Id": device["uuid"],
        "X-Device-Fingerprint": hmac_mod.new(key, msg, hashlib.sha256).hexdigest(),
    }


def fp_for(state: dict, fp_mode: str, phase: str) -> str:
    """phase: 'dispatch' | 'verify' | 'session'"""
    if fp_mode == "empty":
        return ""
    if fp_mode == "msisdn":
        return state.get("session", {}).get("msisdn", "") or state.get("_login_msisdn", "")
    # auto
    if phase == "dispatch":
        return ""
    return (state.get("session", {}) or {}).get("msisdn", "") or state.get("_login_msisdn", "")


# ---------------------------------------------------------------------------
# STEP 1 — checkpoint nonce (ApiCalls::getNonceValidation)
# ---------------------------------------------------------------------------
def get_nonce(session: requests.Session, base: str, msisdn: str,
              extra: dict[str, str], device: dict, timeout: float,
              fp_msisdn: str) -> tuple[str, str]:
    url = base + EP_NONCE
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
        "x-msisdn": msisdn,
        "x-path": EP_TOKEN,
        "x-method": "POST",
        "X-Correlation-ID": str(uuid.uuid1()),
        **APP_HEADERS,
        **device_headers(device, fp_msisdn),
        **extra,
    }
    prep = session.prepare_request(requests.Request("POST", url, headers=headers, data={}))
    LOG.info("[NONCE] checkpoint — anti-replay pre-flight")
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
                extra: dict[str, str], device: dict, timeout: float,
                fp_msisdn: str) -> requests.Response:
    url = base + EP_TOKEN
    form = {
        "client_id": CLIENT_ID,
        "grant_type": "password",
        "username": msisdn,
    }
    if resend:
        form["resend"] = "true"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "User-Agent": USER_AGENT,
        "x-msisdn": msisdn,
        "x-nonce-id": nonce_id,
        "x-chronos-id": chronos_id,
        "X-Correlation-ID": str(uuid.uuid1()),
        **APP_HEADERS,
        **device_headers(device, fp_msisdn),
        **extra,
    }
    prep = session.prepare_request(requests.Request("POST", url, headers=headers, data=form))
    LOG.info("[STEP 2] OTP request — requestOTPbyMSISDN%s", " (resend)" if resend else "")
    return do_request(session, prep, timeout)


# ---------------------------------------------------------------------------
# STEP 4 — OTP verification / login (ApiCalls::loginWithOTP @ 0xe3e88c)
# ---------------------------------------------------------------------------
def login_with_otp(session: requests.Session, base: str, msisdn: str, otp: str,
                   nonce_id: str, chronos_id: str, extra: dict[str, str],
                   device: dict, timeout: float, fp_msisdn: str,
                   password_param: bool) -> requests.Response:
    url = base + EP_TOKEN
    form = {
        "client_id": CLIENT_ID,
        "grant_type": "password",
        "username": msisdn,
        ("password" if password_param else "otp"): otp,   # @ 0xe3eb24 ("otp")
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
        **device_headers(device, fp_msisdn),
        **extra,
    }
    prep = session.prepare_request(requests.Request("POST", url, headers=headers, data=form))
    LOG.info("[STEP 4] OTP verification — loginWithOTP (param '%s')",
             "password" if password_param else "otp")
    return do_request(session, prep, timeout)


# ---------------------------------------------------------------------------
# Refresh grant (ApiCalls::refreshAccessToken @ 0xb70330)
# ---------------------------------------------------------------------------
def refresh_grant(session: requests.Session, base: str, msisdn: str,
                  refresh_token: str, nonce_id: str, chronos_id: str,
                  extra: dict[str, str], device: dict, timeout: float,
                  fp_msisdn: str) -> requests.Response:
    url = base + EP_TOKEN
    form = {
        "client_id": CLIENT_ID,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
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
        **device_headers(device, fp_msisdn),
        **extra,
    }
    prep = session.prepare_request(requests.Request("POST", url, headers=headers, data=form))
    LOG.info("[REFRESH] grant_type=refresh_token (ApiCalls::refreshAccessToken @ 0xb70330)")
    return do_request(session, prep, timeout)


# ---------------------------------------------------------------------------
# Keycloak logout (ApiCalls::logout @ 0xc3bb00 — _getCommonHeaders, no nonce)
# ---------------------------------------------------------------------------
def keycloak_logout(session: requests.Session, base: str, msisdn: str,
                    refresh_token: str, access_token: str,
                    extra: dict[str, str], device: dict, timeout: float,
                    fp_msisdn: str) -> requests.Response:
    url = base + EP_LOGOUT
    form = {
        "client_id": CLIENT_ID,
        "refresh_token": refresh_token,
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "User-Agent": USER_AGENT,
        "Authorization": f"Bearer {access_token}",
        "x-msisdn": msisdn,
        "X-Correlation-ID": str(uuid.uuid1()),
        **APP_HEADERS,
        **device_headers(device, fp_msisdn),
        **extra,
    }
    prep = session.prepare_request(requests.Request("POST", url, headers=headers, data=form))
    LOG.info("[LOGOUT] openid-connect/logout (ApiCalls::logout @ 0xc3bb00)")
    return do_request(session, prep, timeout)


# ---------------------------------------------------------------------------
# Authenticated call (ApiCaller Authorization: Bearer + _getCommonHeaders)
# ---------------------------------------------------------------------------
def authed_call(session: requests.Session, base: str, msisdn: str, access_token: str,
                method: str, path: str, body: dict | None,
                extra: dict[str, str], device: dict, timeout: float,
                fp_msisdn: str) -> requests.Response:
    if not path.startswith("/"):
        path = "/" + path
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "x-msisdn": msisdn,
        "X-Correlation-ID": str(uuid.uuid1()),
        **APP_HEADERS,
        **device_headers(device, fp_msisdn),
        **extra,
    }
    data = None
    if body is not None or method.upper() in ("POST", "PUT", "PATCH"):
        headers["Content-Type"] = "application/json"
        data = json.dumps(body if body is not None else {})
    prep = session.prepare_request(
        requests.Request(method.upper(), base + path, headers=headers, data=data))
    LOG.info("[CALL] authenticated %s %s", method.upper(), path)
    return do_request(session, prep, timeout)


# ---------------------------------------------------------------------------
# Verdict + token persistence
# ---------------------------------------------------------------------------
def tokens_from_response(resp: requests.Response) -> dict | None:
    """App criterion (cubit closure @ 0xe3d730): 2xx AND access_token is String."""
    try:
        body = resp.json()
    except ValueError:
        body = {}
    access = body.get("access_token")
    if 200 <= resp.status_code < 300 and isinstance(access, str) and access:
        return body
    return None


def announce_success(tokens: dict, password_param_used: bool) -> None:
    LOG.info("=" * 76)
    LOG.info("[+] ==============================")
    LOG.info("[+]     LOGGED IN SUCCESSFULLY    ")
    LOG.info("[+] ==============================")
    LOG.info("[i] verdict basis : 2xx + access_token (OnboardingMobileMainCubit @ 0xe3d730)")
    if password_param_used:
        LOG.warning("[i] NOTE: success came via the fallback 'password' param.")
    LOG.info("[+] token_type    : %s", tokens.get("token_type", "(absent)"))
    LOG.info("[+] expires_in    : %s s", tokens.get("expires_in", "(absent)"))
    LOG.info("[+] scope         : %s", tokens.get("scope", "(absent)"))
    at = tokens.get("access_token", "")
    LOG.info("[+] access_token  : %s", at[:38] + "…")
    rt = tokens.get("refresh_token", "")
    LOG.info("[+] refresh_token : %s", rt[:38] + "…")
    payload = decode_jwt_payload(at)
    if payload:
        LOG.info("[+] access_token JWT payload (decoded):")
        LOG.info("%s", json.dumps(payload, indent=2, ensure_ascii=False))
        exp = payload.get("exp")
        if isinstance(exp, (int, float)):
            remain = int(exp - time.time())
            LOG.info("[+] session validity: expires in %d min %d s", remain // 60, remain % 60)
    LOG.info("=" * 76)


def announce_failure(resp: requests.Response) -> None:
    LOG.error("[!] LOGIN FAILED — HTTP %s (%s).",
              resp.status_code,
              {401: "Keycloak: invalid credentials / wrong OTP",
               403: "empty-body rejection signal",
               400: "malformed grant"}.get(resp.status_code,
                                          "server error" if resp.status_code >= 500 else "rejected"))


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
# Interactive OTP input with resend support
# ---------------------------------------------------------------------------
def prompt_otp() -> str | None:
    while True:
        try:
            raw = input("[?] Enter the OTP code from the LATEST SMS "
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
        LOG.warning("[!] '%s' doesn't look like an OTP code (3-10 digits). Try again.", raw)


# ---------------------------------------------------------------------------
# The login flow (dispatch -> wait -> verify-retry-loop) -> tokens or None
# ---------------------------------------------------------------------------
def run_login_flow(args, state: dict, extra: dict[str, str],
                   session: requests.Session) -> dict | None:
    norm = state.get("_login_msisdn", "")

    # --- STEP 1 + 2: nonce then OTP dispatch -----------------------------
    # (dispatch-phase fingerprint is "" in auto mode — field-verified working)
    def dispatch(resend: bool) -> None:
        if args.no_nonce:
            nonce_id, chronos_id = "", ""
        else:
            try:
                nonce_id, chronos_id = get_nonce(
                    session, args.base_url, norm, extra, state, args.timeout,
                    fp_for(state, args.fp_mode, "dispatch"))
            except SystemExit:
                raise
            except Exception as exc:
                LOG.warning("[!] checkpoint pre-flight failed (%s) — continuing", exc)
                nonce_id, chronos_id = "", ""
        request_otp(session, args.base_url, norm, nonce_id, chronos_id,
                    resend, extra, state, args.timeout,
                    fp_for(state, args.fp_mode, "dispatch"))

    dispatch(False)
    resends_left = 5

    # --- WAIT: interactive code entry --------------------------------------
    if args.otp:
        otp_code = "".join(c for c in args.otp if c.isdigit())
        if not (3 <= len(otp_code) <= 10):
            LOG.error("[!] --otp must be 3-10 digits — aborting.")
            return None
    else:
        otp_code = prompt_otp()
        while otp_code == "RESEND":
            if resends_left > 0:
                resends_left -= 1
                dispatch(True)
            else:
                LOG.error("[!] resend limit reached — type the code you have or abort.")
            otp_code = prompt_otp()
        if otp_code is None:
            LOG.info("[!] aborted by user before OTP entry.")
            return None

    # --- STEP 3 + 4: verify with retry loop --------------------------------
    attempts = 0
    while True:
        attempts += 1
        if args.no_nonce:
            nonce_id, chronos_id = "", ""
        else:
            LOG.info("[STEP 3] fresh checkpoint nonce for the verification grant")
            nonce_id, chronos_id = fresh_nonce_or_empty(session, args, state, extra)
        resp_login = login_with_otp(
            session, args.base_url, norm, otp_code, nonce_id, chronos_id,
            extra, state, args.timeout,
            fp_for(state, args.fp_mode, "verify"), args.password_param)
        tokens = tokens_from_response(resp_login)
        if tokens:
            announce_success(tokens, args.password_param)
            state["session"] = session_from_tokens(norm, tokens)
            save_tokens(f"ooredoo_tokens_{norm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                       norm, tokens)
            return tokens
        announce_failure(resp_login)
        if args.otp:  # non-interactive: no retry loop
            return None
        otp_code = prompt_otp()
        while otp_code == "RESEND":
            if resends_left > 0:
                resends_left -= 1
                dispatch(True)
            else:
                LOG.error("[!] resend limit reached — type the code you have or abort.")
            otp_code = prompt_otp()
        if otp_code is None:
            LOG.info("[!] no successful login — session not established.")
            return None


def fresh_nonce_or_empty(session, args, state, extra):
    try:
        return get_nonce(session, args.base_url,
                         state.get("_login_msisdn", ""), extra, state,
                         args.timeout, fp_for(state, args.fp_mode, "verify"))
    except SystemExit:
        raise
    except Exception as exc:
        LOG.warning("[!] checkpoint pre-flight failed (%s) — continuing with empty nonce", exc)
        return "", ""


# ---------------------------------------------------------------------------
# Session shell — preserves the logged-in state for the whole session
# ---------------------------------------------------------------------------
SHELL_HELP = """
  status                       msisdn, token expiry, device ids
  ping                         POST /api/ooredoo-bff/users/authping (session proof)
  call METHOD PATH [JSON]      authenticated call, e.g.
                                 call POST /api/ooredoo-bff/users/detect {"msisdn":"213..."}
  get PATH                     shorthand for call GET PATH
  post PATH [JSON]             shorthand for call POST PATH [JSON]
  refresh                      grant_type=refresh_token — rotate the tokens
  resend                       dispatch a NEW SMS OTP (login again afterwards)
  relog                        full OTP login flow (replaces current session)
  logout                       Keycloak logout + clear persisted session
  tokens                       print current tokens (full)
  help                         this text
  exit                         persist session and quit
""".strip()


def ensure_live_token(session, args, state, extra) -> bool:
    """Auto-refresh if the access token expired. Returns True if usable."""
    sess = state.get("session") or {}
    at, rt = sess.get("access_token", ""), sess.get("refresh_token", "")
    left = token_seconds_left(at, sess.get("expires_at"))
    if at and (left is None or left > 5):
        return True
    if not rt:
        return False
    LOG.warning("[i] access token expired — auto-refreshing via grant_type=refresh_token …")
    nonce_id, chronos_id = ("", "") if args.no_nonce else fresh_nonce_or_empty(
        session, args, state, extra)
    resp = refresh_grant(session, args.base_url, sess["msisdn"], rt,
                         nonce_id, chronos_id, extra, state, args.timeout,
                         fp_for(state, args.fp_mode, "session"))
    tokens = tokens_from_response(resp)
    if not tokens:
        LOG.error("[!] refresh failed (HTTP %s) — session expired; use 'relog'.", resp.status_code)
        return False
    state["session"] = session_from_tokens(sess["msisdn"], tokens)
    save_state(args.state_file, state)
    LOG.info("[+] tokens refreshed — new access_token: %s…", tokens["access_token"][:38])
    return True


def session_shell(args, state: dict, extra: dict[str, str],
                  session: requests.Session) -> None:
    sess = state.get("session") or {}
    msisdn = sess.get("msisdn", "?")
    LOG.info("=" * 76)
    LOG.info("[i] SESSION ACTIVE — logged in as %s", msisdn)
    LOG.info("[i] state file   : %s (tokens persisted — rerun to resume)", os.path.abspath(args.state_file))
    LOG.info("[i] type 'help' for session commands, 'exit' to quit")
    LOG.info("=" * 76)
    while True:
        try:
            line = input(f"[ooredoo:{msisdn}] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            line = "exit"
        if not line:
            continue
        parts = line.split()
        cmd = parts[0].lower()
        try:
            if cmd in ("exit", "quit"):
                save_state(args.state_file, state)
                LOG.info("[i] session preserved in %s — bye.", os.path.abspath(args.state_file))
                return
            elif cmd == "help":
                print(SHELL_HELP)
            elif cmd == "status":
                sess = state.get("session") or {}
                at = sess.get("access_token", "")
                left = token_seconds_left(at, sess.get("expires_at"))
                rt_left = token_seconds_left(sess.get("refresh_token", ""),
                                             sess.get("refresh_expires_at"))
                LOG.info("msisdn           : %s", sess.get("msisdn"))
                LOG.info("logged in since  : %s", sess.get("captured_at"))
                LOG.info("access_token     : %s (%s)", at[:38] + "…",
                         f"{int(left)}s left" if left is not None else "no exp claim")
                LOG.info("refresh_token    : %s (%s)", (sess.get("refresh_token", "") or "")[:38] + "…",
                         f"{int(rt_left)}s left" if rt_left is not None else "-")
                LOG.info("instance-id      : %s", state["uuid"])
                LOG.info("device-id        : %s", state["device_id"])
            elif cmd == "tokens":
                print(json.dumps(state.get("session") or {}, indent=2))
            elif cmd == "ping":
                if ensure_live_token(session, args, state, extra):
                    authed_call(session, args.base_url, msisdn,
                                state["session"]["access_token"],
                                "POST", EP_AUTHPING, {}, extra, state, args.timeout,
                                fp_for(state, args.fp_mode, "session"))
            elif cmd == "get" and len(parts) >= 2:
                if ensure_live_token(session, args, state, extra):
                    authed_call(session, args.base_url, msisdn,
                                state["session"]["access_token"],
                                "GET", parts[1], None, extra, state, args.timeout,
                                fp_for(state, args.fp_mode, "session"))
            elif cmd == "post" and len(parts) >= 2:
                body = json.loads(" ".join(parts[2:])) if len(parts) > 2 else {}
                if ensure_live_token(session, args, state, extra):
                    authed_call(session, args.base_url, msisdn,
                                state["session"]["access_token"],
                                "POST", parts[1], body, extra, state, args.timeout,
                                fp_for(state, args.fp_mode, "session"))
            elif cmd == "call" and len(parts) >= 3:
                body = json.loads(" ".join(parts[3:])) if len(parts) > 3 else None
                if ensure_live_token(session, args, state, extra):
                    authed_call(session, args.base_url, msisdn,
                                state["session"]["access_token"],
                                parts[1], parts[2], body, extra, state, args.timeout,
                                fp_for(state, args.fp_mode, "session"))
            elif cmd == "refresh":
                state["session"] = state.get("session") or {}
                if not ensure_live_token(session, args, state, extra):
                    LOG.warning("[i] tip: 'relog' to start a fresh OTP login.")
                else:
                    LOG.info("[i] tokens are live (auto-refresh already applied if needed).")
            elif cmd == "resend":
                state["_login_msisdn"] = (state.get("session") or {}).get("msisdn", msisdn)
                nonce_id, chronos_id = ("", "") if args.no_nonce else fresh_nonce_or_empty(
                    session, args, state, extra)
                request_otp(session, args.base_url, state["_login_msisdn"],
                            nonce_id, chronos_id, True, extra, state, args.timeout,
                            fp_for(state, args.fp_mode, "dispatch"))
                LOG.warning("[*] new OTP dispatched — use 'relog' and type the fresh code.")
            elif cmd == "relog":
                state["_login_msisdn"] = input("[?] phone number (Enter = same): ").strip() \
                    or (state.get("session") or {}).get("msisdn", "")
                state["_login_msisdn"] = normalize_msisdn(state["_login_msisdn"])
                tokens = run_login_flow(args, state, extra, session)
                if tokens:
                    save_state(args.state_file, state)
                    sess = state.get("session") or {}
                    msisdn = sess.get("msisdn", msisdn)
            elif cmd == "logout":
                sess = state.get("session") or {}
                keycloak_logout(session, args.base_url, msisdn,
                                sess.get("refresh_token", ""), sess.get("access_token", ""),
                                extra, state, args.timeout,
                                fp_for(state, args.fp_mode, "session"))
                state["session"] = None
                save_state(args.state_file, state)
                LOG.info("[i] session cleared (local + Keycloak notified). 'relog' to log in again, 'exit' to quit.")
            else:
                print(f"[?] unknown command '{cmd}' — try 'help'")
        except SystemExit:
            raise
        except Exception as exc:
            LOG.error("[!] command failed: %s", exc)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    p = argparse.ArgumentParser(
        description="My Ooredoo 1.5.17 — OTP login + SESSION client: send SMS OTP, "
                    "wait for the code, verify, then KEEP the logged-in state "
                    "(interactive authenticated session + persisted tokens + resume).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("msisdn", nargs="?", help="MSISDN to log in with. Local/international "
                   "forms accepted. Prompted if omitted and no saved session exists.")
    p.add_argument("--otp", help="non-interactive: the SMS OTP code to verify "
                   "(no retry loop, no session shell on success)")
    p.add_argument("--resend", action="store_true",
                   help="mark the initial OTP request as a re-send (resend=true)")
    p.add_argument("--password-param", action="store_true",
                   help="verify with password=<CODE> instead of the AOT-confirmed otp=<CODE>")
    p.add_argument("--fp-mode", choices=["auto", "empty", "msisdn"], default="auto",
                   help="X-Device-Fingerprint stored-msisdn binding: auto = '' on dispatch "
                        "(field-verified) + MSISDN on verify/session (app behavior — v3's "
                        "401 fix); empty = v3 legacy; msisdn = everywhere")
    p.add_argument("--fresh", action="store_true",
                   help="ignore any saved session and perform a new OTP login")
    p.add_argument("--logout", action="store_true",
                   help="one-shot: log out the saved session (Keycloak + clear state) and exit")
    p.add_argument("--base-url", default=BASE_URL, help="API base URL (lab/mock override)")
    p.add_argument("--proxy", help="HTTP(S) proxy, e.g. http://127.0.0.1:8080 (Burp)")
    p.add_argument("--extra-header", action="append", metavar="K:V",
                   help="additional header, repeatable — overrides synthesized ones")
    p.add_argument("--no-nonce", action="store_true", help="skip checkpoint pre-flights")
    p.add_argument("--timeout", type=float, default=15.0, help="per-request timeout (s)")
    p.add_argument("--insecure", action="store_true", help="do not verify TLS (Burp)")
    p.add_argument("--state-file", default=".ooredoo_device_state.json",
                   help="device + SESSION state persistence")
    p.add_argument("--x-sig-raw", action="store_true",
                   help="use the no-newline x-signature variant")
    p.add_argument("--logfile", help="custom log file path")
    p.add_argument("-v", "--verbose", action="store_true", help="debug output on console")
    args = p.parse_args()

    global X_SIGNATURE
    if args.x_sig_raw:
        X_SIGNATURE = X_SIGNATURE_RAW

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    setup_logging(args.logfile or f"ooredoo_login_{stamp}.log", args.verbose)

    state = load_state(args.state_file)
    banner()
    LOG.info("Base URL     : %s", args.base_url)
    LOG.info("x-signature  : %s%s", X_SIGNATURE[:16] + "…", " (raw variant)" if args.x_sig_raw else "")
    LOG.info("fp-mode      : %s", args.fp_mode)
    LOG.info("Pseudo-device: instance-id=%s  device-id=%s  (state: %s)",
             state["uuid"], state["device_id"], os.path.abspath(args.state_file))
    if args.proxy:
        LOG.info("Proxy        : %s", args.proxy)
    if args.insecure:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        LOG.warning("TLS verification DISABLED (interception mode)")

    extra = parse_extra_headers(args.extra_header)
    if extra:
        LOG.info("Extra headers: %s", extra)

    session = requests.Session()
    session.proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else None
    session.verify = not args.insecure

    # ---------------- one-shot logout ---------------------------------------
    if args.logout:
        sess = state.get("session")
        if not sess:
            LOG.info("[i] no saved session to log out.")
            return
        keycloak_logout(session, args.base_url, sess.get("msisdn", ""),
                        sess.get("refresh_token", ""), sess.get("access_token", ""),
                        extra, state, args.timeout,
                        fp_for(state, args.fp_mode, "session"))
        state["session"] = None
        save_state(args.state_file, state)
        LOG.info("[i] saved session cleared.")
        return

    # ---------------- resume saved session ------------------------------------
    sess = state.get("session")
    if sess and not args.fresh:
        left = token_seconds_left(sess.get("access_token", ""), sess.get("expires_at"))
        LOG.info("[i] saved session found for %s (captured %s)",
                 sess.get("msisdn"), sess.get("captured_at"))
        if left is not None and left > 5:
            LOG.info("[+] access token still valid (%d min left) — RESUMING SESSION.",
                     int(left // 60))
            if args.otp:
                LOG.info("[i] --otp ignored: session already valid.")
            state["_login_msisdn"] = sess.get("msisdn", "")
            session_shell(args, state, extra, session)
            return
        LOG.info("[i] access token expired — trying refresh_token grant …")
        ok = ensure_live_token(session, args, state, extra)
        if ok:
            LOG.info("[+] SESSION RESUMED via refresh token.")
            state["_login_msisdn"] = state["session"]["msisdn"]
            session_shell(args, state, extra, session)
            return
        LOG.warning("[!] session expired — falling back to a fresh OTP login.")
        state["session"] = None
        save_state(args.state_file, state)

    # ---------------- fresh OTP login ----------------------------------------
    msisdn = (args.msisdn or "").strip()
    if not msisdn and args.otp:
        LOG.error("[!] --otp requires a MSISDN when no saved session exists.")
        return
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
        state["_login_msisdn"] = normalize_msisdn(msisdn)
    except ValueError as exc:
        LOG.error("[!] %s — aborting.", exc)
        return
    LOG.info("Input MSISDN : %s  ->  normalized: %s", msisdn, state["_login_msisdn"])

    tokens = run_login_flow(args, state, extra, session)
    if tokens is None:
        LOG.info("=" * 76)
        sys.exit(1)

    save_state(args.state_file, state)          # persist the logged-in state
    if args.otp:
        LOG.info("[i] non-interactive mode: session saved to %s — rerun without "
                 "--otp to resume it.", os.path.abspath(args.state_file))
        return
    session_shell(args, state, extra, session)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] interrupted")
        sys.exit(130)
