use runtime_core::{
    ApiStatus, MemoryProtection, PeImportSymbol, ProcessState, RuntimeCore, STILL_ACTIVE,
    ThreadState, WaitMultipleStatus, WaitStatus, Win32Call, Win32CallResult, load_pe_image,
    parse_pe_metadata,
};

fn pe_with_imports() -> Vec<u8> {
    let mut b = vec![0u8; 0x700];
    b[0] = b'M';
    b[1] = b'Z';
    b[0x3C..0x40].copy_from_slice(&(0x80u32).to_le_bytes());

    b[0x80..0x84].copy_from_slice(&0x0000_4550u32.to_le_bytes());
    b[0x84..0x86].copy_from_slice(&0x8664u16.to_le_bytes());
    b[0x86..0x88].copy_from_slice(&2u16.to_le_bytes());
    b[0x94..0x96].copy_from_slice(&0xF0u16.to_le_bytes());

    let optional = 0x98usize;
    b[optional..optional + 2].copy_from_slice(&0x20Bu16.to_le_bytes());
    b[optional + 24..optional + 32].copy_from_slice(&0x0000_0001_8000_0000u64.to_le_bytes());
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
    b[sh2 + 8..sh2 + 12].copy_from_slice(&0x300u32.to_le_bytes());
    b[sh2 + 12..sh2 + 16].copy_from_slice(&0x3000u32.to_le_bytes());
    b[sh2 + 16..sh2 + 20].copy_from_slice(&0x300u32.to_le_bytes());
    b[sh2 + 20..sh2 + 24].copy_from_slice(&0x400u32.to_le_bytes());

    b[0x200] = 0xCC;
    b[0x201] = 0x90;

    b[0x400..0x404].copy_from_slice(&0x3050u32.to_le_bytes());
    b[0x400 + 12..0x400 + 16].copy_from_slice(&0x3030u32.to_le_bytes());
    b[0x400 + 16..0x400 + 20].copy_from_slice(&0x3070u32.to_le_bytes());

    let dll = b"KERNEL32.dll\0";
    b[0x430..0x430 + dll.len()].copy_from_slice(dll);

    b[0x450..0x458].copy_from_slice(&0x3080u64.to_le_bytes());
    b[0x458..0x460].copy_from_slice(&(0x8000_0000_0000_0123u64).to_le_bytes());
    b[0x460..0x468].copy_from_slice(&0u64.to_le_bytes());

    b[0x480..0x482].copy_from_slice(&7u16.to_le_bytes());
    let name = b"Sleep\0";
    b[0x482..0x482 + name.len()].copy_from_slice(name);

    b
}

fn pe_with_duplicate_imports() -> Vec<u8> {
    let mut b = pe_with_imports();
    b[0x450..0x458].copy_from_slice(&0x3080u64.to_le_bytes());
    b[0x458..0x460].copy_from_slice(&0x3080u64.to_le_bytes());
    b[0x460..0x468].copy_from_slice(&(0x8000_0000_0000_0123u64).to_le_bytes());
    b[0x468..0x470].copy_from_slice(&0u64.to_le_bytes());
    b
}

fn pe_with_exports() -> Vec<u8> {
    let mut b = vec![0u8; 0x800];
    b[0] = b'M';
    b[1] = b'Z';
    b[0x3C..0x40].copy_from_slice(&(0x80u32).to_le_bytes());

    b[0x80..0x84].copy_from_slice(&0x0000_4550u32.to_le_bytes());
    b[0x84..0x86].copy_from_slice(&0x8664u16.to_le_bytes());
    b[0x86..0x88].copy_from_slice(&2u16.to_le_bytes());
    b[0x94..0x96].copy_from_slice(&0xF0u16.to_le_bytes());

    let optional = 0x98usize;
    b[optional..optional + 2].copy_from_slice(&0x20Bu16.to_le_bytes());
    b[optional + 24..optional + 32].copy_from_slice(&0x0000_0001_8000_0000u64.to_le_bytes());
    b[optional + 16..optional + 20].copy_from_slice(&0x1000u32.to_le_bytes());
    b[optional + 56..optional + 60].copy_from_slice(&0x5000u32.to_le_bytes());
    b[optional + 60..optional + 64].copy_from_slice(&0x200u32.to_le_bytes());
    b[optional + 108..optional + 112].copy_from_slice(&16u32.to_le_bytes());
    b[optional + 112..optional + 116].copy_from_slice(&0x3000u32.to_le_bytes());
    b[optional + 116..optional + 120].copy_from_slice(&40u32.to_le_bytes());

    let sh = optional + 0xF0;
    b[sh..sh + 8].copy_from_slice(b".text\0\0\0");
    b[sh + 8..sh + 12].copy_from_slice(&0x100u32.to_le_bytes());
    b[sh + 12..sh + 16].copy_from_slice(&0x1000u32.to_le_bytes());
    b[sh + 16..sh + 20].copy_from_slice(&0x200u32.to_le_bytes());
    b[sh + 20..sh + 24].copy_from_slice(&0x200u32.to_le_bytes());

    let sh2 = sh + 40;
    b[sh2..sh2 + 8].copy_from_slice(b".edata\0\0");
    b[sh2 + 8..sh2 + 12].copy_from_slice(&0x300u32.to_le_bytes());
    b[sh2 + 12..sh2 + 16].copy_from_slice(&0x3000u32.to_le_bytes());
    b[sh2 + 16..sh2 + 20].copy_from_slice(&0x300u32.to_le_bytes());
    b[sh2 + 20..sh2 + 24].copy_from_slice(&0x400u32.to_le_bytes());

    b[0x400 + 12..0x400 + 16].copy_from_slice(&0x3040u32.to_le_bytes());
    b[0x400 + 16..0x400 + 20].copy_from_slice(&0x120u32.to_le_bytes());
    b[0x400 + 20..0x400 + 24].copy_from_slice(&4u32.to_le_bytes());
    b[0x400 + 24..0x400 + 28].copy_from_slice(&1u32.to_le_bytes());
    b[0x400 + 28..0x400 + 32].copy_from_slice(&0x3050u32.to_le_bytes());
    b[0x400 + 32..0x400 + 36].copy_from_slice(&0x3060u32.to_le_bytes());
    b[0x400 + 36..0x400 + 40].copy_from_slice(&0x3064u32.to_le_bytes());

    b[0x45C..0x460].copy_from_slice(&0x2222u32.to_le_bytes());
    b[0x460..0x464].copy_from_slice(&0x3068u32.to_le_bytes());
    b[0x464..0x466].copy_from_slice(&3u16.to_le_bytes());

    let dll = b"KERNEL32.dll\0";
    b[0x440..0x440 + dll.len()].copy_from_slice(dll);

    let name = b"Sleep\0";
    b[0x468..0x468 + name.len()].copy_from_slice(name);

    b
}

#[test]
fn pe_parser_extracts_core_metadata() {
    let meta = parse_pe_metadata(&pe_with_imports()).expect("valid test PE");
    assert_eq!(meta.machine, 0x8664);
    assert_eq!(meta.number_of_sections, 2);
    assert_eq!(meta.entry_point_rva, 0x2000);
    assert_eq!(meta.size_of_image, 0x4000);
    assert_eq!(meta.image_base, 0x0000_0001_8000_0000);
}

#[test]
fn native_loader_maps_sections_and_import_table() {
    let loaded = load_pe_image(&pe_with_imports()).expect("must load PE image");
    assert_eq!(loaded.sections.len(), 2);
    assert_eq!(loaded.imports.len(), 1);
    assert_eq!(loaded.imports[0].dll_name, "KERNEL32.dll");
    assert_eq!(loaded.imports[0].functions.len(), 2);

    match &loaded.imports[0].functions[0].symbol {
        PeImportSymbol::Name { hint, name } => {
            assert_eq!(*hint, 7);
            assert_eq!(name, "Sleep");
        }
        _ => panic!("expected named import"),
    }

    match loaded.imports[0].functions[1].symbol {
        PeImportSymbol::Ordinal(ord) => assert_eq!(ord, 0x0123),
        _ => panic!("expected ordinal import"),
    }

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
        "phase-6 stub while transport layer is built",
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
fn runtime_load_report_tracks_imports_exports_and_relocs() {
    let core = RuntimeCore::new();
    let report = core
        .load_pe_image(&pe_with_imports())
        .expect("runtime must load test image");
    assert_eq!(report.sections_loaded, 2);
    assert_eq!(report.imports_checked, 1);
    assert_eq!(report.import_symbol_count, 2);
    assert_eq!(report.imported_dlls, vec!["KERNEL32.dll".to_string()]);
    assert_eq!(report.exports_checked, 0);
    assert_eq!(report.relocations_count, 0);
    assert_eq!(
        report.import_details[0].symbols,
        vec!["Sleep".to_string(), "#291".to_string()]
    );
}

#[test]
fn mini_linker_resolves_named_and_ordinal_imports() {
    let core = RuntimeCore::new();
    let consumer = load_pe_image(&pe_with_imports()).expect("consumer image");
    let provider = load_pe_image(&pe_with_exports()).expect("provider image");

    let link = core.resolve_imports(&consumer, &[provider]);
    assert_eq!(link.total_symbols, 2);
    assert_eq!(link.resolved_symbols, 2);
    assert_eq!(link.unresolved_symbols, 0);
    assert_eq!(link.ambiguous_symbols, 0);

    assert_eq!(link.resolutions[0].symbol, "Sleep");
    assert!(link.resolutions[0].resolved);
    assert_eq!(link.resolutions[0].target_rva, Some(0x2222));

    assert_eq!(link.resolutions[1].symbol, "#291");
    assert!(link.resolutions[1].resolved);
    assert_eq!(link.resolutions[1].target_rva, Some(0x2222));
}

#[test]
fn linker_uses_cache_for_duplicate_symbols() {
    let core = RuntimeCore::new();
    let consumer = load_pe_image(&pe_with_duplicate_imports()).expect("consumer image");
    let provider = load_pe_image(&pe_with_exports()).expect("provider image");

    let link = core.resolve_imports(&consumer, &[provider]);
    assert_eq!(link.total_symbols, 3);
    assert_eq!(link.resolved_symbols, 3);
    assert_eq!(link.cache_hits, 1);
    assert_eq!(link.ambiguous_symbols, 0);
}

#[test]
fn linker_reports_ambiguity_with_multiple_candidate_modules() {
    let core = RuntimeCore::new();
    let consumer = load_pe_image(&pe_with_imports()).expect("consumer image");
    let provider_a = load_pe_image(&pe_with_exports()).expect("provider a");
    let provider_b = load_pe_image(&pe_with_exports()).expect("provider b");

    let link = core.resolve_imports(&consumer, &[provider_a, provider_b]);
    assert_eq!(link.total_symbols, 2);
    assert_eq!(link.resolved_symbols, 0);
    assert_eq!(link.unresolved_symbols, 2);
    assert_eq!(link.ambiguous_symbols, 2);
    assert_eq!(link.collisions.len(), 2);
}

#[test]
fn runtime_nt_core_process_thread_flow() {
    let mut core = RuntimeCore::new();

    let launch = core.launch_process("installer.exe", 0x1500);
    assert_eq!(
        core.process_id_from_handle(launch.process_handle)
            .expect("process handle resolves"),
        launch.pid
    );
    assert_eq!(
        core.thread_id_from_handle(launch.primary_thread_handle)
            .expect("thread handle resolves"),
        launch.primary_thread_id
    );

    let worker = core
        .spawn_thread(launch.pid, 0x2200)
        .expect("worker thread starts");
    core.set_thread_waiting(worker.tid, "network io")
        .expect("worker enters waiting");
    assert_eq!(
        core.thread(worker.tid).expect("worker exists").state,
        ThreadState::Waiting {
            reason: "network io".to_string()
        }
    );

    core.resume_thread(worker.tid).expect("worker resumes");
    core.exit_thread(worker.tid, 0)
        .expect("worker exits cleanly");
    assert_eq!(
        core.thread(worker.tid).expect("worker exists").state,
        ThreadState::Terminated { exit_code: 0 }
    );
    assert_eq!(
        core.process(launch.pid).expect("process exists").state,
        ProcessState::Running
    );

    core.terminate_process(launch.pid, 33)
        .expect("process termination succeeds");
    assert_eq!(
        core.process(launch.pid).expect("process exists").state,
        ProcessState::Terminated { exit_code: 33 }
    );
    assert_eq!(
        core.thread(launch.primary_thread_id)
            .expect("primary thread exists")
            .state,
        ThreadState::Terminated { exit_code: 33 }
    );

    let snapshot = core.nt_snapshot();
    assert_eq!(snapshot.process_count, 1);
    assert_eq!(snapshot.thread_count, 2);
    assert_eq!(snapshot.running_threads, 0);
    assert_eq!(snapshot.waiting_threads, 0);
    assert_eq!(snapshot.terminated_threads, 2);
    assert_eq!(snapshot.handle_count, 3);
}

#[test]
fn runtime_simulated_win32_calls_cover_process_thread_and_memory() {
    let mut core = RuntimeCore::new();
    core.register_phase8_kernel32_apis();

    let create = core
        .simulate_win32_call(Win32Call::CreateProcess {
            image_name: "office_setup.exe".to_string(),
            entry_point_rva: 0x1400,
        })
        .expect("create process call should succeed");

    let Win32CallResult::Process(launch) = create else {
        panic!("expected process launch");
    };

    for api in [
        "kernel32.CreateProcessW",
        "kernel32.VirtualAlloc",
        "kernel32.WriteProcessMemory",
        "kernel32.ReadProcessMemory",
        "kernel32.GetExitCodeProcess",
        "kernel32.CloseHandle",
    ] {
        let decision = core.dispatch_api(api).expect("api must be implemented");
        assert_eq!(decision.status, ApiStatus::Implemented);
    }

    let alloc = core
        .simulate_win32_call(Win32Call::VirtualAlloc {
            process_handle: launch.process_handle,
            size: 4097,
            protection: MemoryProtection::ReadWrite,
            label: Some("c2r-bootstrap".to_string()),
        })
        .expect("virtual alloc should succeed");
    let Win32CallResult::MemoryRegion { base, size } = alloc else {
        panic!("expected memory region");
    };
    assert_eq!(size, 0x2000);

    let write = core
        .simulate_win32_call(Win32Call::WriteProcessMemory {
            process_handle: launch.process_handle,
            address: base + 32,
            data: b"HELLO".to_vec(),
        })
        .expect("write process memory should succeed");
    assert_eq!(write, Win32CallResult::Size(5));

    let read = core
        .simulate_win32_call(Win32Call::ReadProcessMemory {
            process_handle: launch.process_handle,
            address: base + 32,
            size: 5,
        })
        .expect("read process memory should succeed");
    assert_eq!(read, Win32CallResult::Bytes(b"HELLO".to_vec()));

    let thread = core
        .simulate_win32_call(Win32Call::CreateThread {
            process_handle: launch.process_handle,
            start_rva: 0x2800,
        })
        .expect("create thread should succeed");
    let Win32CallResult::Thread(worker) = thread else {
        panic!("expected thread launch");
    };

    let exit_running = core
        .simulate_win32_call(Win32Call::GetExitCodeProcess {
            process_handle: launch.process_handle,
        })
        .expect("get exit code should succeed");
    assert_eq!(exit_running, Win32CallResult::ExitCode(STILL_ACTIVE));

    core.simulate_win32_call(Win32Call::TerminateProcess {
        process_handle: launch.process_handle,
        exit_code: 55,
    })
    .expect("terminate process should succeed");

    let exit_done = core
        .simulate_win32_call(Win32Call::GetExitCodeProcess {
            process_handle: launch.process_handle,
        })
        .expect("get exit code should succeed");
    assert_eq!(exit_done, Win32CallResult::ExitCode(55));

    core.simulate_win32_call(Win32Call::CloseHandle {
        handle: launch.process_handle,
    })
    .expect("close process handle should succeed");
    core.simulate_win32_call(Win32Call::CloseHandle {
        handle: worker.thread_handle,
    })
    .expect("close worker handle should succeed");

    let invalid = core
        .simulate_win32_call(Win32Call::CreateThread {
            process_handle: launch.process_handle,
            start_rva: 0x3000,
        })
        .expect_err("closed process handle cannot be reused");
    assert_eq!(invalid.to_string(), "invalid process handle: 0x00000100");
}

#[test]
fn runtime_phase9_sync_file_registry_calls() {
    let mut core = RuntimeCore::new();
    core.register_phase9_runtime_apis();

    for api in [
        "kernel32.WaitForSingleObject",
        "kernel32.CreateEventW",
        "kernel32.CreateFileW",
        "advapi32.RegSetValueExW",
    ] {
        let decision = core.dispatch_api(api).expect("api should be registered");
        assert_eq!(decision.status, ApiStatus::Implemented);
    }

    let create = core
        .simulate_win32_call(Win32Call::CreateProcess {
            image_name: "phase9.exe".to_string(),
            entry_point_rva: 0x1111,
        })
        .expect("process creation should succeed");
    let Win32CallResult::Process(launch) = create else {
        panic!("expected process launch");
    };

    let event = core
        .simulate_win32_call(Win32Call::CreateEvent {
            manual_reset: false,
            initial_state: false,
            name: Some("ready".to_string()),
        })
        .expect("create event should succeed");
    let Win32CallResult::Handle(event_handle) = event else {
        panic!("expected event handle");
    };

    let timeout = core
        .simulate_win32_call(Win32Call::WaitForSingleObject {
            handle: event_handle,
            timeout_ms: 0,
            waiter_tid: Some(launch.primary_thread_id),
        })
        .expect("wait single should succeed");
    assert_eq!(timeout, Win32CallResult::Wait(WaitStatus::Timeout));

    core.simulate_win32_call(Win32Call::SetEvent { event_handle })
        .expect("set event should succeed");

    let mutex = core
        .simulate_win32_call(Win32Call::CreateMutex {
            initial_owner_tid: None,
            name: Some("phase9-lock".to_string()),
        })
        .expect("create mutex should succeed");
    let Win32CallResult::Handle(mutex_handle) = mutex else {
        panic!("expected mutex handle");
    };

    let all = core
        .simulate_win32_call(Win32Call::WaitForMultipleObjects {
            handles: vec![event_handle, mutex_handle],
            wait_all: true,
            timeout_ms: 0,
            waiter_tid: Some(launch.primary_thread_id),
        })
        .expect("wait multiple should succeed");
    assert_eq!(
        all,
        Win32CallResult::WaitMultiple(WaitMultipleStatus::AllSignaled)
    );

    core.simulate_win32_call(Win32Call::ReleaseMutex { mutex_handle })
        .expect("release mutex should succeed");

    let file = core
        .simulate_win32_call(Win32Call::OpenFile {
            path: "C:/phase9/install.log".to_string(),
            create_if_missing: true,
        })
        .expect("open file should succeed");
    let Win32CallResult::Handle(file_handle) = file else {
        panic!("expected file handle");
    };
    core.simulate_win32_call(Win32Call::WriteFile {
        file_handle,
        data: b"stage=ready".to_vec(),
    })
    .expect("write file should succeed");
    core.simulate_win32_call(Win32Call::SetFilePointer {
        file_handle,
        position: 0,
    })
    .expect("seek file should succeed");
    let read = core
        .simulate_win32_call(Win32Call::ReadFile {
            file_handle,
            size: 11,
        })
        .expect("read file should succeed");
    assert_eq!(read, Win32CallResult::Bytes(b"stage=ready".to_vec()));

    core.simulate_win32_call(Win32Call::RegSetValue {
        key_path: "HKCU\\Software\\AIWR".to_string(),
        value_name: "Mode".to_string(),
        data: b"desktop".to_vec(),
    })
    .expect("reg set should succeed");
    let reg = core
        .simulate_win32_call(Win32Call::RegQueryValue {
            key_path: "HKCU\\Software\\AIWR".to_string(),
            value_name: "Mode".to_string(),
        })
        .expect("reg query should succeed");
    assert_eq!(reg, Win32CallResult::Bytes(b"desktop".to_vec()));
}
