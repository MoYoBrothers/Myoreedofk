  static _ getReservationToken(/* No info */) async {
    // ** addr: 0x117f850, size: 0x1cc
    // 0x117f850: EnterFrame
    //     0x117f850: stp             fp, lr, [SP, #-0x10]!
    //     0x117f854: mov             fp, SP
    // 0x117f858: AllocStack(0x70)
    //     0x117f858: sub             SP, SP, #0x70
    // 0x117f85c: SetupParameters()
    //     0x117f85c: stur            NULL, [fp, #-8]
    // 0x117f860: CheckStackOverflow
    //     0x117f860: ldr             x16, [THR, #0x48]  ; THR::stack_limit
    //     0x117f864: cmp             SP, x16
    //     0x117f868: b.ls            #0x117fa14
    // 0x117f86c: InitAsync() -> Future<ApiResponse>
    //     0x117f86c: add             x0, PP, #0x26, lsl #12  ; [pp+0x26c90] TypeArguments: <ApiResponse>
    //     0x117f870: ldr             x0, [x0, #0xc90]
    //     0x117f874: bl              #0x8901ec  ; InitAsyncStub
    // 0x117f878: r16 = <String, dynamic>
    //     0x117f878: ldr             x16, [PP, #0x2070]  ; [pp+0x2070] TypeArguments: <String, dynamic>
    // 0x117f87c: ldr             lr, [THR, #0xa8]  ; THR::empty_array
    // 0x117f880: stp             lr, x16, [SP]
    // 0x117f884: r0 = Map._fromLiteral()
    //     0x117f884: bl              #0x87f64c  ; [dart:core] Map::Map._fromLiteral
    // 0x117f888: mov             x4, x0
    // 0x117f88c: stur            x4, [fp, #-0x50]
    // 0x117f890: r0 = LoadClassIdInstr(r4)
    //     0x117f890: ldur            x0, [x4, #-1]
    //     0x117f894: ubfx            x0, x0, #0xc, #0x14
    // 0x117f898: mov             x1, x4
    // 0x117f89c: r2 = "client_id"
    //     0x117f89c: add             x2, PP, #0x13, lsl #12  ; [pp+0x13130] "client_id"
    //     0x117f8a0: ldr             x2, [x2, #0x130]
    // 0x117f8a4: r3 = "number-reservation-auth-oa"
    //     0x117f8a4: add             x3, PP, #0x3f, lsl #12  ; [pp+0x3f100] "number-reservation-auth-oa"
    //     0x117f8a8: ldr             x3, [x3, #0x100]
    // 0x117f8ac: r0 = GDT[cid_x0 + 0x483]()
    //     0x117f8ac: add             lr, x0, #0x483
    //     0x117f8b0: ldr             lr, [x21, lr, lsl #3]
    //     0x117f8b4: blr             lr
    // 0x117f8b8: ldur            x4, [fp, #-0x50]
    // 0x117f8bc: r0 = LoadClassIdInstr(r4)
    //     0x117f8bc: ldur            x0, [x4, #-1]
    //     0x117f8c0: ubfx            x0, x0, #0xc, #0x14
    // 0x117f8c4: mov             x1, x4
    // 0x117f8c8: r2 = "client_secret"
    //     0x117f8c8: add             x2, PP, #0x3f, lsl #12  ; [pp+0x3f108] "client_secret"
    //     0x117f8cc: ldr             x2, [x2, #0x108]
    // 0x117f8d0: r3 = "X5EuIM0TrbnL9O5Mgx4YGJFScEjQXdfy"
    //     0x117f8d0: add             x3, PP, #0x3f, lsl #12  ; [pp+0x3f110] "X5EuIM0TrbnL9O5Mgx4YGJFScEjQXdfy"
    //     0x117f8d4: ldr             x3, [x3, #0x110]
    // 0x117f8d8: r0 = GDT[cid_x0 + 0x483]()
    //     0x117f8d8: add             lr, x0, #0x483
    //     0x117f8dc: ldr             lr, [x21, lr, lsl #3]
    //     0x117f8e0: blr             lr
    // 0x117f8e4: r1 = Null
    //     0x117f8e4: mov             x1, NULL
    // 0x117f8e8: r2 = 4
    //     0x117f8e8: mov             x2, #4
    // 0x117f8ec: r0 = AllocateArray()
    //     0x117f8ec: bl              #0x158dbb4  ; AllocateArrayStub
    // 0x117f8f0: stur            x0, [fp, #-0x58]
    // 0x117f8f4: r0 = LoadStaticField(0xc30)
    //     0x117f8f4: ldr             x0, [THR, #0x78]  ; THR::field_table_values
    //     0x117f8f8: ldr             x0, [x0, #0x1860]
    // 0x117f8fc: ldr             x16, [THR, #0x90]  ; THR::object_sentinel
    // 0x117f900: cmp             w0, w16
    // 0x117f904: b.ne            #0x117f910
    // 0x117f908: r2 = env
    //     0x117f908: ldr             x2, [PP, #0x7568]  ; [pp+0x7568] Field <::.env>: static late final (offset: 0xc30)
    // 0x117f90c: r0 = InitLateFinalStaticField()
    //     0x117f90c: bl              #0x158bc78  ; InitLateFinalStaticFieldStub
    // 0x117f910: LoadField: r1 = r0->field_b
    //     0x117f910: ldur            w1, [x0, #0xb]
    // 0x117f914: DecompressPointer r1
    //     0x117f914: add             x1, x1, HEAP, lsl #32
    // 0x117f918: ldur            x0, [fp, #-0x58]
    // 0x117f91c: StoreField: r0->field_f = r1
    //     0x117f91c: stur            w1, [x0, #0xf]
    // 0x117f920: r16 = "/api/ooredoo-bff/yooz/reservation/token"
    //     0x117f920: add             x16, PP, #0x3f, lsl #12  ; [pp+0x3f118] "/api/ooredoo-bff/yooz/reservation/token"
    //     0x117f924: ldr             x16, [x16, #0x118]
    // 0x117f928: StoreField: r0->field_13 = r16
    //     0x117f928: stur            w16, [x0, #0x13]
    // 0x117f92c: str             x0, [SP]
    // 0x117f930: r0 = _interpolate()
    //     0x117f930: bl              #0x882ff8  ; [dart:core] _StringBase::_interpolate
    // 0x117f934: stur            x0, [fp, #-0x58]
    // 0x117f938: r4 = const [0, 0, 0, 0, null]
    //     0x117f938: add             x4, PP, #0x12, lsl #12  ; [pp+0x12fe8] List(5) [0, 0, 0, 0, Null]
    //     0x117f93c: ldr             x4, [x4, #0xfe8]
    // 0x117f940: r0 = _getCommonHeaders()
    //     0x117f940: bl              #0xcc953c  ; [package:yooz/api/api_calls.dart] YoozApiCalls::_getCommonHeaders
    // 0x117f944: mov             x1, x0
    // 0x117f948: stur            x1, [fp, #-0x60]
    // 0x117f94c: r0 = Await()
    //     0x117f94c: bl              #0x88ffb4  ; AwaitStub
    // 0x117f950: mov             x3, x0
    // 0x117f954: r2 = Null
    //     0x117f954: mov             x2, NULL
    // 0x117f958: r1 = Null
    //     0x117f958: mov             x1, NULL
    // 0x117f95c: stur            x3, [fp, #-0x60]
    // 0x117f960: r8 = Map<String, String>
    //     0x117f960: add             x8, PP, #0xa, lsl #12  ; [pp+0xa838] Type: Map<String, String>
    //     0x117f964: ldr             x8, [x8, #0x838]
