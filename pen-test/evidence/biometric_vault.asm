// ===== work/base/classes4.dex :: Lcom/arimaclanka/arimac_flutter_vault/BiometricVault; extends Lcom/arimaclanka/arimac_flutter_vault/Vault;

--- METHOD <init> (Landroidx/fragment/app/FragmentActivity;)V ---
  sget-object v0, Lcom/arimaclanka/arimac_flutter_vault/VaultMode;->BIOMETRIC Lcom/arimaclanka/arimac_flutter_vault/VaultMode;
  invoke-direct v1, v0, Lcom/arimaclanka/arimac_flutter_vault/Vault;-><init>(Lcom/arimaclanka/arimac_flutter_vault/VaultMode;)V
  if-eqz v2, +008h
  iput-object v2, v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->activity Landroidx/fragment/app/FragmentActivity;
  invoke-direct v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->initialize()V
  return-void 
  new-instance v2, Ljava/lang/IllegalStateException;
  const-string v0, "Provided activity is null"
  invoke-direct v2, v0, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V
  throw v2

--- METHOD getBiometricStatus ()I ---
  iget-object v0, v2, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->activity Landroidx/fragment/app/FragmentActivity;
  invoke-virtual v0, Landroidx/fragment/app/FragmentActivity;->getApplicationContext()Landroid/content/Context;
  move-result-object v0
  invoke-static v0, Landroidx/biometric/BiometricManager;->from(Landroid/content/Context;)Landroidx/biometric/BiometricManager;
  move-result-object v0
  const/16 v1, 15
  invoke-virtual v0, v1, Landroidx/biometric/BiometricManager;->canAuthenticate(I)I
  move-result v0
  return v0

--- METHOD getCipher (I)Ljavax/crypto/Cipher; ---
  const-string v0, "AES/CBC/PKCS7Padding"
  invoke-static v0, Ljavax/crypto/Cipher;->getInstance(Ljava/lang/String;)Ljavax/crypto/Cipher;
  move-result-object v0
  const/4 v1, 1
  if-ne v4, v1, +00ah
  invoke-direct v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getSecretKey()Ljavax/crypto/SecretKey;
  move-result-object v1
  invoke-virtual v0, v4, v1, Ljavax/crypto/Cipher;->init(I Ljava/security/Key;)V
  return-object v0
  const-string/jumbo v1, value3
  invoke-direct v3, v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getValue(Ljava/lang/String;)Ljava/lang/String;
  move-result-object v1
  const/4 v2, 0
  invoke-static v1, v2, Landroid/util/Base64;->decode(Ljava/lang/String; I)[B
  move-result-object v1
  new-instance v2, Ljavax/crypto/spec/IvParameterSpec;
  invoke-direct v2, v1, Ljavax/crypto/spec/IvParameterSpec;-><init>([B)V
  invoke-direct v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getSecretKey()Ljavax/crypto/SecretKey;
  move-result-object v1
  invoke-virtual v0, v4, v1, v2, Ljavax/crypto/Cipher;->init(I Ljava/security/Key; Ljava/security/spec/AlgorithmParameterSpec;)V
  return-object v0

--- METHOD getPref ()Landroid/content/SharedPreferences; ---
  iget-object v0, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->activity Landroidx/fragment/app/FragmentActivity;
  invoke-virtual v0, Landroidx/fragment/app/FragmentActivity;->getApplicationContext()Landroid/content/Context;
  move-result-object v0
  const-string v1, "com.arimaclanka.flutter.vault.biometric"
  const/4 v2, 0
  invoke-virtual v0, v1, v2, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String; I)Landroid/content/SharedPreferences;
  move-result-object v0
  return-object v0

--- METHOD getSecretKey ()Ljavax/crypto/SecretKey; ---
  iget-object v0, v4, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->keyStore Ljava/security/KeyStore;
  const/4 v1, 0
  invoke-virtual v0, v1, Ljava/security/KeyStore;->load(Ljava/security/KeyStore$LoadStoreParameter;)V
  iget-object v0, v4, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->keyStore Ljava/security/KeyStore;
  const-string/jumbo v2, vault_biometric_value1
  invoke-virtual v0, v2, v1, Ljava/security/KeyStore;->getKey(Ljava/lang/String; [C)Ljava/security/Key;
  move-result-object v0
  check-cast v0, Ljavax/crypto/SecretKey;
  if-eqz v0, +003h
  return-object v0
  const-string v0, "AES"
  const-string v1, "AndroidKeyStore"
  invoke-static v0, v1, Ljavax/crypto/KeyGenerator;->getInstance(Ljava/lang/String; Ljava/lang/String;)Ljavax/crypto/KeyGenerator;
  move-result-object v0
  new-instance v1, Landroid/security/keystore/KeyGenParameterSpec$Builder;
  const/4 v3, 3
  invoke-direct v1, v2, v3, Landroid/security/keystore/KeyGenParameterSpec$Builder;-><init>(Ljava/lang/String; I)V
  const-string v2, "CBC"
  filled-new-array v2, [Ljava/lang/String;
  move-result-object v2
  invoke-virtual v1, v2, Landroid/security/keystore/KeyGenParameterSpec$Builder;->setBlockModes([Ljava/lang/String;)Landroid/security/keystore/KeyGenParameterSpec$Builder;
  move-result-object v1
  const/4 v2, 1
  invoke-virtual v1, v2, Landroid/security/keystore/KeyGenParameterSpec$Builder;->setUserAuthenticationRequired(Z)Landroid/security/keystore/KeyGenParameterSpec$Builder;
  move-result-object v1
  const-string v2, "PKCS7Padding"
  filled-new-array v2, [Ljava/lang/String;
  move-result-object v2
  invoke-virtual v1, v2, Landroid/security/keystore/KeyGenParameterSpec$Builder;->setEncryptionPaddings([Ljava/lang/String;)Landroid/security/keystore/KeyGenParameterSpec$Builder;
  move-result-object v1
  invoke-virtual v1, Landroid/security/keystore/KeyGenParameterSpec$Builder;->build()Landroid/security/keystore/KeyGenParameterSpec;
  move-result-object v1
  invoke-virtual v0, v1, Ljavax/crypto/KeyGenerator;->init(Ljava/security/spec/AlgorithmParameterSpec;)V
  invoke-virtual v0, Ljavax/crypto/KeyGenerator;->generateKey()Ljavax/crypto/SecretKey;
  move-result-object v0
  return-object v0

--- METHOD getValue (Ljava/lang/String;)Ljava/lang/String; ---
  invoke-direct v2, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getPref()Landroid/content/SharedPreferences;
  move-result-object v0
  const-string v1, ""
  invoke-interface v0, v3, v1, Landroid/content/SharedPreferences;->getString(Ljava/lang/String; Ljava/lang/String;)Ljava/lang/String;
  move-result-object v3
  return-object v3

--- METHOD initialize ()V ---
  new-instance v0, Lcom/arimaclanka/arimac_flutter_vault/EncryptDecryptHelper;
  invoke-direct v0, Lcom/arimaclanka/arimac_flutter_vault/EncryptDecryptHelper;-><init>()V
  iput-object v0, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->encryptDecryptHelper Lcom/arimaclanka/arimac_flutter_vault/EncryptDecryptHelper;
  const-string v0, "AndroidKeyStore"
  invoke-static v0, Ljava/security/KeyStore;->getInstance(Ljava/lang/String;)Ljava/security/KeyStore;
  move-result-object v0
  iput-object v0, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->keyStore Ljava/security/KeyStore;
  return-void 
  move-exception v0
  new-instance v1, Ljava/lang/RuntimeException;
  const-string v2, "Failed to get an instance of KeyStore"
  invoke-direct v1, v2, v0, Ljava/lang/RuntimeException;-><init>(Ljava/lang/String; Ljava/lang/Throwable;)V
  throw v1

--- METHOD isBiometricsReady (Lcom/arimaclanka/arimac_flutter_vault/AuthCallback;)Z ---
  invoke-direct v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getBiometricStatus()I
  move-result v0
  const/4 v1, -2
  if-eq v0, v1, +056h
  const/4 v1, -1
  if-eq v0, v1, +062h
  const/4 v1, 1
  if-eqz v0, +04fh
  const-string v2, "Biometric features unavailable"
  if-eq v0, v1, +03dh
  const/16 v1, 11
  if-eq v0, v1, +029h
  const/16 v1, 12
  if-eq v0, v1, +015h
  const/16 v1, 15
  if-eq v0, v1, +003h
  goto +5ch
  if-eqz v4, +03dh
  iget-object v0, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->vaultMode Lcom/arimaclanka/arimac_flutter_vault/VaultMode;
  invoke-virtual v0, Lcom/arimaclanka/arimac_flutter_vault/VaultMode;->name()Ljava/lang/String;
  move-result-object v0
  sget-object v1, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_NOT_SUPPORTED Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  invoke-interface v4, v0, v1, v2, Lcom/arimaclanka/arimac_flutter_vault/AuthCallback;->onAuthenticationError(Ljava/lang/String; Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  goto +30h
  if-eqz v4, +04dh
  iget-object v0, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->vaultMode Lcom/arimaclanka/arimac_flutter_vault/VaultMode;
  invoke-virtual v0, Lcom/arimaclanka/arimac_flutter_vault/VaultMode;->name()Ljava/lang/String;
  move-result-object v0
  sget-object v1, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_NOT_SUPPORTED Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  const-string v2, "No biometric features available on this device."
  invoke-interface v4, v0, v1, v2, Lcom/arimaclanka/arimac_flutter_vault/AuthCallback;->onAuthenticationError(Ljava/lang/String; Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  goto +3eh
  if-eqz v4, +03dh
  iget-object v0, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->vaultMode Lcom/arimaclanka/arimac_flutter_vault/VaultMode;
  invoke-virtual v0, Lcom/arimaclanka/arimac_flutter_vault/VaultMode;->name()Ljava/lang/String;
  move-result-object v0
  sget-object v1, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_NOT_SUPPORTED Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  const-string v2, "Biometric not enrolled"
  invoke-interface v4, v0, v1, v2, Lcom/arimaclanka/arimac_flutter_vault/AuthCallback;->onAuthenticationError(Ljava/lang/String; Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  goto +2eh
  if-eqz v4, +02dh
  iget-object v0, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->vaultMode Lcom/arimaclanka/arimac_flutter_vault/VaultMode;
  invoke-virtual v0, Lcom/arimaclanka/arimac_flutter_vault/VaultMode;->name()Ljava/lang/String;
  move-result-object v0
  sget-object v1, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_NOT_SUPPORTED Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  invoke-interface v4, v0, v1, v2, Lcom/arimaclanka/arimac_flutter_vault/AuthCallback;->onAuthenticationError(Ljava/lang/String; Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  goto +20h
  return v1
  if-eqz v4, +00fh
  iget-object v0, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->vaultMode Lcom/arimaclanka/arimac_flutter_vault/VaultMode;
  invoke-virtual v0, Lcom/arimaclanka/arimac_flutter_vault/VaultMode;->name()Ljava/lang/String;
  move-result-object v0
  sget-object v1, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_NOT_SUPPORTED Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  const-string v2, "Biometric features not supported"
  invoke-interface v4, v0, v1, v2, Lcom/arimaclanka/arimac_flutter_vault/AuthCallback;->onAuthenticationError(Ljava/lang/String; Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  if-eqz v4, +00fh
  iget-object v0, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->vaultMode Lcom/arimaclanka/arimac_flutter_vault/VaultMode;
  invoke-virtual v0, Lcom/arimaclanka/arimac_flutter_vault/VaultMode;->name()Ljava/lang/String;
  move-result-object v0
  sget-object v1, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_NOT_SUPPORTED Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  const-string v2, "Biometric status unknown"
  invoke-interface v4, v0, v1, v2, Lcom/arimaclanka/arimac_flutter_vault/AuthCallback;->onAuthenticationError(Ljava/lang/String; Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  const/4 v4, 0
  return v4

--- METHOD setValue (Ljava/lang/String; Ljava/lang/String;)V ---
  invoke-direct v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getPref()Landroid/content/SharedPreferences;
  move-result-object v0
  invoke-interface v0, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;
  move-result-object v0
  invoke-interface v0, v2, v3, Landroid/content/SharedPreferences$Editor;->putString(Ljava/lang/String; Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;
  move-result-object v2
  invoke-interface v2, Landroid/content/SharedPreferences$Editor;->apply()V
  return-void 

--- METHOD authenticate (Lcom/arimaclanka/arimac_flutter_vault/AuthCallback;)V ---
  invoke-direct v4, v5, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->isBiometricsReady(Lcom/arimaclanka/arimac_flutter_vault/AuthCallback;)Z
  move-result v0
  if-eqz v0, +061h
  new-instance v0, Landroidx/biometric/BiometricPrompt;
  iget-object v1, v4, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->activity Landroidx/fragment/app/FragmentActivity;
  new-instance v2, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault$1;
  invoke-direct v2, v4, v5, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault$1;-><init>(Lcom/arimaclanka/arimac_flutter_vault/BiometricVault; Lcom/arimaclanka/arimac_flutter_vault/AuthCallback;)V
  invoke-direct v0, v1, v2, Landroidx/biometric/BiometricPrompt;-><init>(Landroidx/fragment/app/FragmentActivity; Landroidx/biometric/BiometricPrompt$AuthenticationCallback;)V
  iget-object v1, v4, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->biometricPromptInfo Landroidx/biometric/BiometricPrompt$PromptInfo;
  if-nez v1, +012h
  if-eqz v5, +04fh
  iget-object v0, v4, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->vaultMode Lcom/arimaclanka/arimac_flutter_vault/VaultMode;
  invoke-virtual v0, Lcom/arimaclanka/arimac_flutter_vault/VaultMode;->name()Ljava/lang/String;
  move-result-object v0
  sget-object v1, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_PROMPT_NOT_CONFIGURED Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  const-string v2, "Android prompt info not configured"
  invoke-interface v5, v0, v1, v2, Lcom/arimaclanka/arimac_flutter_vault/AuthCallback;->onAuthenticationError(Ljava/lang/String; Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  return-void 
  const-string/jumbo v1, value2
  invoke-direct v4, v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getValue(Ljava/lang/String;)Ljava/lang/String;
  move-result-object v1
  invoke-virtual v1, Ljava/lang/String;->isEmpty()Z
  move-result v1
  if-eqz v1, +012h
  iget-object v1, v4, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->biometricPromptInfo Landroidx/biometric/BiometricPrompt$PromptInfo;
  new-instance v2, Landroidx/biometric/BiometricPrompt$CryptoObject;
  const/4 v3, 1
  invoke-direct v4, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getCipher(I)Ljavax/crypto/Cipher;
  move-result-object v3
  invoke-direct v2, v3, Landroidx/biometric/BiometricPrompt$CryptoObject;-><init>(Ljavax/crypto/Cipher;)V
  invoke-virtual v0, v1, v2, Landroidx/biometric/BiometricPrompt;->authenticate(Landroidx/biometric/BiometricPrompt$PromptInfo; Landroidx/biometric/BiometricPrompt$CryptoObject;)V
  return-void 
  iget-object v1, v4, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->biometricPromptInfo Landroidx/biometric/BiometricPrompt$PromptInfo;
  new-instance v2, Landroidx/biometric/BiometricPrompt$CryptoObject;
  const/4 v3, 2
  invoke-direct v4, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getCipher(I)Ljavax/crypto/Cipher;
  move-result-object v3
  invoke-direct v2, v3, Landroidx/biometric/BiometricPrompt$CryptoObject;-><init>(Ljavax/crypto/Cipher;)V
  invoke-virtual v0, v1, v2, Landroidx/biometric/BiometricPrompt;->authenticate(Landroidx/biometric/BiometricPrompt$PromptInfo; Landroidx/biometric/BiometricPrompt$CryptoObject;)V
  return-void 
  move-exception v0
  if-eqz v5, +011h
  iget-object v1, v4, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->vaultMode Lcom/arimaclanka/arimac_flutter_vault/VaultMode;
  invoke-virtual v1, Lcom/arimaclanka/arimac_flutter_vault/VaultMode;->name()Ljava/lang/String;
  move-result-object v1
  sget-object v2, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_AUTH_ERROR Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  invoke-virtual v0, Ljava/lang/Exception;->getMessage()Ljava/lang/String;
  move-result-object v0
  invoke-interface v5, v1, v2, v0, Lcom/arimaclanka/arimac_flutter_vault/AuthCallback;->onAuthenticationError(Ljava/lang/String; Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  return-void 

--- METHOD clearData ()V ---
  const-string/jumbo v0, value2
  const-string v1, ""
  invoke-direct v2, v0, v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->setValue(Ljava/lang/String; Ljava/lang/String;)V
  const-string/jumbo v0, value3
  invoke-direct v2, v0, v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->setValue(Ljava/lang/String; Ljava/lang/String;)V
  const-string/jumbo v0, value1
  invoke-direct v2, v0, v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->setValue(Ljava/lang/String; Ljava/lang/String;)V
  return-void 

--- METHOD closeVault ()Z ---
  const/4 v0, 0
  iput-object v0, v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->encryptionKey [B
  const/4 v0, 1
  return v0

--- METHOD getBiometricState ()Lcom/arimaclanka/arimac_flutter_vault/VaultError; ---
  invoke-direct v2, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getBiometricStatus()I
  move-result v0
  const/4 v1, -2
  if-eq v0, v1, +026h
  const/4 v1, -1
  if-eq v0, v1, +020h
  const/4 v1, 1
  if-eq v0, v1, +01ah
  const/16 v1, 15
  if-eq v0, v1, +013h
  const/16 v1, 11
  if-eq v0, v1, +00ch
  const/16 v1, 12
  if-eq v0, v1, +005h
  sget-object v0, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->NONE Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  return-object v0
  sget-object v0, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_NOT_SUPPORTED Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  return-object v0
  sget-object v0, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_NOT_AVAILABLE Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  return-object v0
  sget-object v0, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_NOT_SUPPORTED Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  return-object v0
  sget-object v0, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_NOT_SUPPORTED Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  return-object v0
  sget-object v0, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_NOT_SUPPORTED Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  return-object v0
  sget-object v0, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->BIOMETRIC_NOT_SUPPORTED Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  return-object v0

--- METHOD isDataAvailable ()Z ---
  const-string/jumbo v0, value1
  invoke-direct v1, v0, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getValue(Ljava/lang/String;)Ljava/lang/String;
  move-result-object v0
  if-eqz v0, +00ah
  invoke-virtual v0, Ljava/lang/String;->isEmpty()Z
  move-result v0
  if-nez v0, +004h
  const/4 v0, 1
  return v0
  const/4 v0, 0
  return v0

--- METHOD isEnabled ()Z ---
  invoke-virtual v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->isSupported()Z
  move-result v0
  if-eqz v0, +00ah
  invoke-virtual v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->isDataAvailable()Z
  move-result v0
  if-eqz v0, +004h
  const/4 v0, 1
  return v0
  const/4 v0, 0
  return v0

--- METHOD isOpen ()Z ---
  iget-object v0, v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->encryptionKey [B
  if-eqz v0, +004h
  const/4 v0, 1
  return v0
  const/4 v0, 0
  return v0

--- METHOD isSecretKeyAuthenticationRequired ()Z ---
  invoke-direct v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getSecretKey()Ljavax/crypto/SecretKey;
  move-result-object v0
  invoke-interface v0, Ljavax/crypto/SecretKey;->getAlgorithm()Ljava/lang/String;
  move-result-object v1
  const-string v2, "AndroidKeyStore"
  invoke-static v1, v2, Ljavax/crypto/SecretKeyFactory;->getInstance(Ljava/lang/String; Ljava/lang/String;)Ljavax/crypto/SecretKeyFactory;
  move-result-object v1
  const-class v2, Landroid/security/keystore/KeyInfo;
  invoke-virtual v1, v0, v2, Ljavax/crypto/SecretKeyFactory;->getKeySpec(Ljavax/crypto/SecretKey; Ljava/lang/Class;)Ljava/security/spec/KeySpec;
  move-result-object v0
  check-cast v0, Landroid/security/keystore/KeyInfo;
  invoke-virtual v0, Landroid/security/keystore/KeyInfo;->isUserAuthenticationRequired()Z
  move-result v0
  return v0
  move-exception v0
  new-instance v1, Lcom/arimaclanka/arimac_flutter_vault/VaultException;
  sget-object v2, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->SECRET_KEY_ERROR Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  invoke-virtual v0, Ljava/lang/Exception;->getMessage()Ljava/lang/String;
  move-result-object v0
  invoke-direct v1, v2, v0, Lcom/arimaclanka/arimac_flutter_vault/VaultException;-><init>(Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  throw v1

--- METHOD isSupported ()Z ---
  invoke-direct v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getBiometricStatus()I
  move-result v0
  if-nez v0, +004h
  const/4 v0, 1
  return v0
  const/4 v0, 0
  return v0

--- METHOD openVault (Lcom/arimaclanka/arimac_flutter_vault/VaultCallback;)V ---
  invoke-virtual v2, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->isSecretKeyAuthenticationRequired()Z
  move-result v0
  if-eqz v0, +015h
  new-instance v0, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault$2;
  invoke-direct v0, v2, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault$2;-><init>(Lcom/arimaclanka/arimac_flutter_vault/BiometricVault; Lcom/arimaclanka/arimac_flutter_vault/VaultCallback;)V
  invoke-virtual v2, v0, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->authenticate(Lcom/arimaclanka/arimac_flutter_vault/AuthCallback;)V
  return-void 
  move-exception v0
  sget-object v1, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->VAULT_OPENING_ERROR Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  invoke-virtual v0, Ljava/lang/Exception;->getMessage()Ljava/lang/String;
  move-result-object v0
  invoke-interface v3, v1, v0, Lcom/arimaclanka/arimac_flutter_vault/VaultCallback;->onVaultError(Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  return-void 

--- METHOD openVaultActual (Ljavax/crypto/Cipher; Lcom/arimaclanka/arimac_flutter_vault/VaultCallback;)V ---
  const-string/jumbo v0, value2
  invoke-direct v4, v0, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getValue(Ljava/lang/String;)Ljava/lang/String;
  move-result-object v1
  invoke-virtual v1, Ljava/lang/String;->isEmpty()Z
  move-result v2
  const/4 v3, 0
  if-eqz v2, +032h
  iget-object v1, v4, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->encryptDecryptHelper Lcom/arimaclanka/arimac_flutter_vault/EncryptDecryptHelper;
  invoke-virtual v1, Lcom/arimaclanka/arimac_flutter_vault/EncryptDecryptHelper;->generateKey()[B
  move-result-object v1
  iput-object v1, v4, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->encryptionKey [B
  iget-object v1, v4, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->encryptionKey [B
  invoke-virtual v5, v1, Ljavax/crypto/Cipher;->doFinal([B)[B
  move-result-object v1
  invoke-virtual v5, Ljavax/crypto/Cipher;->getParameters()Ljava/security/AlgorithmParameters;
  move-result-object v5
  const-class v2, Ljavax/crypto/spec/IvParameterSpec;
  invoke-virtual v5, v2, Ljava/security/AlgorithmParameters;->getParameterSpec(Ljava/lang/Class;)Ljava/security/spec/AlgorithmParameterSpec;
  move-result-object v5
  check-cast v5, Ljavax/crypto/spec/IvParameterSpec;
  invoke-virtual v5, Ljavax/crypto/spec/IvParameterSpec;->getIV()[B
  move-result-object v5
  invoke-static v5, v3, Landroid/util/Base64;->encodeToString([B I)Ljava/lang/String;
  move-result-object v5
  invoke-static v1, v3, Landroid/util/Base64;->encodeToString([B I)Ljava/lang/String;
  move-result-object v1
  invoke-direct v4, v0, v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->setValue(Ljava/lang/String; Ljava/lang/String;)V
  const-string/jumbo v0, value3
  invoke-direct v4, v0, v5, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->setValue(Ljava/lang/String; Ljava/lang/String;)V
  goto +bh
  invoke-static v1, v3, Landroid/util/Base64;->decode(Ljava/lang/String; I)[B
  move-result-object v0
  invoke-virtual v5, v0, Ljavax/crypto/Cipher;->doFinal([B)[B
  move-result-object v5
  iput-object v5, v4, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->encryptionKey [B
  iget-object v5, v4, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->vaultMode Lcom/arimaclanka/arimac_flutter_vault/VaultMode;
  invoke-virtual v5, Lcom/arimaclanka/arimac_flutter_vault/VaultMode;->name()Ljava/lang/String;
  move-result-object v5
  invoke-interface v6, v5, Lcom/arimaclanka/arimac_flutter_vault/VaultCallback;->onVaultOpen(Ljava/lang/String;)V
  return-void 
  move-exception v5
  sget-object v0, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->VAULT_OPENING_ERROR Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  invoke-virtual v5, Ljava/lang/Exception;->getMessage()Ljava/lang/String;
  move-result-object v5
  invoke-interface v6, v0, v5, Lcom/arimaclanka/arimac_flutter_vault/VaultCallback;->onVaultError(Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  return-void 

--- METHOD requestEnroll (Landroid/app/Activity; I)V ---
  if-eqz v4, +014h
  new-instance v0, Landroid/content/Intent;
  const-string v1, "android.settings.BIOMETRIC_ENROLL"
  invoke-direct v0, v1, Landroid/content/Intent;-><init>(Ljava/lang/String;)V
  const-string v1, "android.provider.extra.BIOMETRIC_AUTHENTICATORS_ALLOWED"
  const v2, 32783
  invoke-virtual v0, v1, v2, Landroid/content/Intent;->putExtra(Ljava/lang/String; I)Landroid/content/Intent;
  invoke-virtual v4, v0, v5, Landroid/app/Activity;->startActivityForResult(Landroid/content/Intent; I)V
  return-void 

--- METHOD retrieveData ()Ljava/lang/String; ---
  invoke-virtual v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->isOpen()Z
  move-result v0
  if-eqz v0, +028h
  const-string/jumbo v0, value1
  invoke-direct v3, v0, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->getValue(Ljava/lang/String;)Ljava/lang/String;
  move-result-object v0
  const/4 v1, 0
  invoke-static v0, v1, Landroid/util/Base64;->decode(Ljava/lang/String; I)[B
  move-result-object v0
  iget-object v1, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->encryptDecryptHelper Lcom/arimaclanka/arimac_flutter_vault/EncryptDecryptHelper;
  iget-object v2, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->encryptionKey [B
  invoke-virtual v1, v2, Lcom/arimaclanka/arimac_flutter_vault/EncryptDecryptHelper;->getSecretKey([B)Ljavax/crypto/SecretKey;
  move-result-object v2
  invoke-virtual v1, v0, v2, Lcom/arimaclanka/arimac_flutter_vault/EncryptDecryptHelper;->decrypt([B Ljavax/crypto/SecretKey;)Ljava/lang/String;
  move-result-object v0
  return-object v0
  move-exception v0
  new-instance v1, Lcom/arimaclanka/arimac_flutter_vault/VaultException;
  sget-object v2, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->VAULT_RETRIEVE_ERROR Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  invoke-virtual v0, Ljava/lang/Exception;->getMessage()Ljava/lang/String;
  move-result-object v0
  invoke-direct v1, v2, v0, Lcom/arimaclanka/arimac_flutter_vault/VaultException;-><init>(Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  throw v1
  new-instance v0, Lcom/arimaclanka/arimac_flutter_vault/VaultException;
  sget-object v1, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->VAULT_NOT_OPEN Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  const-string v2, "Vault should be in open state to retrieve data"
  invoke-direct v0, v1, v2, Lcom/arimaclanka/arimac_flutter_vault/VaultException;-><init>(Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  throw v0

--- METHOD setBiometricPromptInfo (Ljava/lang/String; Ljava/lang/String; Ljava/lang/String;)V ---
  new-instance v0, Landroidx/biometric/BiometricPrompt$PromptInfo$Builder;
  invoke-direct v0, Landroidx/biometric/BiometricPrompt$PromptInfo$Builder;-><init>()V
  invoke-virtual v0, v2, Landroidx/biometric/BiometricPrompt$PromptInfo$Builder;->setTitle(Ljava/lang/CharSequence;)Landroidx/biometric/BiometricPrompt$PromptInfo$Builder;
  invoke-virtual v0, v3, Landroidx/biometric/BiometricPrompt$PromptInfo$Builder;->setSubtitle(Ljava/lang/CharSequence;)Landroidx/biometric/BiometricPrompt$PromptInfo$Builder;
  invoke-virtual v0, v4, Landroidx/biometric/BiometricPrompt$PromptInfo$Builder;->setNegativeButtonText(Ljava/lang/CharSequence;)Landroidx/biometric/BiometricPrompt$PromptInfo$Builder;
  invoke-virtual v0, Landroidx/biometric/BiometricPrompt$PromptInfo$Builder;->build()Landroidx/biometric/BiometricPrompt$PromptInfo;
  move-result-object v2
  iput-object v2, v1, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->biometricPromptInfo Landroidx/biometric/BiometricPrompt$PromptInfo;
  return-void 

--- METHOD storeData (Ljava/lang/String;)Z ---
  invoke-virtual v2, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->isOpen()Z
  move-result v0
  if-eqz v0, +028h
  iget-object v0, v2, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->encryptDecryptHelper Lcom/arimaclanka/arimac_flutter_vault/EncryptDecryptHelper;
  iget-object v1, v2, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->encryptionKey [B
  invoke-virtual v0, v1, Lcom/arimaclanka/arimac_flutter_vault/EncryptDecryptHelper;->getSecretKey([B)Ljavax/crypto/SecretKey;
  move-result-object v1
  invoke-virtual v0, v3, v1, Lcom/arimaclanka/arimac_flutter_vault/EncryptDecryptHelper;->encrypt(Ljava/lang/String; Ljavax/crypto/SecretKey;)[B
  move-result-object v3
  const-string/jumbo v0, value1
  const/4 v1, 0
  invoke-static v3, v1, Landroid/util/Base64;->encodeToString([B I)Ljava/lang/String;
  move-result-object v3
  invoke-direct v2, v0, v3, Lcom/arimaclanka/arimac_flutter_vault/BiometricVault;->setValue(Ljava/lang/String; Ljava/lang/String;)V
  const/4 v3, 1
  return v3
  move-exception v3
  new-instance v0, Lcom/arimaclanka/arimac_flutter_vault/VaultException;
  sget-object v1, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->VAULT_STORE_ERROR Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  invoke-virtual v3, Ljava/lang/Exception;->getMessage()Ljava/lang/String;
  move-result-object v3
  invoke-direct v0, v1, v3, Lcom/arimaclanka/arimac_flutter_vault/VaultException;-><init>(Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  throw v0
  new-instance v3, Lcom/arimaclanka/arimac_flutter_vault/VaultException;
  sget-object v0, Lcom/arimaclanka/arimac_flutter_vault/VaultError;->VAULT_NOT_OPEN Lcom/arimaclanka/arimac_flutter_vault/VaultError;
  const-string v1, "Vault should be in open state to save data"
  invoke-direct v3, v0, v1, Lcom/arimaclanka/arimac_flutter_vault/VaultException;-><init>(Lcom/arimaclanka/arimac_flutter_vault/VaultError; Ljava/lang/String;)V
  throw v3
