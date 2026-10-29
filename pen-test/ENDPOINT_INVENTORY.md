# My Ooredoo 1.5.17 — Full URI / Endpoint Inventory (static analysis)

Source: `My Ooredoo_1.5.17.apks` — Blutter Dart-AOT reversal (libapp.so, Dart 3.11.5) + jadx + string-pool scans

Total distinct paths: **216**

## Hosts / base URLs
```
http://api.ooredoo.dz/Shops/getWilayas
https://apis.ooredoo.dz            <- primary API base (EnvironmentSettings::getCurrentEnv)
http://apis.ooredoo.dz             <- cleartext variant present in pool
https://algeria.page.link          <- Firebase dynamic links (mgm/referral)
```

## Authentication / account (49)

- `/api/ooredoo-bff/attestation/challenge`
- `/api/ooredoo-bff/biometric/token`
- `/api/ooredoo-bff/checkpoint/token`
- `/api/ooredoo-bff/custom/token`
- `/api/ooredoo-bff/sa/all`
- `/api/ooredoo-bff/sa/master`
- `/api/ooredoo-bff/sa/master/link-accounts`
- `/api/ooredoo-bff/sa/master/unlink`
- `/api/ooredoo-bff/sa/migration/status`
- `/api/ooredoo-bff/sa/migration/v2/changeContractOffer`
- `/api/ooredoo-bff/sa/requestOTP`
- `/api/ooredoo-bff/sa/slave`
- `/api/ooredoo-bff/sa/slave/logout`
- `/api/ooredoo-bff/sa/slave/token`
- `/api/ooredoo-bff/sa/slave/token/refresh`
- `/api/ooredoo-bff/sahlabox/auth/login`
- `/api/ooredoo-bff/sahlabox/auth/pretoken`
- `/api/ooredoo-bff/sahlabox/auth/register`
- `/api/ooredoo-bff/sahlabox/auth/reset/request`
- `/api/ooredoo-bff/sahlabox/auth/token`
- `/api/ooredoo-bff/social/login`
- `/api/ooredoo-bff/social/register`
- `/api/ooredoo-bff/social/resendotp`
- `/api/ooredoo-bff/users/activate`
- `/api/ooredoo-bff/users/authping`
- `/api/ooredoo-bff/users/autologin`
- `/api/ooredoo-bff/users/changeEmail`
- `/api/ooredoo-bff/users/changePassword`
- `/api/ooredoo-bff/users/create-password`
- `/api/ooredoo-bff/users/data-share-pro/get-slaves`
- `/api/ooredoo-bff/users/deleteUser`
- `/api/ooredoo-bff/users/detect`
- `/api/ooredoo-bff/users/haya/recharge-mode`
- `/api/ooredoo-bff/users/haya/switch-mode`
- `/api/ooredoo-bff/users/loan/apply`
- `/api/ooredoo-bff/users/loan/eligibleBands`
- `/api/ooredoo-bff/users/mgm/attribute/update`
- `/api/ooredoo-bff/users/mgm/info/apply`
- `/api/ooredoo-bff/users/mgm/invitations`
- `/api/ooredoo-bff/users/mgm/redeem`
- `/api/ooredoo-bff/users/mgm/referral`
- `/api/ooredoo-bff/users/quickaccess/register`
- `/api/ooredoo-bff/users/recharge/pin`
- `/api/ooredoo-bff/users/register`
- `/api/ooredoo-bff/users/reset/password`
- `/api/ooredoo-bff/users/reset/request`
- `/api/ooredoo-bff/users/sendEmailverification`
- `/api/ooredoo-bff/users/status`
- `/api/ooredoo-bff/users/validateUser`

## BFF · 5 (1)

- `/api/ooredoo-bff/5G/register`

## BFF · anaflix (4)

- `/api/ooredoo-bff/anaflix/getContent`
- `/api/ooredoo-bff/anaflix/getUser`
- `/api/ooredoo-bff/anaflix/play`
- `/api/ooredoo-bff/anaflix/purchase`

## BFF · anazik (6)

- `/api/ooredoo-bff/anazik/content/getContent`
- `/api/ooredoo-bff/anazik/content/getUser`
- `/api/ooredoo-bff/anazik/player/stream`
- `/api/ooredoo-bff/anazik/service/getSubPlans`
- `/api/ooredoo-bff/anazik/service/subscribe`
- `/api/ooredoo-bff/anazik/service/unsubscribe`

## BFF · asset (1)

- `/api/ooredoo-bff/asset/file`

## BFF · available-services (1)

- `/api/ooredoo-bff/available-services/change`

## BFF · bundle (18)

- `/api/ooredoo-bff/bundle/boost/bundle-purchase`
- `/api/ooredoo-bff/bundle/boost/eligible-bundles`
- `/api/ooredoo-bff/bundle/bundleConversion`
- `/api/ooredoo-bff/bundle/bundlePurchase/v2`
- `/api/ooredoo-bff/bundle/bundleRefill`
- `/api/ooredoo-bff/bundle/free-calls/activate`
- `/api/ooredoo-bff/bundle/getActivePackages`
- `/api/ooredoo-bff/bundle/getBundleConvertEligibility`
- `/api/ooredoo-bff/bundle/others/bundle-purchase`
- `/api/ooredoo-bff/bundle/others/eligible-bundles`
- `/api/ooredoo-bff/bundle/purchase/byop`
- `/api/ooredoo-bff/bundle/scholar/purchase`
- `/api/ooredoo-bff/bundle/slave/bundlePurchase`
- `/api/ooredoo-bff/bundle/social-bundle/purchase`
- `/api/ooredoo-bff/bundle/tod/purchase`
- `/api/ooredoo-bff/bundle/yooz/byop`
- `/api/ooredoo-bff/bundle/yooz/purchase`
- `/api/ooredoo-bff/bundle/yooz/super/purchase`

## BFF · credit (3)

- `/api/ooredoo-bff/credit/advancedpayment`
- `/api/ooredoo-bff/credit/p2p/confirm`
- `/api/ooredoo-bff/credit/p2p/initiate`

## BFF · cvm (11)

- `/api/ooredoo-bff/cvm/boosters-bundles`
- `/api/ooredoo-bff/cvm/bundlePurchase`
- `/api/ooredoo-bff/cvm/cvm_optINOUT`
- `/api/ooredoo-bff/cvm/dynamic-bundle-purchase`
- `/api/ooredoo-bff/cvm/fusion-bearings`
- `/api/ooredoo-bff/cvm/getBundles`
- `/api/ooredoo-bff/cvm/getCvmAllocations`
- `/api/ooredoo-bff/cvm/getPcBundles`
- `/api/ooredoo-bff/cvm/scholar-bundles`
- `/api/ooredoo-bff/cvm/status`
- `/api/ooredoo-bff/cvm/yooz/get-bundles/v2`

## BFF · dashboard (1)

- `/api/ooredoo-bff/dashboard/database/sync`

## BFF · e-ticket (3)

- `/api/ooredoo-bff/e-ticket`
- `/api/ooredoo-bff/e-ticket/eligible`
- `/api/ooredoo-bff/e-ticket/get-failed-tickets`

## BFF · favorite-numbers (2)

- `/api/ooredoo-bff/favorite-numbers`
- `/api/ooredoo-bff/favorite-numbers/`

## BFF · fayda (4)

- `/api/ooredoo-bff/fayda/carousels`
- `/api/ooredoo-bff/fayda/categories`
- `/api/ooredoo-bff/fayda/partners/`
- `/api/ooredoo-bff/fayda/use-offer/`

## BFF · flarie (1)

- `/api/ooredoo-bff/flarie/player/token`

## BFF · fusion (1)

- `/api/ooredoo-bff/fusion/eligibility`

## BFF · gamification (5)

- `/api/ooredoo-bff/gamification/history`
- `/api/ooredoo-bff/gamification/play`
- `/api/ooredoo-bff/gamification/power-snake`
- `/api/ooredoo-bff/gamification/power-snake/`
- `/api/ooredoo-bff/gamification/status`

## BFF · history (1)

- `/api/ooredoo-bff/history`

## BFF · ipg (1)

- `/api/ooredoo-bff/ipg/init`

## BFF · islamiyat (14)

- `/api/ooredoo-bff/islamiyat/adhkar`
- `/api/ooredoo-bff/islamiyat/advice-of-the-day`
- `/api/ooredoo-bff/islamiyat/douaa-of-the-day`
- `/api/ooredoo-bff/islamiyat/favorites`
- `/api/ooredoo-bff/islamiyat/get-app-details`
- `/api/ooredoo-bff/islamiyat/hadith-of-the-day`
- `/api/ooredoo-bff/islamiyat/hijri-date`
- `/api/ooredoo-bff/islamiyat/play-surat`
- `/api/ooredoo-bff/islamiyat/preview-reciter`
- `/api/ooredoo-bff/islamiyat/prophet-of-the-day`
- `/api/ooredoo-bff/islamiyat/reciters`
- `/api/ooredoo-bff/islamiyat/set-favourite`
- `/api/ooredoo-bff/islamiyat/surat-of-the-day`
- `/api/ooredoo-bff/islamiyat/surats`

## BFF · migration (6)

- `/api/ooredoo-bff/migration/change-bearing`
- `/api/ooredoo-bff/migration/eligible-offers`
- `/api/ooredoo-bff/migration/energy`
- `/api/ooredoo-bff/migration/otp/request`
- `/api/ooredoo-bff/migration/v2/changeContractOffer`
- `/api/ooredoo-bff/migration/v2/status`

## BFF · non (4)

- `/api/ooredoo-bff/nonEligible/getUser`
- `/api/ooredoo-bff/nonEligible/prayertimes`
- `/api/ooredoo-bff/nonEligible/v2/anaflix/getContent`
- `/api/ooredoo-bff/nonEligible/weather/getWeatherCondition`

## BFF · noudjoum (5)

- `/api/ooredoo-bff/noudjoum/balance`
- `/api/ooredoo-bff/noudjoum/catalog`
- `/api/ooredoo-bff/noudjoum/enroll`
- `/api/ooredoo-bff/noudjoum/get_allocations`
- `/api/ooredoo-bff/noudjoum/redeem`

## BFF · plan (8)

- `/api/ooredoo-bff/plan/data-share-pro/shared-data`
- `/api/ooredoo-bff/plan/data-sharing/action`
- `/api/ooredoo-bff/plan/laGold/activateMode`
- `/api/ooredoo-bff/plan/laSwitch/disableDataSharing`
- `/api/ooredoo-bff/plan/laSwitch/enableDataSharing`
- `/api/ooredoo-bff/plan/laSwitch/limitDataSharing`
- `/api/ooredoo-bff/plan/laSwitch/sharedData`
- `/api/ooredoo-bff/plan/pntpp/sharedData`

## BFF · prayertimes (2)

- `/api/ooredoo-bff/prayertimes/`
- `/api/ooredoo-bff/prayertimes/v2`

## BFF · public (4)

- `/api/ooredoo-bff/public/anaflix/getContent`
- `/api/ooredoo-bff/public/anaflix/play`
- `/api/ooredoo-bff/public/prayertimes`
- `/api/ooredoo-bff/public/weather/getWeatherCondition`

## BFF · quiz (6)

- `/api/ooredoo-bff/quiz/optout`
- `/api/ooredoo-bff/quiz/profile`
- `/api/ooredoo-bff/quiz/profile/game`
- `/api/ooredoo-bff/quiz/profile/reply`
- `/api/ooredoo-bff/quiz/profile/update`
- `/api/ooredoo-bff/quiz/singleclicklogin`

## BFF · raffle-draw (2)

- `/api/ooredoo-bff/raffle-draw/eligibility`
- `/api/ooredoo-bff/raffle-draw/register`

## BFF · ramadan (5)

- `/api/ooredoo-bff/ramadan/activate`
- `/api/ooredoo-bff/ramadan/getAccountInfo`
- `/api/ooredoo-bff/ramadan/getPlanAllocation`
- `/api/ooredoo-bff/ramadan/purchases`
- `/api/ooredoo-bff/ramadan/validity`

## BFF · renewal (1)

- `/api/ooredoo-bff/renewal/getAutoRenewalStatus`

## BFF · rise (5)

- `/api/ooredoo-bff/rise/data/transfer`
- `/api/ooredoo-bff/rise/delete-msisdn`
- `/api/ooredoo-bff/rise/favourites`
- `/api/ooredoo-bff/rise/transfer-history`
- `/api/ooredoo-bff/rise/transfer-quota-values`

## BFF · scholar (1)

- `/api/ooredoo-bff/scholar/eligibility`

## BFF · snap-chat (2)

- `/api/ooredoo-bff/snap-chat/apply`
- `/api/ooredoo-bff/snap-chat/eligibility`

## BFF · soccer (2)

- `/api/ooredoo-bff/soccer/activate`
- `/api/ooredoo-bff/soccer/eligibility-check`

## BFF · sport (4)

- `/api/ooredoo-bff/sport/wc2026/checkElgibility`
- `/api/ooredoo-bff/sport/wc2026/getClubsByCompetition`
- `/api/ooredoo-bff/sport/wc2026/getFavoriteClubs`
- `/api/ooredoo-bff/sport/wc2026/serviceActivation`

## BFF · subscriptions (1)

- `/api/ooredoo-bff/subscriptions/getAccountInfo`

## BFF · transfer (1)

- `/api/ooredoo-bff/transfer/data`

## BFF · user (5)

- `/api/ooredoo-bff/userInfo`
- `/api/ooredoo-bff/userInfo/getContract`
- `/api/ooredoo-bff/userInfo/getCustomerTickets`
- `/api/ooredoo-bff/userInfo/personal`
- `/api/ooredoo-bff/userInfo/rise`

## BFF · user-info (1)

- `/api/ooredoo-bff/user-info/willaya`

## BFF · weather (1)

- `/api/ooredoo-bff/weather/getWeatherCondition`

## BFF · yooz (6)

- `/api/ooredoo-bff/yooz/reservation/msisdn/pickup`
- `/api/ooredoo-bff/yooz/reservation/msisdn/prefix`
- `/api/ooredoo-bff/yooz/reservation/msisdn/reserve`
- `/api/ooredoo-bff/yooz/reservation/msisdn/validate`
- `/api/ooredoo-bff/yooz/reservation/pickup/details`
- `/api/ooredoo-bff/yooz/reservation/token`

## Direct /api (non-BFF) (14)

- `/api/app-updates`
- `/api/communes`
- `/api/countries`
- `/api/faqs`
- `/api/haya-recharge-modes`
- `/api/migration-promoted-offers`
- `/api/product-offerings`
- `/api/product-offerings6`
- `/api/soccer-clubsN`
- `/api/startup-zones`
- `/api/stores`
- `/api/stores/nearby`
- `/api/ui-labels`
- `/api/wilayas`

## Keycloak IdP (auth) (3)

- `/api/auth/realms/myooredoo/protocol/openid-connect/logout`
- `/api/auth/realms/myooredoo/protocol/openid-connect/token`
- `/api/auth/realms/myooredoo/protocol/openid-connect/userinfo`
