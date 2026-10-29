  static dynamic setAccessToken(String) async {
    // ** addr: 0x95b6c8, size: 0x60
    // 0x95b6c8: EnterFrame
    //     0x95b6c8: stp             fp, lr, [SP, #-0x10]!
    //     0x95b6cc: mov             fp, SP
    // 0x95b6d0: AllocStack(0x18)
    //     0x95b6d0: sub             SP, SP, #0x18
    // 0x95b6d4: SetupParameters(dynamic _ /* r1 => r3, fp-0x10 */)
    //     0x95b6d4: stur            NULL, [fp, #-8]
    //     0x95b6d8: mov             x3, x1
    //     0x95b6dc: stur            x1, [fp, #-0x10]
    // 0x95b6e0: CheckStackOverflow
    //     0x95b6e0: ldr             x16, [THR, #0x48]  ; THR::stack_limit
    //     0x95b6e4: cmp             SP, x16
    //     0x95b6e8: b.ls            #0x95b720
    // 0x95b6ec: InitAsync() -> Future
    //     0x95b6ec: mov             x0, NULL
    //     0x95b6f0: bl              #0x8901ec  ; InitAsyncStub
    // 0x95b6f4: r0 = getInstance()
    //     0x95b6f4: bl              #0x9264d8  ; [package:shared_preferences/src/shared_preferences_legacy.dart] SharedPreferences::getInstance
    // 0x95b6f8: mov             x1, x0
    // 0x95b6fc: stur            x1, [fp, #-0x18]
    // 0x95b700: r0 = Await()
    //     0x95b700: bl              #0x88ffb4  ; AwaitStub
    // 0x95b704: mov             x1, x0
    // 0x95b708: ldur            x3, [fp, #-0x10]
    // 0x95b70c: r2 = "access_token"
    //     0x95b70c: add             x2, PP, #0xa, lsl #12  ; [pp+0xab08] "access_token"
    //     0x95b710: ldr             x2, [x2, #0xb08]
    // 0x95b714: r0 = setString()
    //     0x95b714: bl              #0x95b40c  ; [package:shared_preferences/src/shared_preferences_legacy.dart] SharedPreferences::setString
    // 0x95b718: r0 = Null
    //     0x95b718: mov             x0, NULL
    // 0x95b71c: r0 = ReturnAsyncNotFuture()
    //     0x95b71c: b               #0x88fb70  ; ReturnAsyncNotFutureStub
    // 0x95b720: r0 = StackOverflowSharedWithoutFPURegs()
    //     0x95b720: bl              #0x158dcc0  ; StackOverflowSharedWithoutFPURegsStub
    // 0x95b724: b               #0x95b6ec
  }
  static _ getSlaveRefreshToken(/* No info */) async {
    // ** addr: 0x95cd24, size: 0x5c
    // 0x95cd24: EnterFrame
    //     0x95cd24: stp             fp, lr, [SP, #-0x10]!
    //     0x95cd28: mov             fp, SP
    // 0x95cd2c: AllocStack(0x10)
    //     0x95cd2c: sub             SP, SP, #0x10
    // 0x95cd30: SetupParameters()
    //     0x95cd30: stur            NULL, [fp, #-8]
    // 0x95cd34: CheckStackOverflow
    //     0x95cd34: ldr             x16, [THR, #0x48]  ; THR::stack_limit
    //     0x95cd38: cmp             SP, x16
    //     0x95cd3c: b.ls            #0x95cd78
    // 0x95cd40: InitAsync() -> Future<String?>
    //     0x95cd40: ldr             x0, [PP, #0xd78]  ; [pp+0xd78] TypeArguments: <String?>
    //     0x95cd44: bl              #0x8901ec  ; InitAsyncStub
    // 0x95cd48: r0 = getInstance()
    //     0x95cd48: bl              #0x9264d8  ; [package:shared_preferences/src/shared_preferences_legacy.dart] SharedPreferences::getInstance
    // 0x95cd4c: mov             x1, x0
    // 0x95cd50: stur            x1, [fp, #-0x10]
    // 0x95cd54: r0 = Await()
    //     0x95cd54: bl              #0x88ffb4  ; AwaitStub
    // 0x95cd58: mov             x1, x0
    // 0x95cd5c: r2 = "slave_refresh_token"
    //     0x95cd5c: add             x2, PP, #0x13, lsl #12  ; [pp+0x13258] "slave_refresh_token"
    //     0x95cd60: ldr             x2, [x2, #0x258]
    // 0x95cd64: r0 = getString()
    //     0x95cd64: bl              #0x9261e0  ; [package:shared_preferences/src/shared_preferences_legacy.dart] SharedPreferences::getString
    // 0x95cd68: cmp             w0, NULL
    // 0x95cd6c: b.ne            #0x95cd74
    // 0x95cd70: r0 = ""
    //     0x95cd70: ldr             x0, [PP, #0x8b8]  ; [pp+0x8b8] ""
    // 0x95cd74: r0 = ReturnAsyncNotFuture()
    //     0x95cd74: b               #0x88fb70  ; ReturnAsyncNotFutureStub
    // 0x95cd78: r0 = StackOverflowSharedWithoutFPURegs()
    //     0x95cd78: bl              #0x158dcc0  ; StackOverflowSharedWithoutFPURegsStub
    // 0x95cd7c: b               #0x95cd40
  }
  static _ getRefreshToken(/* No info */) async {
    // ** addr: 0x95cd80, size: 0x5c
    // 0x95cd80: EnterFrame
    //     0x95cd80: stp             fp, lr, [SP, #-0x10]!
    //     0x95cd84: mov             fp, SP
    // 0x95cd88: AllocStack(0x10)
    //     0x95cd88: sub             SP, SP, #0x10
    // 0x95cd8c: SetupParameters()
    //     0x95cd8c: stur            NULL, [fp, #-8]
    // 0x95cd90: CheckStackOverflow
    //     0x95cd90: ldr             x16, [THR, #0x48]  ; THR::stack_limit
    //     0x95cd94: cmp             SP, x16
    //     0x95cd98: b.ls            #0x95cdd4
    // 0x95cd9c: InitAsync() -> Future<String?>
    //     0x95cd9c: ldr             x0, [PP, #0xd78]  ; [pp+0xd78] TypeArguments: <String?>
    //     0x95cda0: bl              #0x8901ec  ; InitAsyncStub
    // 0x95cda4: r0 = getInstance()
    //     0x95cda4: bl              #0x9264d8  ; [package:shared_preferences/src/shared_preferences_legacy.dart] SharedPreferences::getInstance
    // 0x95cda8: mov             x1, x0
    // 0x95cdac: stur            x1, [fp, #-0x10]
    // 0x95cdb0: r0 = Await()
    //     0x95cdb0: bl              #0x88ffb4  ; AwaitStub
    // 0x95cdb4: mov             x1, x0
    // 0x95cdb8: r2 = "refresh_token"
    //     0x95cdb8: add             x2, PP, #0x13, lsl #12  ; [pp+0x13148] "refresh_token"
    //     0x95cdbc: ldr             x2, [x2, #0x148]
    // 0x95cdc0: r0 = getString()
    //     0x95cdc0: bl              #0x9261e0  ; [package:shared_preferences/src/shared_preferences_legacy.dart] SharedPreferences::getString
    // 0x95cdc4: cmp             w0, NULL
    // 0x95cdc8: b.ne            #0x95cdd0
    // 0x95cdcc: r0 = ""
    //     0x95cdcc: ldr             x0, [PP, #0x8b8]  ; [pp+0x8b8] ""
    // 0x95cdd0: r0 = ReturnAsyncNotFuture()
    //     0x95cdd0: b               #0x88fb70  ; ReturnAsyncNotFutureStub
    // 0x95cdd4: r0 = StackOverflowSharedWithoutFPURegs()
    //     0x95cdd4: bl              #0x158dcc0  ; StackOverflowSharedWithoutFPURegsStub
    // 0x95cdd8: b               #0x95cd9c
  }
  static _ getMigrateOTP(/* No info */) async {
    // ** addr: 0x963f70, size: 0x50
    // 0x963f70: EnterFrame
    //     0x963f70: stp             fp, lr, [SP, #-0x10]!
    //     0x963f74: mov             fp, SP
    // 0x963f78: AllocStack(0x10)
    //     0x963f78: sub             SP, SP, #0x10
    // 0x963f7c: SetupParameters()
    //     0x963f7c: stur            NULL, [fp, #-8]
