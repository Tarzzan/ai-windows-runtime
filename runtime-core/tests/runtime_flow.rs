use runtime_core::{ApiStatus, RuntimeCore, load_pe_image, parse_pe_metadata};

fn pe_with_imports() -> Vec<u8> {
    let mut b = vec![0u8; 0x600];
    b[0] = b'M';
    b[1] = b'Z';
    b[0x3C..0x40].copy_from_slice(&(0x80u32).to_le_bytes());

    b[0x80..0x84].copy_from_slice(&0x0000_4550u32.to_le_bytes());
    b[0x84..0x86].copy_from_slice(&0x8664u16.to_le_bytes());
    b[0x86..0x88].copy_from_slice(&2u16.to_le_bytes());
    b[0x94..0x96].copy_from_slice(&0xF0u16.to_le_bytes());

    let optional = 0x98usize;
    b[optional..optional + 2].copy_from_slice(&0x20Bu16.to_le_bytes());
    b[optional + 16..optional + 20].copy_from_slice(&0x2000u32.to_le_bytes());
    b[optional + 56..optional + 60].copy_from_slice(&0x4000u32.to_le_bytes());
    b[optional + 60..optional + 64].copy_from_slice(&0x200u32.to_le_bytes());
    b[optional + 108..optional + 112].copy_from_slice(&16u32.to_le_bytes());
    b[optional + 120..optional + 124].copy_from_slice(&0x3000u32.to_le_bytes());
    b[optional + 124..optional + 128].copy_from_slice(&40u32.to_le_bytes());

    let sh = optional + 0xF0;

    b[sh..sh + 8].copy_from_slice(b".text\0\0\0");
    b[sh + 8..sh + 12].copy_from_slice(&0x100u32.to_le_bytes());
    b[sh + 12..sh + 16].copy_from_slice(&0x1000u32.to_le_bytes());
    b[sh + 16..sh + 20].copy_from_slice(&0x200u32.to_le_bytes());
    b[sh + 20..sh + 24].copy_from_slice(&0x200u32.to_le_bytes());

    let sh2 = sh + 40;
    b[sh2..sh2 + 8].copy_from_slice(b".rdata\0\0");
    b[sh2 + 8..sh2 + 12].copy_from_slice(&0x200u32.to_le_bytes());
    b[sh2 + 12..sh2 + 16].copy_from_slice(&0x3000u32.to_le_bytes());
    b[sh2 + 16..sh2 + 20].copy_from_slice(&0x200u32.to_le_bytes());
    b[sh2 + 20..sh2 + 24].copy_from_slice(&0x400u32.to_le_bytes());

    b[0x200] = 0xCC;
    b[0x201] = 0x90;

    b[0x400 + 12..0x400 + 16].copy_from_slice(&0x3030u32.to_le_bytes());
    b[0x400 + 16..0x400 + 20].copy_from_slice(&0x3040u32.to_le_bytes());

    let name = b"KERNEL32.dll\0";
    b[0x430..0x430 + name.len()].copy_from_slice(name);

    b
}

#[test]
fn pe_parser_extracts_core_metadata() {
    let meta = parse_pe_metadata(&pe_with_imports()).expect("valid test PE");
    assert_eq!(meta.machine, 0x8664);
    assert_eq!(meta.number_of_sections, 2);
    assert_eq!(meta.entry_point_rva, 0x2000);
    assert_eq!(meta.size_of_image, 0x4000);
}

#[test]
fn native_loader_maps_sections_and_import_table() {
    let loaded = load_pe_image(&pe_with_imports()).expect("must load PE image");
    assert_eq!(loaded.sections.len(), 2);
    assert_eq!(loaded.imports.len(), 1);
    assert_eq!(loaded.imports[0].dll_name, "KERNEL32.dll");
    assert_eq!(loaded.mapped_image[0x1000], 0xCC);
    assert_eq!(loaded.mapped_image[0x1001], 0x90);
}

#[test]
fn runtime_dispatcher_supports_stub_and_implemented() {
    let mut core = RuntimeCore::new();
    core.dispatcher_mut()
        .register_implemented("kernel32.GetTickCount");
    core.dispatcher_mut().register_stub(
        "winhttp.WinHttpOpen",
        "phase-3 stub while transport layer is built",
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

#[test]
fn runtime_load_report_tracks_imports() {
    let core = RuntimeCore::new();
    let report = core
        .load_pe_image(&pe_with_imports())
        .expect("runtime must load test image");
    assert_eq!(report.sections_loaded, 2);
    assert_eq!(report.imports_checked, 1);
    assert_eq!(report.imported_dlls, vec!["KERNEL32.dll".to_string()]);
}
