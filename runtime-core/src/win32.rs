use crate::ntcore::{
    Handle, MemoryProtection, ProcessLaunch, ThreadId, ThreadLaunch, VirtualAddress,
    WaitMultipleStatus, WaitStatus,
};

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
    CreateEvent {
        manual_reset: bool,
        initial_state: bool,
        name: Option<String>,
    },
    SetEvent {
        event_handle: Handle,
    },
    ResetEvent {
        event_handle: Handle,
    },
    CreateMutex {
        initial_owner_tid: Option<ThreadId>,
        name: Option<String>,
    },
    ReleaseMutex {
        mutex_handle: Handle,
    },
    WaitForSingleObject {
        handle: Handle,
        timeout_ms: u32,
        waiter_tid: Option<ThreadId>,
    },
    WaitForMultipleObjects {
        handles: Vec<Handle>,
        wait_all: bool,
        timeout_ms: u32,
        waiter_tid: Option<ThreadId>,
    },
    OpenFile {
        path: String,
        create_if_missing: bool,
    },
    WriteFile {
        file_handle: Handle,
        data: Vec<u8>,
    },
    ReadFile {
        file_handle: Handle,
        size: usize,
    },
    SetFilePointer {
        file_handle: Handle,
        position: usize,
    },
    RegSetValue {
        key_path: String,
        value_name: String,
        data: Vec<u8>,
    },
    RegQueryValue {
        key_path: String,
        value_name: String,
    },
    RegDeleteValue {
        key_path: String,
        value_name: String,
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
    Handle(Handle),
    Wait(WaitStatus),
    WaitMultiple(WaitMultipleStatus),
    Bytes(Vec<u8>),
    ExitCode(u32),
    Size(usize),
    Position(u64),
    None,
}
