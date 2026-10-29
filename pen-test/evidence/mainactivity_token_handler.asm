  move-result v0
  if-nez v0, +004h
  goto/16 +09eh
  invoke-virtual v5, Lcom/example/ooredoo_selfcare_algeria/MainActivity;->getContentResolver()Landroid/content/ContentResolver;
  move-result-object v5
  const-string v6, "adb_enabled"
  invoke-static v5, v6, v4, Landroid/provider/Settings$Secure;->getInt(Landroid/content/ContentResolver; Ljava/lang/String; I)I
  move-result v5
  if-eqz v5, +003h
  goto +2h
  move v3, v4
  invoke-static v3, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
  move-result-object v5
  invoke-interface v7, v5, Lio/flutter/plugin/common/MethodChannel$Result;->success(Ljava/lang/Object;)V
  return-void 
  const-string v0, "isDeveloperModeOn"
  invoke-virtual v1, v0, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
  move-result v0
  if-nez v0, +004h
  goto/16 +07eh
  invoke-virtual v5, Lcom/example/ooredoo_selfcare_algeria/MainActivity;->getContentResolver()Landroid/content/ContentResolver;
  move-result-object v5
  const-string v6, "development_settings_enabled"
  invoke-static v5, v6, v4, Landroid/provider/Settings$Secure;->getInt(Landroid/content/ContentResolver; Ljava/lang/String; I)I
  move-result v5
  if-eqz v5, +003h
  goto +2h
  move v3, v4
  invoke-static v3, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;
  move-result-object v5
  invoke-interface v7, v5, Lio/flutter/plugin/common/MethodChannel$Result;->success(Ljava/lang/Object;)V
  return-void 
  const-string/jumbo v2, token
  invoke-virtual v1, v2, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
  move-result v1
  if-nez v1, +003h
  goto +5dh
  invoke-virtual v5, Lcom/example/ooredoo_selfcare_algeria/MainActivity;->getApplicationContext()Landroid/content/Context;
  move-result-object v6
  invoke-virtual v6, Landroid/content/Context;->getPackageName()Ljava/lang/String;
  move-result-object v6
  new-instance v1, Ljava/lang/StringBuilder;
  const-string/jumbo v2, token requested, package=
  invoke-direct v1, v2, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V
  invoke-virtual v1, v6, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
  invoke-virtual v1, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
  move-result-object v1
  const-string v2, "OALib"
  invoke-static v2, v1, Landroid/util/Log;->d(Ljava/lang/String; Ljava/lang/String;)I
  const-string v1, "com.algeria.selfcare.app.android"
  invoke-static v6, v1, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object; Ljava/lang/Object;)Z
  move-result v6
  if-nez v6, +00dh
  const-string v5, "Non-prod environment detected, returning hardcoded token"
  invoke-static v2, v5, Landroid/util/Log;->d(Ljava/lang/String; Ljava/lang/String;)I
  const-string v5, "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.TEST_TOKEN_DEV"
  invoke-interface v7, v5, Lio/flutter/plugin/common/MethodChannel$Result;->success(Ljava/lang/Object;)V
  return-void 
  new-instance v6, Lcom/algeria/selfcare/app/oalib/OALib;
  invoke-direct v6, Lcom/algeria/selfcare/app/oalib/OALib;-><init>()V
  invoke-virtual v5, Lcom/example/ooredoo_selfcare_algeria/MainActivity;->getApplicationContext()Landroid/content/Context;
  move-result-object v5
  invoke-virtual v6, v5, Lcom/algeria/selfcare/app/oalib/OALib;->generate(Landroid/content/Context;)Ljava/lang/String;
  move-result-object v5
  if-nez v5, +003h
  move-object v5, v0
  invoke-interface v7, v5, Lio/flutter/plugin/common/MethodChannel$Result;->success(Ljava/lang/Object;)V
  return-void 
  move-exception v5
  const-string v6, "Failed to generate token"
  check-cast v5, Ljava/lang/Throwable;
