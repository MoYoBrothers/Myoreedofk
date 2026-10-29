#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
 My Ooredoo (Algeria) v1.5.17 — OTP-SEND LOGIN-STEP SCRIPT (authorized pentest)
===============================================================================
 Target app   : My Ooredoo — com.algeria.selfcare.app.android v1.5.17 (1461)
 Source       : static reverse-engineering of 'My Ooredoo_1.5.17.apks'
                (jadx + Blutter Dart-AOT reversal of libapp.so)
 Reconstructed: ApiCalls::requestOTPbyMSISDN @ 0xb905b8 (api_calls.dart)
                ApiCalls::getNonceValidation @ 0x95c71c (api_calls.dart)
 Purpose      : replicate ONLY the "send me an SMS OTP" step of the app login.
                NO login / token redemption is performed by this script.
 Output       : full request/response logging (console + timestamped log file)
                for pentest documentation purposes.

 FLOW REPLICATED (verified against Dart AOT disassembly):
   1) POST {BASE}/api/ooredoo-bff/checkpoint/token        <- anti-replay nonce
        Content-Type: application/json
        headers: x-msisdn, x-path, x-method, X-Correlation-ID(uuid1),
                 platform, X-Platform-Origin, x-version ...
        response headers carry: x-nonce-id, x-chronos-id
   2) POST {BASE}/api/auth/realms/myooredoo/protocol/openid-connect/token
        Content-Type: application/x-www-form-urlencoded
        body:    client_id=myooredoo-app & grant_type=password
                 & username=<MSISDN> [& resend=true]
        headers: x-nonce-id, x-chronos-id, x-msisdn, x-force-update,
                 x-version, platform, X-Platform-Origin, X-Correlation-ID ...
      => the server side triggers the SMS OTP dispatch to the MSISDN.

 Device-bound headers the real app attaches (x-signature, X-Device-Fingerprint,
 X-Platform-Info, X-JWS/Huawei, X-Native-Integrity-Token/Play-Integrity) are
 generated per-install on a real device; here they are optional pass-through
 values (--extra-header) so the analyst can supply captured ones if desired.

 LEGAL: for use ONLY in controlled/authorized security-testing environments
 against numbers you own or are authorized to test. The author of this script
 accepts no liability for misuse.
===============================================================================
"""

import argparse
import json
import logging
import os
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
# Static configuration recovered from the APK (Dart string pool / asm)
# ---------------------------------------------------------------------------
BASE_URL = "https://apis.ooredoo.dz"                      # EnvironmentSettings::getCurrentEnv @ 0x926110
EP_NONCE = "/api/ooredoo-bff/checkpoint/token"            # ApiCalls::getNonceValidation @ 0x95ca00
EP_TOKEN = "/api/auth/realms/myooredoo/protocol/openid-connect/token"  # requestOTPbyMSISDN @ 0xb90658
CLIENT_ID = "myooredoo-app"                              # @ 0xb9084c
APP_VERSION = "1.5.17"                                    # x-version header
USER_AGENT = "Dart/3.11 (dart:io)"                        # Dart http default UA

APP_HEADERS = {
    "platform": "android",
    "X-Platform-Origin": "mobile-android",
    "x-version": APP_VERSION,
    "x-force-update": "true",
}

LOG = logging.getLogger("ooredoo-otp")


# ---------------------------------------------------------------------------
# Logging helpers — pentest-grade, full-wire documentation
# ---------------------------------------------------------------------------
def setup_logging(msisdn: str, logfile: str | None, verbose: bool) -> logging.Logger:
    """Console (INFO+) + file (DEBUG, everything) handlers."""
    LOG.setLevel(logging.DEBUG)
    LOG.handlers.clear()

    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", "%H:%M:%S")
    con = logging.StreamHandler(sys.stdout)
    con.setLevel(logging.DEBUG if verbose else logging.INFO)
    con.setFormatter(fmt)
    LOG.addHandler(con)

    if not logfile:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe = "".join(c if c.isalnum() else "_" for c in msisdn)
        logfile = f"ooredoo_otp_{safe}_{stamp}.log"
    fh = logging.FileHandler(logfile, mode="w", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s"))
    LOG.addHandler(fh)
    LOG.info("Log file: %s", os.path.abspath(logfile))
    return LOG


def banner() -> None:
    LOG.info("=" * 76)
    LOG.info("My Ooredoo 1.5.17 — OTP-SEND login-step replication (no login performed)")
    LOG.info("Reconstructed from: Apicalls::requestOTPbyMSISDN @ 0xb905b8")
    LOG.info("=" * 76)


def log_request(prep: requests.PreparedRequest) -> None:
    """Log the complete outgoing request exactly as it goes on the wire."""
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
    LOG.debug("raw request:\n%s", prep.path_url if False else body)


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
    """Send with full request + response documentation."""
    log_request(prep)
    t0 = time.time()
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
    LOG.debug("wire time: %.0f ms (total %.0f ms)",
              (time.time() - t0) * 1000, resp.elapsed.total_seconds() * 1000)
    log_response(resp)
    return resp


def parse_extra_headers(items: list[str] | None) -> dict[str, str]:
    """--extra-header 'K: V' (repeatable) — for captured device-bound headers."""
    out: dict[str, str] = {}
    for it in items or []:
        if ":" not in it:
            LOG.warning("[!] ignoring malformed --extra-header: %r", it)
            continue
        k, v = it.split(":", 1)
        out[k.strip()] = v.strip()
    return out


# ---------------------------------------------------------------------------
# Step 1 — checkpoint nonce (ApiCalls::getNonceValidation)
# ---------------------------------------------------------------------------
def get_nonce(session: requests.Session, base: str, msisdn: str,
              extra: dict[str, str], timeout: float,
              insecure: bool) -> tuple[str, str]:
    """
    POST {base}/api/ooredoo-bff/checkpoint/token

    The app calls this before the OTP request with:
        x-path   = the path of the call being protected (the token endpoint)
        x-method = POST
    and harvests 'x-nonce-id' / 'x-chronos-id' from the RESPONSE HEADERS
    (ApiCalls::requestOTPbyMSISDN @ 0xb908bc-0xb9096c).
    """
    url = base + EP_NONCE
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
        "x-msisdn": msisdn,
        "x-path": EP_TOKEN,          # protected call path
        "x-method": "POST",         # protected call method
        "X-Correlation-ID": str(uuid.uuid1()),  # Uuid::v1 @ 0x92afa0
        **APP_HEADERS,
        **extra,
    }
    req = requests.Request("POST", url, headers=headers, data={})
    prep = session.prepare_request(req)

    LOG.info("[STEP 1] checkpoint nonce — anti-replay pre-flight")
    resp = do_request(session, prep, timeout)

    nonce_id = resp.headers.get("x-nonce-id", "")
    chronos_id = resp.headers.get("x-chronos-id", "")
    if resp.ok:
        if nonce_id:
            LOG.info("[+] nonce acquired  x-nonce-id=%s  x-chronos-id=%s",
                     nonce_id, chronos_id or "(absent)")
        else:
            LOG.warning("[!] checkpoint responded 2xx but no x-nonce-id header — "
                        "the app sends an empty string in that case and continues.")
    else:
        LOG.warning("[!] checkpoint returned HTTP %s — continuing with empty nonce "
                    "(the app tolerates this: empty-string fallback @ 0xb908f8).",
                    resp.status_code)
    return nonce_id, chronos_id


# ---------------------------------------------------------------------------
# Step 2 — the OTP send (ApiCalls::requestOTPbyMSISDN)
# ---------------------------------------------------------------------------
def request_otp(session: requests.Session, base: str, msisdn: str,
                nonce_id: str, chronos_id: str, resend: bool,
                extra: dict[str, str], timeout: float) -> requests.Response:
    """
    POST {base}/api/auth/realms/myooredoo/protocol/openid-connect/token

    Body (x-www-form-urlencoded), exactly as built @ 0xb90840-0xb908b8:
        client_id  = myooredoo-app
        grant_type = password
        username   = <MSISDN>
        resend     = true            # ONLY on the resend variant

    NOTE (finding F-04 of the companion report): the received SMS OTP is later
    used AS the password of a ROPC grant (loginWithOTP). This script NEVER
    performs that second call — it stops after the OTP-dispatch step.
    """
    url = base + EP_TOKEN
    form = {
        "client_id": CLIENT_ID,
        "grant_type": "password",
        "username": msisdn,
    }
    if resend:
        form["resend"] = "true"      # @ 0xb908a0

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "User-Agent": USER_AGENT,
        "x-msisdn": msisdn,
        "x-nonce-id": nonce_id,
        "x-chronos-id": chronos_id,
        "X-Correlation-ID": str(uuid.uuid1()),
        **APP_HEADERS,
        **extra,
    }
    req = requests.Request("POST", url, headers=headers, data=form)
    prep = session.prepare_request(req)

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
    p.add_argument("msisdn", nargs="?", help="MSISDN to request the OTP for "
                   "(e.g. 0550123456 or 213550123456). Prompted if omitted.")
    p.add_argument("--resend", action="store_true",
                   help="mark the request as a re-send (adds resend=true to the grant body)")
    p.add_argument("--base-url", default=BASE_URL,
                   help="API base URL (override to point at a mock/lab endpoint)")
    p.add_argument("--proxy", help="HTTP(S) proxy for the traffic, e.g. http://127.0.0.1:8080 (Burp)")
    p.add_argument("--extra-header", action="append", metavar="K:V",
                   help="additional header, repeatable (x-signature, X-JWS, "
                        "X-Device-Fingerprint, X-Native-Integrity-Token, ...)")
    p.add_argument("--no-nonce", action="store_true",
                   help="skip the checkpoint pre-flight (send empty nonce ids)")
    p.add_argument("--timeout", type=float, default=15.0, help="per-request timeout (s)")
    p.add_argument("--insecure", action="store_true",
                   help="do not verify TLS (needed for interception proxies w/ self-signed certs)")
    p.add_argument("--logfile", help="custom log file path")
    p.add_argument("-v", "--verbose", action="store_true", help="debug output on console")
    args = p.parse_args()

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

    setup_logging(msisdn, args.logfile, args.verbose)
    banner()
    LOG.info("Target MSISDN : %s", msisdn)
    LOG.info("Base URL      : %s", args.base_url)
    if args.proxy:
        LOG.info("Proxy         : %s", args.proxy)
    if args.insecure:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        LOG.warning("TLS verification DISABLED (interception mode)")

    extra = parse_extra_headers(args.extra_header)
    if extra:
        LOG.info("Extra headers : %s", extra)

    session = requests.Session()
    session.proxies = {"http": args.proxy, "https": args.proxy} if args.proxy else None
    session.verify = not args.insecure

    # --- step 1: anti-replay nonce ----------------------------------------
    if args.no_nonce:
        LOG.info("[STEP 1] skipped by --no-nonce (empty nonce ids)")
        nonce_id, chronos_id = "", ""
    else:
        try:
            nonce_id, chronos_id = get_nonce(session, args.base_url, msisdn,
                                             extra, args.timeout, args.insecure)
        except SystemExit:
            raise
        except Exception as exc:  # keep going like the app does on failure
            LOG.warning("[!] checkpoint pre-flight failed (%s) — continuing with empty nonce", exc)
            nonce_id, chronos_id = "", ""

    # --- step 2: the OTP dispatch ------------------------------------------
    resp = request_otp(session, args.base_url, msisdn, nonce_id, chronos_id,
                       args.resend, extra, args.timeout)

    # --- verdict ------------------------------------------------------------
    LOG.info("=" * 76)
    if 200 <= resp.status_code < 300:
        LOG.info("[+] OTP-REQUEST COMPLETED — HTTP %s. If the MSISDN is valid and "
                 "authorized, an SMS OTP has been dispatched by the operator.",
                 resp.status_code)
        LOG.info("[i] Per design (F-04), the app would next use that OTP as the "
                 "'password' of a ROPC grant — intentionally NOT done here.")
    elif resp.status_code in (400, 401, 403):
        LOG.info("[*] HTTP %s — challenge/rejection. Inspect the body above: the "
                 "server may demand device-bound headers (x-signature / "
                 "X-Native-Integrity-Token / X-JWS) or nonce validation failed.",
                 resp.status_code)
    elif resp.status_code == 429:
        LOG.info("[*] HTTP 429 — rate-limited / too many OTP requests for this MSISDN.")
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
