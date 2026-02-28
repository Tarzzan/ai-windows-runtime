use runtime_core::{ApiStatus, RuntimeCore, parse_pe_metadata};

fn minimal_pe() -> Vec<u8> {
    let mut b = vec![0u8; 512];
    b[0] = b'M';
    b[1] = b'Z';
    b[0x3C..0x40].copy_from_slice(&(0x80u32).to_le_bytes());

    b[0x80..0x84].copy_from_slice(&0x0000_4550u32.to_le_bytes());
    b[0x84..0x86].copy_from_slice(&0x8664u16.to_le_bytes());
    b[0x86..0x88].copy_from_slice(&5u16.to_le_bytes());
    b[0x94..0x96].copy_from_slice(&0xF0u16.to_le_bytes());

    let optional = 0x98usize;
    b[optional + 16..optional + 20].copy_from_slice(&0x2000u32.to_le_bytes());
    b[optional + 56..optional + 60].copy_from_slice(&0xB000u32.to_le_bytes());
    b
}

#[test]
fn pe_parser_extracts_core_metadata() {
    let meta = parse_pe_metadata(&minimal_pe()).expect("valid test PE");
    assert_eq!(meta.machine, 0x8664);
    assert_eq!(meta.number_of_sections, 5);
    assert_eq!(meta.entry_point_rva, 0x2000);
    assert_eq!(meta.size_of_image, 0xB000);
}

#[test]
fn runtime_dispatcher_supports_stub_and_implemented() {
    let mut core = RuntimeCore::new();
    core.dispatcher_mut()
        .register_implemented("kernel32.GetTickCount");
    core.dispatcher_mut().register_stub(
        "winhttp.WinHttpOpen",
        "phase-2 stub while transport layer is built",
    );

    let ok = core
        .dispatch_api("kernel32.GetTickCount")
        .expect("implemented API must dispatch");
    assert_eq!(ok.status, ApiStatus::Implemented);

    let stub = core
        .dispatch_api("winhttp.WinHttpOpen")
        .expect("stubbed API must dispatch");
    assert_eq!(stub.status, ApiStatus::Stubbed);

    let missing = core.dispatch_api("combase.RoActivateInstance");
    assert!(missing.is_err());
}
