use crate::ntcore::{Handle, MemoryProtection, ProcessLaunch, ThreadLaunch, VirtualAddress};

pub const STILL_ACTIVE: u32 = 259;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Win32Call {
    CreateProcess {
        image_name: String,
        entry_point_rva: u32,
    },
    CreateThread {
        process_handle: Handle,
        start_rva: u32,
    },
    VirtualAlloc {
        process_handle: Handle,
        size: usize,
        protection: MemoryProtection,
        label: Option<String>,
    },
    VirtualProtect {
        process_handle: Handle,
        base: VirtualAddress,
        protection: MemoryProtection,
    },
    VirtualFree {
        process_handle: Handle,
        base: VirtualAddress,
    },
    WriteProcessMemory {
        process_handle: Handle,
        address: VirtualAddress,
        data: Vec<u8>,
    },
    ReadProcessMemory {
        process_handle: Handle,
        address: VirtualAddress,
        size: usize,
    },
    TerminateProcess {
        process_handle: Handle,
        exit_code: u32,
    },
    GetExitCodeProcess {
        process_handle: Handle,
    },
    CloseHandle {
        handle: Handle,
    },
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Win32CallResult {
    Process(ProcessLaunch),
    Thread(ThreadLaunch),
    MemoryRegion { base: VirtualAddress, size: usize },
    Bytes(Vec<u8>),
    ExitCode(u32),
    Size(usize),
    None,
}
