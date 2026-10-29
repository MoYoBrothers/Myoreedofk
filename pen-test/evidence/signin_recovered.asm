  static _ signIn(/* No info */) async {
    // ** addr: 0xc8f4a4, size: 0x3d4
    // 0xc8f4a4: EnterFrame
    //     0xc8f4a4: stp             fp, lr, [SP, #-0x10]!
    //     0xc8f4a8: mov             fp, SP
    // 0xc8f4ac: AllocStack(0xb8)
    //     0xc8f4ac: sub             SP, SP, #0xb8
    // 0xc8f4b0: SetupParameters(dynamic _ /* r1 => r1, fp-0x80 */, dynamic _ /* r2 => r3, fp-0x88 */)
    //     0xc8f4b0: stur            NULL, [fp, #-8]
    //     0xc8f4b4: mov             x3, x2
    //     0xc8f4b8: stur            x1, [fp, #-0x80]
    //     0xc8f4bc: stur            x2, [fp, #-0x88]
    // 0xc8f4c0: CheckStackOverflow
    //     0xc8f4c0: ldr             x16, [THR, #0x48]  ; THR::stack_limit
    //     0xc8f4c4: cmp             SP, x16
    //     0xc8f4c8: b.ls            #0xc8f868
    // 0xc8f4cc: InitAsync() -> Future<ApiResponse>
    //     0xc8f4cc: add             x0, PP, #0x12, lsl #12  ; [pp+0x12fc0] TypeArguments: <ApiResponse>
    //     0xc8f4d0: ldr             x0, [x0, #0xfc0]
    //     0xc8f4d4: bl              #0x8901ec  ; InitAsyncStub
    // 0xc8f4d8: r0 = ApiResponse()
    //     0xc8f4d8: bl              #0x8ffc68  ; AllocateApiResponseStub -> ApiResponse (size=0x1c)
    // 0xc8f4dc: mov             x1, x0
    // 0xc8f4e0: stur            x0, [fp, #-0x90]
    // 0xc8f4e4: r4 = const [0, 0x1, 0, 0x1, null]
    //     0xc8f4e4: ldr             x4, [PP, #0xe8]  ; [pp+0xe8] List(5) [0, 0x1, 0, 0x1, Null]
    // 0xc8f4e8: r0 = ApiResponse()
    //     0xc8f4e8: bl              #0x8f9b88  ; [package:ooredoo_selfcare_algeria/api/api_response.dart] ApiResponse::ApiResponse
    // 0xc8f4ec: r16 = <String, String>
    //     0xc8f4ec: add             x16, PP, #8, lsl #12  ; [pp+0x8a08] TypeArguments: <String, String>
    //     0xc8f4f0: ldr             x16, [x16, #0xa08]
    // 0xc8f4f4: ldr             lr, [THR, #0xa8]  ; THR::empty_array
    // 0xc8f4f8: stp             lr, x16, [SP]
    // 0xc8f4fc: r0 = Map._fromLiteral()
    //     0xc8f4fc: bl              #0x87f64c  ; [dart:core] Map::Map._fromLiteral
    // 0xc8f500: stur            x0, [fp, #-0x98]
    // 0xc8f504: ldur            x16, [fp, #-0x80]
    // 0xc8f508: str             x16, [SP]
    // 0xc8f50c: r1 = "POST"
    //     0xc8f50c: add             x1, PP, #8, lsl #12  ; [pp+0x8bd8] "POST"
    //     0xc8f510: ldr             x1, [x1, #0xbd8]
    // 0xc8f514: r2 = "/api/auth/realms/myooredoo/protocol/openid-connect/token"
    //     0xc8f514: add             x2, PP, #0x13, lsl #12  ; [pp+0x13120] "/api/auth/realms/myooredoo/protocol/openid-connect/token"
    //     0xc8f518: ldr             x2, [x2, #0x120]
    // 0xc8f51c: r4 = const [0, 0x3, 0x1, 0x2, msisdn, 0x2, null]
    //     0xc8f51c: add             x4, PP, #0x13, lsl #12  ; [pp+0x13128] List(7) [0, 0x3, 0x1, 0x2, "msisdn", 0x2, Null]
    //     0xc8f520: ldr             x4, [x4, #0x128]
    // 0xc8f524: r0 = getNonceValidation()
    //     0xc8f524: bl              #0x95c71c  ; [package:ooredoo_selfcare_algeria/api/api_calls.dart] ApiCalls::getNonceValidation
    // 0xc8f528: mov             x1, x0
    // 0xc8f52c: stur            x1, [fp, #-0xa0]
    // 0xc8f530: r0 = Await()
    //     0xc8f530: bl              #0x88ffb4  ; AwaitStub
    // 0xc8f534: stur            x0, [fp, #-0x90]
    // 0xc8f538: LoadField: r1 = r0->field_f
    //     0xc8f538: ldur            w1, [x0, #0xf]
    // 0xc8f53c: DecompressPointer r1
    //     0xc8f53c: add             x1, x1, HEAP, lsl #32
    // 0xc8f540: tbnz            w1, #4, #0xc8f7e0
    // 0xc8f544: ldur            x1, [fp, #-0x80]
    // 0xc8f548: r16 = <String, String>
    //     0xc8f548: add             x16, PP, #8, lsl #12  ; [pp+0x8a08] TypeArguments: <String, String>
    //     0xc8f54c: ldr             x16, [x16, #0xa08]
    // 0xc8f550: ldr             lr, [THR, #0xa8]  ; THR::empty_array
    // 0xc8f554: stp             lr, x16, [SP]
    // 0xc8f558: r0 = Map._fromLiteral()
    //     0xc8f558: bl              #0x87f64c  ; [dart:core] Map::Map._fromLiteral
    // 0xc8f55c: mov             x1, x0
    // 0xc8f560: r2 = "client_id"
    //     0xc8f560: add             x2, PP, #0x13, lsl #12  ; [pp+0x13130] "client_id"
    //     0xc8f564: ldr             x2, [x2, #0x130]
    // 0xc8f568: r3 = "myooredoo-app"
    //     0xc8f568: add             x3, PP, #0x13, lsl #12  ; [pp+0x13138] "myooredoo-app"
    //     0xc8f56c: ldr             x3, [x3, #0x138]
    // 0xc8f570: stur            x0, [fp, #-0xa0]
    // 0xc8f574: r0 = []=()
    //     0xc8f574: bl              #0x148c694  ; [dart:_compact_hash] __Map&_HashVMBase&MapMixin&_HashBase&_OperatorEqualsAndHashCode&_LinkedHashMapMixin::[]=
    // 0xc8f578: ldur            x1, [fp, #-0xa0]
    // 0xc8f57c: r2 = "grant_type"
    //     0xc8f57c: add             x2, PP, #0x13, lsl #12  ; [pp+0x13140] "grant_type"
    //     0xc8f580: ldr             x2, [x2, #0x140]
    // 0xc8f584: r3 = "password"
    //     0xc8f584: add             x3, PP, #0x18, lsl #12  ; [pp+0x18718] "password"
    //     0xc8f588: ldr             x3, [x3, #0x718]
    // 0xc8f58c: r0 = []=()
    //     0xc8f58c: bl              #0x148c694  ; [dart:_compact_hash] __Map&_HashVMBase&MapMixin&_HashBase&_OperatorEqualsAndHashCode&_LinkedHashMapMixin::[]=
    // 0xc8f590: ldur            x3, [fp, #-0x80]
    // 0xc8f594: r0 = LoadClassIdInstr(r3)
    //     0xc8f594: ldur            x0, [x3, #-1]
    //     0xc8f598: ubfx            x0, x0, #0xc, #0x14
    // 0xc8f59c: mov             x1, x3
    // 0xc8f5a0: r2 = "@"
    //     0xc8f5a0: add             x2, PP, #0xa, lsl #12  ; [pp+0xa780] "@"
    //     0xc8f5a4: ldr             x2, [x2, #0x780]
    // 0xc8f5a8: r4 = const [0, 0x2, 0, 0x2, null]
    //     0xc8f5a8: ldr             x4, [PP, #0xc0]  ; [pp+0xc0] List(5) [0, 0x2, 0, 0x2, Null]
    // 0xc8f5ac: r0 = GDT[cid_x0 + -0xffc]()
    //     0xc8f5ac: sub             lr, x0, #0xffc
    //     0xc8f5b0: ldr             lr, [x21, lr, lsl #3]
    //     0xc8f5b4: blr             lr
    // 0xc8f5b8: tbnz            w0, #4, #0xc8f5d4
    // 0xc8f5bc: ldur            x1, [fp, #-0xa0]
    // 0xc8f5c0: ldur            x3, [fp, #-0x80]
    // 0xc8f5c4: r2 = "email"
    //     0xc8f5c4: add             x2, PP, #0x18, lsl #12  ; [pp+0x186a0] "email"
    //     0xc8f5c8: ldr             x2, [x2, #0x6a0]
    // 0xc8f5cc: r0 = []=()
    //     0xc8f5cc: bl              #0x148c694  ; [dart:_compact_hash] __Map&_HashVMBase&MapMixin&_HashBase&_OperatorEqualsAndHashCode&_LinkedHashMapMixin::[]=
    // 0xc8f5d0: b               #0xc8f5e8
    // 0xc8f5d4: ldur            x1, [fp, #-0xa0]
    // 0xc8f5d8: ldur            x3, [fp, #-0x80]
    // 0xc8f5dc: r2 = "username"
    //     0xc8f5dc: add             x2, PP, #0x1e, lsl #12  ; [pp+0x1e610] "username"
    //     0xc8f5e0: ldr             x2, [x2, #0x610]
    // 0xc8f5e4: r0 = []=()
    //     0xc8f5e4: bl              #0x148c694  ; [dart:_compact_hash] __Map&_HashVMBase&MapMixin&_HashBase&_OperatorEqualsAndHashCode&_LinkedHashMapMixin::[]=
    // 0xc8f5e8: ldur            x4, [fp, #-0xa0]
    // 0xc8f5ec: r0 = LoadClassIdInstr(r4)
    //     0xc8f5ec: ldur            x0, [x4, #-1]
    //     0xc8f5f0: ubfx            x0, x0, #0xc, #0x14
    // 0xc8f5f4: mov             x1, x4
    // 0xc8f5f8: ldur            x3, [fp, #-0x88]
    // 0xc8f5fc: r2 = "password"
    //     0xc8f5fc: add             x2, PP, #0x18, lsl #12  ; [pp+0x18718] "password"
    //     0xc8f600: ldr             x2, [x2, #0x718]
    // 0xc8f604: r0 = GDT[cid_x0 + 0x483]()
    //     0xc8f604: add             lr, x0, #0x483
    //     0xc8f608: ldr             lr, [x21, lr, lsl #3]
    //     0xc8f60c: blr             lr
    // 0xc8f610: ldur            x1, [fp, #-0x90]
    // 0xc8f614: r0 = getResponseHeaders()
    //     0xc8f614: bl              #0x95c648  ; [package:ooredoo_selfcare_algeria/api/api_response.dart] ApiResponse::getResponseHeaders
    // 0xc8f618: cmp             w0, NULL
    // 0xc8f61c: b.eq            #0xc8f870
    // 0xc8f620: r1 = LoadClassIdInstr(r0)
    //     0xc8f620: ldur            x1, [x0, #-1]
    //     0xc8f624: ubfx            x1, x1, #0xc, #0x14
    // 0xc8f628: mov             x16, x0
    // 0xc8f62c: mov             x0, x1
    // 0xc8f630: mov             x1, x16
    // 0xc8f634: r2 = "x-nonce-id"
    //     0xc8f634: add             x2, PP, #0x12, lsl #12  ; [pp+0x12fd0] "x-nonce-id"
    //     0xc8f638: ldr             x2, [x2, #0xfd0]
    // 0xc8f63c: r0 = GDT[cid_x0 + -0x13d]()
    //     0xc8f63c: sub             lr, x0, #0x13d
    //     0xc8f640: ldr             lr, [x21, lr, lsl #3]
    //     0xc8f644: blr             lr
    // 0xc8f648: cmp             w0, NULL
    // 0xc8f64c: b.ne            #0xc8f654
    // 0xc8f650: r0 = ""
    //     0xc8f650: ldr             x0, [PP, #0x8b8]  ; [pp+0x8b8] ""
    // 0xc8f654: ldur            x1, [fp, #-0x98]
    // 0xc8f658: mov             x3, x0
    // 0xc8f65c: stur            x0, [fp, #-0x88]
    // 0xc8f660: r2 = "x-nonce-id"
    //     0xc8f660: add             x2, PP, #0x12, lsl #12  ; [pp+0x12fd0] "x-nonce-id"
    //     0xc8f664: ldr             x2, [x2, #0xfd0]
    // 0xc8f668: r0 = []=()
    //     0xc8f668: bl              #0x148c694  ; [dart:_compact_hash] __Map&_HashVMBase&MapMixin&_HashBase&_OperatorEqualsAndHashCode&_LinkedHashMapMixin::[]=
    // 0xc8f66c: ldur            x1, [fp, #-0x90]
    // 0xc8f670: r0 = getResponseHeaders()
    //     0xc8f670: bl              #0x95c648  ; [package:ooredoo_selfcare_algeria/api/api_response.dart] ApiResponse::getResponseHeaders
    // 0xc8f674: cmp             w0, NULL
    // 0xc8f678: b.eq            #0xc8f874
    // 0xc8f67c: r1 = LoadClassIdInstr(r0)
    //     0xc8f67c: ldur            x1, [x0, #-1]
    //     0xc8f680: ubfx            x1, x1, #0xc, #0x14
    // 0xc8f684: mov             x16, x0
    // 0xc8f688: mov             x0, x1
    // 0xc8f68c: mov             x1, x16
    // 0xc8f690: r2 = "x-chronos-id"
    //     0xc8f690: add             x2, PP, #0x12, lsl #12  ; [pp+0x12fd8] "x-chronos-id"
    //     0xc8f694: ldr             x2, [x2, #0xfd8]
    // 0xc8f698: r0 = GDT[cid_x0 + -0x13d]()
    //     0xc8f698: sub             lr, x0, #0x13d
    //     0xc8f69c: ldr             lr, [x21, lr, lsl #3]
    //     0xc8f6a0: blr             lr
    // 0xc8f6a4: cmp             w0, NULL
    // 0xc8f6a8: b.ne            #0xc8f6b0
    // 0xc8f6ac: r0 = ""
    //     0xc8f6ac: ldr             x0, [PP, #0x8b8]  ; [pp+0x8b8] ""
    // 0xc8f6b0: ldur            x1, [fp, #-0x98]
    // 0xc8f6b4: mov             x3, x0
    // 0xc8f6b8: stur            x0, [fp, #-0x88]
    // 0xc8f6bc: r2 = "x-chronos-id"
    //     0xc8f6bc: add             x2, PP, #0x12, lsl #12  ; [pp+0x12fd8] "x-chronos-id"
    //     0xc8f6c0: ldr             x2, [x2, #0xfd8]
    // 0xc8f6c4: r0 = []=()
    //     0xc8f6c4: bl              #0x148c694  ; [dart:_compact_hash] __Map&_HashVMBase&MapMixin&_HashBase&_OperatorEqualsAndHashCode&_LinkedHashMapMixin::[]=
    // 0xc8f6c8: ldur            x1, [fp, #-0x98]
    // 0xc8f6cc: ldur            x3, [fp, #-0x80]
    // 0xc8f6d0: r2 = "x-msisdn"
    //     0xc8f6d0: add             x2, PP, #0xa, lsl #12  ; [pp+0xaaf8] "x-msisdn"
    //     0xc8f6d4: ldr             x2, [x2, #0xaf8]
    // 0xc8f6d8: r0 = []=()
    //     0xc8f6d8: bl              #0x148c694  ; [dart:_compact_hash] __Map&_HashVMBase&MapMixin&_HashBase&_OperatorEqualsAndHashCode&_LinkedHashMapMixin::[]=
    // 0xc8f6dc: ldur            x1, [fp, #-0x98]
    // 0xc8f6e0: r0 = setChecksumHeaders()
    //     0xc8f6e0: bl              #0x92ab94  ; [package:ooredoo_selfcare_algeria/api/api_calls.dart] ApiCalls::setChecksumHeaders
    // 0xc8f6e4: mov             x1, x0
    // 0xc8f6e8: stur            x1, [fp, #-0xa8]
    // 0xc8f6ec: r0 = Await()
    //     0xc8f6ec: bl              #0x88ffb4  ; AwaitStub
    // 0xc8f6f0: ldur            x1, [fp, #-0x98]
    // 0xc8f6f4: r0 = setDeviceDataGatherForKeycloak()
    //     0xc8f6f4: bl              #0x95c568  ; [package:ooredoo_selfcare_algeria/api/api_calls.dart] ApiCalls::setDeviceDataGatherForKeycloak
    // 0xc8f6f8: mov             x1, x0
    // 0xc8f6fc: stur            x1, [fp, #-0xa8]
    // 0xc8f700: r0 = Await()
    //     0xc8f700: bl              #0x88ffb4  ; AwaitStub
    // 0xc8f704: ldur            x1, [fp, #-0x98]
    // 0xc8f708: r4 = const [0, 0x1, 0, 0x1, null]
    //     0xc8f708: ldr             x4, [PP, #0xe8]  ; [pp+0xe8] List(5) [0, 0x1, 0, 0x1, Null]
    // 0xc8f70c: r0 = setDeviceFingerprintHeader()
    //     0xc8f70c: bl              #0x92a480  ; [package:ooredoo_selfcare_algeria/api/api_calls.dart] ApiCalls::setDeviceFingerprintHeader
    // 0xc8f710: mov             x1, x0
    // 0xc8f714: stur            x1, [fp, #-0xa8]
    // 0xc8f718: r0 = Await()
    //     0xc8f718: bl              #0x88ffb4  ; AwaitStub
    // 0xc8f71c: ldur            x1, [fp, #-0x98]
    // 0xc8f720: r2 = "x-force-update"
    //     0xc8f720: add             x2, PP, #0x13, lsl #12  ; [pp+0x13150] "x-force-update"
    //     0xc8f724: ldr             x2, [x2, #0x150]
    // 0xc8f728: r3 = "true"
    //     0xc8f728: ldr             x3, [PP, #0x6b28]  ; [pp+0x6b28] "true"
    // 0xc8f72c: r0 = []=()
    //     0xc8f72c: bl              #0x148c694  ; [dart:_compact_hash] __Map&_HashVMBase&MapMixin&_HashBase&_OperatorEqualsAndHashCode&_LinkedHashMapMixin::[]=
    // 0xc8f730: r0 = getAppVersion()
    //     0xc8f730: bl              #0x92b71c  ; [package:ooredoo_selfcare_algeria/utils/functions/common_functions.dart] ::getAppVersion
    // 0xc8f734: mov             x1, x0
    // 0xc8f738: stur            x1, [fp, #-0xa8]
    // 0xc8f73c: r0 = Await()
    //     0xc8f73c: bl              #0x88ffb4  ; AwaitStub
    // 0xc8f740: ldur            x1, [fp, #-0x98]
    // 0xc8f744: mov             x3, x0
    // 0xc8f748: r2 = "x-version"
    //     0xc8f748: ldr             x2, [PP, #0x7ad8]  ; [pp+0x7ad8] "x-version"
    // 0xc8f74c: stur            x0, [fp, #-0xa8]
    // 0xc8f750: r0 = []=()
    //     0xc8f750: bl              #0x148c694  ; [dart:_compact_hash] __Map&_HashVMBase&MapMixin&_HashBase&_OperatorEqualsAndHashCode&_LinkedHashMapMixin::[]=
    // 0xc8f754: r0 = LoadStaticField(0xc30)
    //     0xc8f754: ldr             x0, [THR, #0x78]  ; THR::field_table_values
    //     0xc8f758: ldr             x0, [x0, #0x1860]
    // 0xc8f75c: ldr             x16, [THR, #0x90]  ; THR::object_sentinel
    // 0xc8f760: cmp             w0, w16
    // 0xc8f764: b.ne            #0xc8f770
    // 0xc8f768: r2 = env
    //     0xc8f768: ldr             x2, [PP, #0x7568]  ; [pp+0x7568] Field <::.env>: static late final (offset: 0xc30)
    // 0xc8f76c: r0 = InitLateFinalStaticField()
    //     0xc8f76c: bl              #0x158bc78  ; InitLateFinalStaticFieldStub
    // 0xc8f770: ldur            x1, [fp, #-0x98]
    // 0xc8f774: r2 = "platform"
    //     0xc8f774: ldr             x2, [PP, #0x7ac8]  ; [pp+0x7ac8] "platform"
    // 0xc8f778: r3 = "android"
    //     0xc8f778: ldr             x3, [PP, #0x3a20]  ; [pp+0x3a20] "android"
    // 0xc8f77c: stur            x0, [fp, #-0x80]
    // 0xc8f780: r0 = []=()
    //     0xc8f780: bl              #0x148c694  ; [dart:_compact_hash] __Map&_HashVMBase&MapMixin&_HashBase&_OperatorEqualsAndHashCode&_LinkedHashMapMixin::[]=
    // 0xc8f784: ldur            x1, [fp, #-0x98]
    // 0xc8f788: r2 = "X-Platform-Origin"
    //     0xc8f788: ldr             x2, [PP, #0x7ad0]  ; [pp+0x7ad0] "X-Platform-Origin"
    // 0xc8f78c: r3 = "mobile-android"
    //     0xc8f78c: ldr             x3, [PP, #0x7c08]  ; [pp+0x7c08] "mobile-android"
    // 0xc8f790: r0 = []=()
    //     0xc8f790: bl              #0x148c694  ; [dart:_compact_hash] __Map&_HashVMBase&MapMixin&_HashBase&_OperatorEqualsAndHashCode&_LinkedHashMapMixin::[]=
    // 0xc8f794: r1 = Null
    //     0xc8f794: mov             x1, NULL
    // 0xc8f798: r2 = 4
    //     0xc8f798: mov             x2, #4
    // 0xc8f79c: r0 = AllocateArray()
    //     0xc8f79c: bl              #0x158dbb4  ; AllocateArrayStub
    // 0xc8f7a0: mov             x1, x0
    // 0xc8f7a4: ldur            x0, [fp, #-0x80]
    // 0xc8f7a8: LoadField: r2 = r0->field_b
    //     0xc8f7a8: ldur            w2, [x0, #0xb]
    // 0xc8f7ac: DecompressPointer r2
    //     0xc8f7ac: add             x2, x2, HEAP, lsl #32
    // 0xc8f7b0: StoreField: r1->field_f = r2
    //     0xc8f7b0: stur            w2, [x1, #0xf]
    // 0xc8f7b4: r16 = "/api/auth/realms/myooredoo/protocol/openid-connect/token"
    //     0xc8f7b4: add             x16, PP, #0x13, lsl #12  ; [pp+0x13120] "/api/auth/realms/myooredoo/protocol/openid-connect/token"
    //     0xc8f7b8: ldr             x16, [x16, #0x120]
    // 0xc8f7bc: StoreField: r1->field_13 = r16
    //     0xc8f7bc: stur            w16, [x1, #0x13]
    // 0xc8f7c0: str             x1, [SP]
    // 0xc8f7c4: r0 = _interpolate()
    //     0xc8f7c4: bl              #0x882ff8  ; [dart:core] _StringBase::_interpolate
    // 0xc8f7c8: mov             x1, x0
    // 0xc8f7cc: ldur            x2, [fp, #-0x98]
    // 0xc8f7d0: ldur            x3, [fp, #-0xa0]
    // 0xc8f7d4: ldur            x5, [fp, #-0x98]
    // 0xc8f7d8: r0 = XWFormRequest()
    //     0xc8f7d8: bl              #0x95b76c  ; [package:ooredoo_selfcare_algeria/api/api_caller.dart] ApiCaller::XWFormRequest
    // 0xc8f7dc: r0 = ReturnAsync()
    //     0xc8f7dc: b               #0x8b52f4  ; ReturnAsyncStub
    // 0xc8f7e0: ldur            x0, [fp, #-0x90]
    // 0xc8f7e4: r0 = ReturnAsync()
    //     0xc8f7e4: b               #0x8b52f4  ; ReturnAsyncStub
    // 0xc8f7e8: sub             SP, fp, #0xb8
    // 0xc8f7ec: stur            x0, [fp, #-0x80]
    // 0xc8f7f0: r0 = ApiResponse()
    //     0xc8f7f0: bl              #0x8ffc68  ; AllocateApiResponseStub -> ApiResponse (size=0x1c)
    // 0xc8f7f4: mov             x1, x0
    // 0xc8f7f8: stur            x0, [fp, #-0x88]
    // 0xc8f7fc: r4 = const [0, 0x1, 0, 0x1, null]
    //     0xc8f7fc: ldr             x4, [PP, #0xe8]  ; [pp+0xe8] List(5) [0, 0x1, 0, 0x1, Null]
    // 0xc8f800: r0 = ApiResponse()
    //     0xc8f800: bl              #0x8f9b88  ; [package:ooredoo_selfcare_algeria/api/api_response.dart] ApiResponse::ApiResponse
    // 0xc8f804: ldur            x1, [fp, #-0x88]
    // 0xc8f808: r0 = false
    //     0xc8f808: add             x0, NULL, #0x30  ; false
    // 0xc8f80c: StoreField: r1->field_f = r0
