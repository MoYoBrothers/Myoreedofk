// lib: , url: package:ooredoo_selfcare_algeria/utils/oa_infosec/pubkey_pinning_client.dart

// class id: 1050960, size: 0x8
class :: {
}

// class id: 1861, size: 0xc, field offset: 0xc
class PublicKeyPinningClient extends IOClient {

  static _ create(/* No info */) async {
    // ** addr: 0x91cc4c, size: 0xd4
    // 0x91cc4c: EnterFrame
    //     0x91cc4c: stp             fp, lr, [SP, #-0x10]!
    //     0x91cc50: mov             fp, SP
    // 0x91cc54: AllocStack(0x18)
    //     0x91cc54: sub             SP, SP, #0x18
    // 0x91cc58: SetupParameters()
    //     0x91cc58: stur            NULL, [fp, #-8]
    // 0x91cc5c: CheckStackOverflow
    //     0x91cc5c: ldr             x16, [THR, #0x48]  ; THR::stack_limit
    //     0x91cc60: cmp             SP, x16
    //     0x91cc64: b.ls            #0x91cd18
    // 0x91cc68: InitAsync() -> Future<PublicKeyPinningClient>
    //     0x91cc68: add             x0, PP, #0x13, lsl #12  ; [pp+0x135c8] TypeArguments: <PublicKeyPinningClient>
    //     0x91cc6c: ldr             x0, [x0, #0x5c8]
    //     0x91cc70: bl              #0x8901ec  ; InitAsyncStub
    // 0x91cc74: r0 = getCurrentEnv()
    //     0x91cc74: bl              #0x9260dc  ; [package:ooredoo_selfcare_algeria/api/env_settings.dart] EnvironmentSettings::getCurrentEnv
    // 0x91cc78: LoadField: r1 = r0->field_f
    //     0x91cc78: ldur            w1, [x0, #0xf]
    // 0x91cc7c: DecompressPointer r1
    //     0x91cc7c: add             x1, x1, HEAP, lsl #32
    // 0x91cc80: stur            x1, [fp, #-0x10]
    // 0x91cc84: r1 = 1
    //     0x91cc84: mov             x1, #1
    // 0x91cc88: r0 = AllocateContext()
    //     0x91cc88: bl              #0x158cac4  ; AllocateContextStub
    // 0x91cc8c: mov             x1, x0
    // 0x91cc90: ldur            x0, [fp, #-0x10]
    // 0x91cc94: stur            x1, [fp, #-0x18]
    // 0x91cc98: StoreField: r1->field_f = r0
    //     0x91cc98: stur            w0, [x1, #0xf]
    // 0x91cc9c: r0 = LoadStaticField(0x444)
    //     0x91cc9c: ldr             x0, [THR, #0x78]  ; THR::field_table_values
    //     0x91cca0: ldr             x0, [x0, #0x888]
    // 0x91cca4: ldr             x16, [THR, #0x90]  ; THR::object_sentinel
    // 0x91cca8: cmp             w0, w16
    // 0x91ccac: b.ne            #0x91ccbc
    // 0x91ccb0: r2 = defaultContext
    //     0x91ccb0: add             x2, PP, #9, lsl #12  ; [pp+0x9d88] Field <_SecurityContext@16069316.defaultContext>: static late final (offset: 0x444)
    //     0x91ccb4: ldr             x2, [x2, #0xd88]
    // 0x91ccb8: r0 = InitLateFinalStaticField()
    //     0x91ccb8: bl              #0x158bc78  ; InitLateFinalStaticFieldStub
    // 0x91ccbc: stur            x0, [fp, #-0x10]
    // 0x91ccc0: r0 = current()
    //     0x91ccc0: bl              #0x91b3d4  ; [dart:_http] HttpOverrides::current
    // 0x91ccc4: r0 = _HttpClient()
    //     0x91ccc4: bl              #0x91d0f8  ; Allocate_HttpClientStub -> _HttpClient (size=0x4c)
    // 0x91ccc8: mov             x1, x0
    // 0x91cccc: ldur            x2, [fp, #-0x10]
    // 0x91ccd0: stur            x0, [fp, #-0x10]
    // 0x91ccd4: r0 = _HttpClient()
    //     0x91ccd4: bl              #0x91cdb0  ; [dart:_http] _HttpClient::_HttpClient
    // 0x91ccd8: ldur            x2, [fp, #-0x18]
    // 0x91ccdc: r1 = Function '<anonymous closure>': static.
    //     0x91ccdc: add             x1, PP, #0x13, lsl #12  ; [pp+0x135d0] AnonymousClosure: static (0x91d104), in [package:ooredoo_selfcare_algeria/utils/oa_infosec/pubkey_pinning_client.dart] PublicKeyPinningClient::create (0x91cc4c)
    //     0x91cce0: ldr             x1, [x1, #0x5d0]
    // 0x91cce4: r0 = AllocateClosure()
    //     0x91cce4: bl              #0x158ce98  ; AllocateClosureStub
    // 0x91cce8: ldur            x1, [fp, #-0x10]
    // 0x91ccec: StoreField: r1->field_33 = r0
    //     0x91ccec: stur            w0, [x1, #0x33]
    //     0x91ccf0: ldurb           w16, [x1, #-1]
    //     0x91ccf4: ldurb           w17, [x0, #-1]
    //     0x91ccf8: and             x16, x17, x16, lsr #2
    //     0x91ccfc: tst             x16, HEAP, lsr #32
    //     0x91cd00: b.eq            #0x91cd08
    //     0x91cd04: bl              #0x158c220  ; WriteBarrierWrappersStub
    // 0x91cd08: r0 = PublicKeyPinningClient()
    //     0x91cd08: bl              #0x91cda4  ; AllocatePublicKeyPinningClientStub -> PublicKeyPinningClient (size=0xc)
    // 0x91cd0c: ldur            x1, [fp, #-0x10]
    // 0x91cd10: StoreField: r0->field_7 = r1
    //     0x91cd10: stur            w1, [x0, #7]
    // 0x91cd14: r0 = ReturnAsyncNotFuture()
    //     0x91cd14: b               #0x88fb70  ; ReturnAsyncNotFutureStub
    // 0x91cd18: r0 = StackOverflowSharedWithoutFPURegs()
    //     0x91cd18: bl              #0x158dcc0  ; StackOverflowSharedWithoutFPURegsStub
    // 0x91cd1c: b               #0x91cc68
  }
  [closure] static bool <anonymous closure>(dynamic, X509Certificate, String, int) {
    // ** addr: 0x91d104, size: 0x44
    // 0x91d104: EnterFrame
    //     0x91d104: stp             fp, lr, [SP, #-0x10]!
    //     0x91d108: mov             fp, SP
    // 0x91d10c: ldr             x0, [fp, #0x28]
    // 0x91d110: ArrayLoad: r1 = r0[0]  ; List_4
    //     0x91d110: ldur            w1, [x0, #0x17]
    // 0x91d114: DecompressPointer r1
    //     0x91d114: add             x1, x1, HEAP, lsl #32
    // 0x91d118: CheckStackOverflow
    //     0x91d118: ldr             x16, [THR, #0x48]  ; THR::stack_limit
    //     0x91d11c: cmp             SP, x16
    //     0x91d120: b.ls            #0x91d140
    // 0x91d124: LoadField: r2 = r1->field_f
    //     0x91d124: ldur            w2, [x1, #0xf]
    // 0x91d128: DecompressPointer r2
    //     0x91d128: add             x2, x2, HEAP, lsl #32
    // 0x91d12c: ldr             x1, [fp, #0x20]
    // 0x91d130: r0 = _validateSpki()
    //     0x91d130: bl              #0x91d148  ; [package:ooredoo_selfcare_algeria/utils/oa_infosec/pubkey_pinning_client.dart] PublicKeyPinningClient::_validateSpki
    // 0x91d134: LeaveFrame
    //     0x91d134: mov             SP, fp
    //     0x91d138: ldp             fp, lr, [SP], #0x10
    // 0x91d13c: ret
    //     0x91d13c: ret             
    // 0x91d140: r0 = StackOverflowSharedWithoutFPURegs()
    //     0x91d140: bl              #0x158dcc0  ; StackOverflowSharedWithoutFPURegsStub
    // 0x91d144: b               #0x91d124
  }
  static _ _validateSpki(/* No info */) {
