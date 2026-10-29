# My Ooredoo 1.5.17 — "Power of Snake" Gamification Module — Full Reverse-Engineering Analysis

**Target:** My Ooredoo (Algeria) — `com.algeria.selfcare.app.android` v1.5.17 (1461)
**Method:** Static analysis — Blutter Dart-AOT disassembly (`libapp.so`), cross-referenced with live mitmproxy captures and **field-verified** server responses
**Scope:** `features/power_snake/**` module + legacy gamification calls in `api/api_calls.dart` + the Flarie "Score & Win" WebView layer + the runtime CMS
**Companion client:** `ooredoo_otp_send.py` **[v8]** — after login a SIMPLE NUMBERED MENU: `1` Power of Snake (auto-open all cards), `2` Daily Game (claim today's gift), `3` cards, `4` history, `5` Score & Win browser link, `6` status, `7` new login, `8` logout, `9` custom API call, `0` exit + `--autoopen` one-shot flag

---

## 1. Executive summary

"Power of Snake" is a **purchase-triggered scratch-card loyalty mechanic**. Every
**bundle purchase** mints one card server-side (mystery data reward, 2 GB … 1 TB,
3-day validity — per the live CMS FAQ: *"Achetez un forfait My Ooredoo et un
Power of Snake sera ajouté à votre compte"*). The client is a thin wrapper over
**five BFF endpoints**; all state lives server-side and the client only needs the
Keycloak `access_token` to list and redeem cards.

| # | Endpoint | Method | Layer | Nonce? | Purpose |
|---|----------|--------|-------|--------|---------|
| 1 | `/api/ooredoo-bff/gamification/power-snake?status=AVAILABLE` | GET | module Dio (`RegisterModule::dio`) | **no** | list openable cards |
| 2 | `/api/ooredoo-bff/gamification/power-snake/<uuid>/redeem` | POST (**empty body**) | module Dio | **no** | open a card |
| 3 | `/api/ooredoo-bff/gamification/status` | GET | legacy `ApiCaller.requestAuth` | no | daily-game FAB gating `{played, lastPlayedTime}` |
| 4 | `/api/ooredoo-bff/gamification/history` | GET | legacy `requestAuth` | no | past rewards |
| 5 | `/api/ooredoo-bff/gamification/play` | GET | legacy `playGame` | **YES** (`getNonceValidation`) | daily game payload |
| 6 | `/api/ooredoo-bff/flarie/player/token` | GET | legacy `flarieGetToken` | pre-flight used by client | `{token, attempts}` — Flarie "Score & Win" player identity |
| 7 | `/cms/v2/api/ui-labels?locale=en|fr|ar` | GET | **public Strapi CMS** | no | live campaign config incl. `flarie_url` game template |

The critical client-side quirk: **the app treats `body.code == 400` as the
SUCCESS verdict for a redeem** (`PowerSnakeCubit` compares the JSON field with
`0x190` and branches to the *failed* path on any other value).

**Field-verified (2026-10-29):** the BFF *does* enforce card status
**server-side** on `redeem` — replaying a REDEEMED uuid returns
`HTTP 500 {"success":false,"message":"Power snake not available for redemption.
Current power snake status is: REDEEMED"}`. The listing filter is bypassable
(any status / none); the redeem gate is not. "Opening cards with none
available" therefore requires the *grant* event — see §10 for the full
Flarie + purchase analysis.

---

## 2. Transport & security posture

### 2.1 The two transports

* **Module Dio** (`RegisterModule::dio` @ `0xb5c64c`, `core/di/injections.dart`)
  — used by `RemotePowerSnakeApi` (endpoints 1–2):
  * `BaseOptions`: `baseUrl = env.baseUrl` (`https://apis.ooredoo.dz`), headers
    `Accept: application/json` **and** `Content-Type: application/json` on
    *every* request (including GETs);
  * one `InterceptorsWrapper` (closure @ `0xb5d128`) that stamps, in order:
    `X-Correlation-ID` (uuid1), `setDeviceDataGather` (X-Platform-Info …),
    `setDeviceFingerprintHeader` (X-Timestamp / X-Instance-Id /
    X-Device-Fingerprint), `platform: android`, `X-Platform-Origin`,
    `x-version`;
  * **no checkpoint/nonce interceptor** → `x-nonce-id` / `x-chronos-id` are
    never sent by this module;
  * plus a `TalkerDioLogger` (pure logging).
* **Legacy layer** (`ApiCalls`/`ApiCaller` in `api/api_calls.dart` /
  `api/api_caller.dart`) — endpoints 3–5: same common header suite
  (`_getCommonHeaders` @ `0x92a350`), `Authorization: Bearer` added by
  `requestAuth` (@ `0x959c04`), which also transparently token-refreshes.
  `playGame` (@ `0xe89a74`) **additionally** performs the anti-replay
  checkpoint pre-flight
  `getNonceValidation(msisdn, "GET", "/api/ooredoo-bff/gamification/play")`
  before the request and forwards `x-nonce-id`/`x-chronos-id`.

### 2.2 Per-call auth (`_authHeaders` @ `0xdf34d8`)

```
Settings::getIsMaster() ? Settings::getAccessToken() : Settings::getSlaveAccessToken()
→ headers = { "Authorization": "Bearer <token>", "x-msisdn": <msisdn> }
```

So both snake calls carry **Bearer + x-msisdn on top of the common suite**
(x-signature, X-Platform-Info, X-Timestamp, X-Instance-Id, X-Device-Fingerprint,
platform, X-Platform-Origin, x-version, X-Correlation-ID).

---

## 3. How the app knows you have cards

Three independent mechanisms:

1. **On-demand list** — `PowerSnakeCubit::getPowerSnakes` (@ `0xde9898`,
   called from `PowerSnakeScreen` @ `0x1269fb4 and `PowerSnakesTab` refresh
   @ `0xde9884`): emits `loading → success(items)` / `failed`. `items`
   non-empty ⇒ cards to open. The list request always filters
   `status=AVAILABLE`.
2. **Auto-popup** (`bloc/auto_popup/popup_cubit.dart`) — the home screen can
   pop the snake sheet automatically. Gating conditions (all read through
   `tr()` translation keys, i.e. remotely-configurable flags):
   * `is_power_snake_popup_enabled` == `"true"`
   * `power_snake_enabled` == `"true"`
   * `checkPowerSnakeTimeRestriction()` (@ `0x10fa388`):
     `now - Settings::getPowerSnakePopupLastShown() >=
     myo_power_snake_auto_popup_restricted_time_in_hours`
   * after showing: `markPowerSnakeShown` (@ `0xc51bf0`) persists the
     timestamp via `Settings::setPowerSnakePopupLastShown`.
   The same popup manager arbitrates between campaigns: `echri_bsarf`,
   `arcane`, `tod`, `world_cup`, `soccer`, `ramadan_promo`, `five_g`, `cvm`,
   `flarie`, `puzzle_snake`, `raffle_draw`, `blacknut`, `level_up`,
   `power_snake` (string pool @ `0x10f95c8–0x10f966c`).
3. **Daily-game FAB** (`gaming_floating_action_button.dart` +
   `GameCubit::callGameApiStatusEvent` @ `0xc49efc`): flag
   `gamification-UI-Enable` ⇒ `getGameStatus` ⇒
   `played == true` → hide FAB (`GameUIDisableState`, parses `lastPlayedTime`),
   `played == false` → show FAB (`GameUIEnableState`).

The **server is the single source of truth**: nothing is cached between
sessions; the sheet always re-fetches `power-snake?status=AVAILABLE`.

---

## 4. Data models (wire JSON)

### 4.1 Card list — `GET …/power-snake?status=AVAILABLE`

```jsonc
{
  "total": 2,                                  // PowerSnakeModel.total
  "items": [                                   // PowerSnakeModel.items[]
    {
      "uuid": "6a0e2c77-…",                    // ← redeem key
      "earnedDate": "2026-10-28T09:14:00Z",
      "expiryDate": "2026-11-11T09:14:00Z",
      "status": "AVAILABLE",                   // also REDEEMED / EXPIRED seen in model
      "assignedReward": {                      // AssignedReward
        "type": "DATA",                        // reward_type
        "reward": {                           // RewardDetailsModel
          "usage-value": "10",
          "usage-unit": "GB",
          "unlimited-usage": "",               // non-empty ⇒ "unlimited"
          "validity": "7",
          "validity-unit": "day"
        },
        "earnedDate": "…"
      },
      "redeemedDate": null
    }
  ]
}
```

### 4.2 Redeem — `POST …/power-snake/<uuid>/redeem`

* **Request body: none.** Dio `post(path, data: null)` (array @ `0xdf43d4`
  builds only the URL `"/api/ooredoo-bff/gamification/power-snake/" + uuid +
  "/redeem"`; the stack slot for `data` is `NULL` @ `0xdf4434`) ⇒
  `Content-Length: 0`, `Content-Type: application/json` from BaseOptions.

```jsonc
{
  "message": "…",                    // PowerSnakeRedeemResponse.message
  "code": 400,                       // ← 400 == SUCCESS (see §5)
  "assignedReward": { "type": "…", "reward": { …as above… }, "earnedDate": "…" }
}
```

### 4.3 `GET …/gamification/status`

```jsonc
{ "played": false, "lastPlayedTime": "2026-10-28T18:22:00Z" }
```

---

## 5. The redeem verdict — `code == 400` means success

`PowerSnakeCubit::unlockPowerSnake` (@ `0xdf3ebc`) after awaiting the use-case:

```asm
0xdf3f38: LoadField: r1 = r0->field_b      ; response.code  (num → int via fromJson)
0xdf3f40: cmp     w1, #0x190               ; == 400
0xdf3f44: b.ne    #0xdf4168                ; anything else → FAILED branch
; fall-through = SUCCESS branch:
;   CleverTap onPowerSnakeActivation {"status":"success",
;       "reward_type": assignedReward.type,
;       "reward_value": unlimited-usage ? "unlimited"
;                        : "${usage-value} ${usage-unit}" (N/A fallbacks)}
;   emit PowerSnakeUnlockSuccess(message:"", powerSnakeReward: response)
;   Future.delayed(Duration) → getPowerSnakes()      ; refresh list
0xdf4168: ; FAILED branch:
;   CleverTap onPowerSnakeActivation {"status":"failed"}
;   emit PowerSnakeUnlockFailed(message ?? "Something went wrong", snakes)
```

Why 400? The BFF evidently wraps a downstream gamification service and
mirrors its status code in the JSON body while answering HTTP 2xx to the
client. The app engineers made `400` the "redeem-ok" sentinel. Practical
consequence for replication: **parse the body, ignore the HTTP status for the
verdict, and treat `code == 400` as unlocked.**

Error translation (`RemotePowerSnakeApi::unlockPowerSnake` catch @
`0xdf4490`): `DioException` → `response.data["message"]` (Map directly, or
`jsonDecode` if string) → `throw ApiException(message ?? "Something went
wrong")`; non-Dio → `"Failed to unlock power snake: $e"`.

UI trigger (`power_snakes_tab.dart` closure @ `0xdf3dd8`): tap card →
`setState` (animation) → `uuid == null ?` error toast
(`something_went_wrong_try_again_later_new`) `: cubit.unlockPowerSnake(uuid)`.

---

## 6. Full client flow (state machine)

```
[Home screen]
   ├─ PopupCubit: flags + hours-since-last-popup ──────► show snake sheet (auto)
   └─ GameCubit: gamification/status {played} ─────────► game FAB
[Snake screen / bottom sheet]
   └─ PowerSnakeCubit.getPowerSnakes()
         GET power-snake?status=AVAILABLE
         ├─ loading → success(items)  ──► render _SnakeCard list
         └─ failed(error)
[Tap a card]
   └─ PowerSnakeCubit.unlockPowerSnake(uuid)
         POST power-snake/<uuid>/redeem        (EMPTY body)
         ├─ code == 400 → UnlockSuccess(reward) ──► success sheet
         │                  └─ delay → getPowerSnakes()   (refresh)
         └─ else      → UnlockFailed(message)
```

CleverTap events: `onPowerSnakeActivation` (success/failed), plus
`gamification_accessed` when the gamification hub is opened.

---

## 7. Replication checklist (Python client v8)

Implemented in `ooredoo_otp_send.py` **[v8]** (post-login NUMBERED MENU — every
option is listed on screen, you type its number; Power of Snake and the Daily
Game are SEPARATE items and each runs fully on its own):

| Menu item | Emits |
|----------------|-------|
| `1` — **Power of Snake** | **THE CARD BYPASS, fully automatic**: probes the list endpoint with EVERY status filter (and none), dedupes by uuid, POSTs redeem on EVERY card regardless of status, applies the `code==400` verdict per card, prints rewards + summary. Runs even when the app shows zero AVAILABLE cards. |
| `2` — **Daily Game** | **THE DAILY-GIFT BYPASS, fully automatic**: `GET …/status` (played?), and if not played yet: checkpoint nonce pre-flight (`x-path=…/play, x-method=GET`) then `GET …/play` — the daily spin-wheel gift arrives IN THE RESPONSE (`giftName`, `validityHour`; parsed by game_home_screen @ 0xe89df8). If already played, shows the most recent gift from history. |
| `3` — My Snake Cards | `GET …/power-snake` (no filter — full enumeration) — pretty card table |
| `4` — Game History | `GET …/history` |
| `5` — Score & Win | nonce pre-flight + `GET /api/ooredoo-bff/flarie/player/token` → prints `{token, attempts}` and the **browser-playable game URL** (`flarie_url` template with `{coid}` filled) |
| `6` — Session Status | msisdn, token expiries, instance/device ids |
| `7` — New Login | fresh SMS OTP flow (replaces the session) |
| `8` — Logout | Keycloak logout + clear persisted session |
| `9` — Custom API Call | advanced: authenticated `METHOD PATH [JSON]` with the full header suite |
| `0` / `q` — Exit | persist the session and quit |
| `--autoopen` flag | non-interactive: runs menu `1` + menu `2` once after login/resume, then shows the menu |

### 7.1 What the bypass does and does NOT remove (field-tested)

* The **listing gate** is the `?status=AVAILABLE` query parameter the app
  itself chooses (`getPowerSnakes` @ 0xde9c6c). The BFF serves any other
  status (or none) to the same endpoint — so cards in REDEEMED/EXPIRED/other
  states **can be enumerated** outside the app.
* The **redeem gate is SERVER-side** (field-verified): re-redeeming a
  REDEEMED uuid → `HTTP 500 "Power snake not available for redemption.
  Current power snake status is: REDEEMED"`. Statuses REDEEMED / AVAILABLE /
  EXPIRED are the only valid filters; the rest (LOCKED/PENDING/EARNED/…)
  crash the BFF with a plain 500.
* The spin-wheel / puzzle-snake / Flarie WebView games are **pure client
  theater for the DAILY gift**: granted by a plain authenticated
  `GET …/play` with the checkpoint nonce — no score, no session proof is
  uploaded. Skipping straight to `play` yields the same daily gift
  (field-verified: `{"giftName":"50Mo","validityHour":2}` with zero gameplay).
* **Cards cannot be conjured without a purchase**: the mint is a billing-side
  event (one card per bundle purchase, per the CMS FAQ). The correct
  headless flow is: purchase (any channel, e.g. USSD) → menu `1` (Power of
  Snake) redeems the new card with no app UI at all. Menu `5` (Score & Win)
  fetches the **Flarie** player token + browser game URL (§10) so the second
  reward track is reachable outside the app too.

### 7.2 v6 wire-format corrections (STEP-4 401 suspects)

| Header | v3–v5 (wrong) | v6 (AOT-verified) |
|---|---|---|
| `X-Platform-Info` (Keycloak grants, `setDeviceDataGatherForKeycloak` @ 0x95c568) / `X-Platform-Data-Signature` (BFF `_getCommonHeaders` @ 0x92aab4 + module-Dio interceptor) | raw JSON string | **Base64(utf8(json))** (JsonCodec → Utf8Encoder → Base64Codec) |
| `device-id` inside that payload | random 16-hex token | **Settings 'uuid'** — the exact same value as `X-Instance-Id` (`setUUIdForUser` @ 0x1157168: `Uuid.v1() + epoch-millis`) |
| `X-Correlation-ID` (`ApiCalls::getXCorrelationId` @ 0x92af84) | bare uuid4 | **`Uuid.v1() + epoch-millis`** |
| `X-Device-Fingerprint` msg (`SignatureHelper::generateDeviceFingerprint` @ 0x92a630) | `msisdn + uuid + ts` | **`ts + uuid + msisdn`** (key = ts; operand order resolved from the AOT `+`-stub ABI) |
| Power-snake module Dio headers (interceptor @ 0xb5d128) | full legacy suite incl. x-signature / x-force-update / X-Platform-Info | **no x-signature, no x-force-update, no X-Platform-Info** — only X-Platform-Data-Signature (b64) + fingerprint triplet + platform/x-version |

The client keeps all six fingerprint concatenation orders selectable
(`--fp-order`, default `auto`): on a 401 verify grant it rotates the orders ×
the two platform-info encodings with the SAME OTP and persists the winning
profile in the state file.

---

## 8. Evidence index (Dart AOT addresses)

| Function | Address | File |
|---|---|---|
| `RemotePowerSnakeApi::getPowerSnakes` | `0xde9bfc` | `features/power_snake/data/source/power_snake_api.dart` |
| `RemotePowerSnakeApi::_authHeaders` | `0xdf34d8` | idem |
| `RemotePowerSnakeApi::unlockPowerSnake` | `0xdf4388` | idem |
| `PowerSnakeRepo::getPowerSnakes / unlockPowerSnake` | `0xde9ba8 / 0xdf432c` | `data/repository/power_snake_repo.dart` |
| `PowerSnakeCubit::getPowerSnakes` | `0xde9898` | `presentation/logic/power_snake_cubit.dart` |
| `PowerSnakeCubit::unlockPowerSnake` (verdict `cmp #0x190`) | `0xdf3ebc / 0xdf3f40` | idem |
| `GetPowerSnakesUseCase / UnlockPowerSnakeUseCase` | `0xde9b54 / 0xdf42d0` | `domain/usecases/*` |
| `RegisterModule::dio` (module transport) | `0xb5c64c` | `core/di/injections.dart` |
| Dio request interceptor | `0xb5d128` | idem |
| `ApiCalls::getGameStatus` | `0xc4a024` | `api/api_calls.dart` |
| `ApiCalls::getGameHistories` | `0xd03e70` | idem |
| `ApiCalls::playGame` (+ nonce) | `0xe89a74` | idem |
| `GameCubit::callGameApiStatusEvent` | `0xc49efc` | `bloc/game_bloc/game_cubit.dart` |
| `PopupCubit::checkPowerSnakeTimeRestriction` | `0x10fa388` | `bloc/auto_popup/popup_cubit.dart` |
| `PopupCubit::markPowerSnakeShown` | `0xc51bf0` | idem |
| `_PowerSnakesTabState` unlock tap closure | `0xdf3dd8` | `presentation/screens/power_snakes_tab.dart` |
| Card-tap error toast key | `0xdf3e7c` (`something_went_wrong_try_again_later_new`) | idem |
| `ApiCalls::flarieGetToken` | `0xb7f90c` | `api/api_calls.dart` |
| `::handlePuzzleSnakeDeeplink` (flags + token + WebView) | `0xb7eb80` | `utils/functions/common_functions.dart` |
| `::handleFlarieDeeplink` | `0xb7fca0` | idem |
| `PuzzleSnakeWebView::loadGameUrl` (`{coid}` template) | `0x1169e5c` | `ui/screens/gamification/puzzle_snake_gamification_screen.dart` |
| `PuzzleSnakeWebViewState::handleCallback` (JS channel "Flutter": `loading`/`game` msgs) | `0x11676dc` | idem |
| `PuzzleSnakeWebViewState::gameOverCallback` (score/time → CleverTap only, NO BFF call) | `0x11679a4` | idem |
| `FlarieWebView` (spin-wheel twin) | `0x1161e00`/`0x116395c` | `ui/screens/gamification/flarie_gamification_screen.dart` |
| `OoredooAssetLoader::load` (runtime CMS i18n) | `0x13250c1` (obj) / `load` in class id 4106 | `utils/ooredoo_asset_loader.dart` |
| `ApiCalls::getUiLabels` (public CMS labels) | `0xb6418c` | `api/api_calls.dart` |

---

## 9. Security observations (pen-test notes)

1. **No replay protection on redeem** — the card-redeem endpoint requires
   neither a nonce nor a body; any client holding a live `access_token` can
   redeem any **own** AVAILABLE card. The anti-replay checkpoint is only
   wired into the *legacy* layer (login/refresh/play). Status, however,
   **is** re-checked server-side (field-verified: REDEEMED → 500).
2. **`code: 400` as success sentinel** invites server/client drift: a future
   BFF returning a genuine 400-style error inside a 2xx envelope would be
   rendered as a successful unlock by old clients.
3. **Popup flags delivered through the i18n layer** (`tr("is_power_snake_popup_enabled")`)
   — weak remote-config channel; values are translation strings compared to
   `"true"` (case/whitespace-sensitive: the code `trim()`s but does not
   lowercase). The full campaign config (game URL, excluded rate plans,
   employee blockers, attempt backoff) ships from a **public, unauthenticated
   Strapi CMS** (`/cms/v2/api/ui-labels`) — no client secret required to read.
4. **Full reward metadata leaks pre-open**: the list response embeds each
   card's `assignedReward` *before* redemption — the "surprise" is visible to
   any API client, enabling selective opening of only high-value cards.
5. **The daily gamification is entirely optional client-side** (v6 finding):
   the card gate is a query parameter (`status=AVAILABLE`) and the daily gift
   is a plain nonce'd GET — no game interaction is required to obtain either.
   The card **mint** is the only strictly server-side event (§10).
6. **The "app-only" game is a public web page** (v7 finding): the Flarie
   Score & Win puzzle plays in any browser given the player token from
   `/flarie/player/token`; the game's scoring engine (`prod-api.flarie.com`)
   is directly reachable with an `isCheater` guard as the only visible
   server-side defense on score submission.

---

*Authorized security-testing research artifact — use only against accounts
you own. Companion log/proof-of-concept: `ooredoo_otp_send.py` v6.*

## 10. The Flarie "Score & Win" layer + the real card-earning mechanic (v7)

Field-tested 2026-10-29 against the live CMS + game bundle. This is the layer
the app hides inside two WebViews (`ui/screens/gamification/`).

### 10.1 Where the game URL comes from (it is NOT in the APK)

`PuzzleSnakeWebView.loadGameUrl` @ `0x1169e5c` resolves the URL via
`tr("myo_puzzle_snake_url", {"coid": …})` — an easy_localization key. The
shipped `assets/translations/*.json` do **not** contain it: at startup
`OoredooAssetLoader` @ `0x13250c1` (custom `AssetLoader`) calls
`ApiCalls::getUiLabels` @ `0xb6418c` → **public** Strapi call:

```
GET https://apis.ooredoo.dz/cms/v2/api/ui-labels?locale=fr&pagination[pageSize]=8000
→ data[].attributes.{name, value}   (~5000 labels, no auth)
```

Live values that matter (2026-10-29):

| key | value |
|---|---|
| `flarie_url` | `https://game-eu.flarie.com/games/puzzle/a202d843-5997-49da-a876-4c7f01458660?uuid={coid}` |
| `power_snake_enabled` | `true` |
| `is_power_snake_popup_enabled` | `true` |
| `excluded_rate_for_flarie` | `["707","656","680","681","698","716","744","657","658","609","755"]` |
| `myo_is_disabled_employee_check_for_flarie` | `true` |
| `flarie_429_err_desc` | "…you reached the game limit… retry in 10 minutes…" |
| `power_snake_instructions` | *"Achetez un forfait My Ooredoo et un Power of Snake sera ajouté à votre compte"* |
| `power_snake_faq_list` | *"Chaque forfait acheté vous [donne] un Power of Snake"* |

**⇒ the earning rule is purchase-based**, confirmed by the app's own live FAQ:
one card per bundle purchase; the game is a separate prize track.

### 10.2 The player token = the whole game session

`handlePuzzleSnakeDeeplink` @ `0xb7eb80` gates on the CMS flags above, then:

```
ApiCalls::flarieGetToken @ 0xb7f90c
  GET /api/ooredoo-bff/flarie/player/token   (Bearer + x-msisdn)
  → {"attempts": <int>, "token": "<flarie player uuid>"}
```

The token is injected as `{coid}` → the app's WebView merely loads
`https://game-eu.flarie.com/games/puzzle/a202d843-…?uuid=<token>`.
**Consequence:** the identical URL plays in any browser on any device — the
"app-only" constraint is fiction. The BFF also enforces: excluded rate plans
(see list above), an employee blocker flag, and an attempt counter
(429-style "retry in 10 minutes" backoff; `flarie_429_err_*` strings).

### 10.3 The Flarie game engine API (from the game's own JS bundle)

The puzzle page's engine talks to `https://prod-api.flarie.com`:

| endpoint | purpose |
|---|---|
| `POST /api/post-game-load` | game load event |
| `POST /api/post-game-start` | play session start |
| `POST /api/post-game-score` | **score submit** — payload carries `gameId`, `playerId`, `uniqueId` (`uuid_epoch-ms`), score/time; response carries `highScore`, `ranking`, and `couponCode` prizes |
| `POST /api/post-game-share` / `-click` / `-form` | telemetry / lead forms |

The client JS contains an `isCheater` branch on the score response — scores
are sanity-checked server-side against the play session, so naive
`post-game-score` replays with inflated scores are the obvious next pentest
target (requires a live player token; **menu `5` Score & Win supplies it**).

### 10.4 What "open even when no cards" means after this research

| Track | Grant mechanism | Bypass status |
|---|---|---|
| Daily gift (50Mo/200Mo/…) | `GET /gamification/play` (nonce) | ✅ fully bypassed — granted with zero gameplay |
| Snake cards (2GB…1TB) | **server-side mint per bundle purchase** | listing+redeem fully headless; mint itself requires the billing event — no client bypass exists |
| Score & Win prizes | Flarie game (WebView ⇄ prod-api.flarie.com) | ✅ escaped the app — the game URL with the player token plays in any browser; score-submit API identified |

`--autoopen` runs the full harvest non-interactively (menu `1` cards → menu `2`
daily gift); interactively each track is its own numbered menu item.

---

*Authorized security-testing research artifact — use only against accounts
you own. Companion log/proof-of-concept: `ooredoo_otp_send.py` v8.*
