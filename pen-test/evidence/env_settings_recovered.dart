// lib: , url: package:ooredoo_selfcare_algeria/api/env_settings.dart

// class id: 1050199, size: 0x8
class :: {
}

// class id: 1360, size: 0x14, field offset: 0x8
class EnvironmentData extends Object {
}

// class id: 1361, size: 0x8, field offset: 0x8
abstract class EnvironmentSettings extends Object {

  static _ getCurrentEnv(/* No info */) {
    // ** addr: 0x9260dc, size: 0x68
    // 0x9260dc: EnterFrame
    //     0x9260dc: stp             fp, lr, [SP, #-0x10]!
    //     0x9260e0: mov             fp, SP
    // 0x9260e4: CheckStackOverflow
    //     0x9260e4: ldr             x16, [THR, #0x48]  ; THR::stack_limit
    //     0x9260e8: cmp             SP, x16
    //     0x9260ec: b.ls            #0x92613c
    // 0x9260f0: r0 = LoadStaticField(0xc30)
    //     0x9260f0: ldr             x0, [THR, #0x78]  ; THR::field_table_values
    //     0x9260f4: ldr             x0, [x0, #0x1860]
    // 0x9260f8: ldr             x16, [THR, #0x90]  ; THR::object_sentinel
    // 0x9260fc: cmp             w0, w16
    // 0x926100: b.ne            #0x92610c
    // 0x926104: r2 = env
    //     0x926104: ldr             x2, [PP, #0x7568]  ; [pp+0x7568] Field <::.env>: static late final (offset: 0xc30)
    // 0x926108: r0 = InitLateFinalStaticField()
    //     0x926108: bl              #0x158bc78  ; InitLateFinalStaticFieldStub
    // 0x92610c: r0 = EnvironmentData()
    //     0x92610c: bl              #0x926144  ; AllocateEnvironmentDataStub -> EnvironmentData (size=0x14)
    // 0x926110: r1 = "https://apis.ooredoo.dz"
    //     0x926110: add             x1, PP, #8, lsl #12  ; [pp+0x8a18] "https://apis.ooredoo.dz"
    //     0x926114: ldr             x1, [x1, #0xa18]
    // 0x926118: StoreField: r0->field_7 = r1
    //     0x926118: stur            w1, [x0, #7]
    // 0x92611c: r1 = true
    //     0x92611c: add             x1, NULL, #0x20  ; true
    // 0x926120: StoreField: r0->field_b = r1
    //     0x926120: stur            w1, [x0, #0xb]
    // 0x926124: r1 = "sha256/o6TJ1cdulh3OG+cI3qkjKWp6EUgCvDJfalozcJczjgU="
    //     0x926124: add             x1, PP, #0x13, lsl #12  ; [pp+0x139a8] "sha256/o6TJ1cdulh3OG+cI3qkjKWp6EUgCvDJfalozcJczjgU="
    //     0x926128: ldr             x1, [x1, #0x9a8]
    // 0x92612c: StoreField: r0->field_f = r1
    //     0x92612c: stur            w1, [x0, #0xf]
    // 0x926130: LeaveFrame
    //     0x926130: mov             SP, fp
    //     0x926134: ldp             fp, lr, [SP], #0x10
    // 0x926138: ret
    //     0x926138: ret             
    // 0x92613c: r0 = StackOverflowSharedWithoutFPURegs()
    //     0x92613c: bl              #0x158dcc0  ; StackOverflowSharedWithoutFPURegsStub
    // 0x926140: b               #0x9260f0
  }
}
