use std::collections::HashMap;
use std::fmt;

pub type ProcessId = u32;
pub type ThreadId = u32;
pub type Handle = u32;
pub type VirtualAddress = u64;

const PAGE_SIZE: u64 = 0x1000;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum MemoryProtection {
    ReadOnly,
    ReadWrite,
    ReadExecute,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MemoryRegion {
    pub owner_pid: ProcessId,
    pub base: VirtualAddress,
    pub size: usize,
    pub protection: MemoryProtection,
    pub label: Option<String>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum WaitStatus {
    Signaled,
    Timeout,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum WaitMultipleStatus {
    SignaledIndex(usize),
    AllSignaled,
    Timeout,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ProcessState {
    Running,
    Terminated { exit_code: u32 },
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ThreadState {
    Running,
    Waiting { reason: String },
    Terminated { exit_code: u32 },
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProcessRecord {
    pub pid: ProcessId,
    pub image_name: String,
    pub state: ProcessState,
    pub threads: Vec<ThreadId>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ThreadRecord {
    pub tid: ThreadId,
    pub owner_pid: ProcessId,
    pub start_rva: u32,
    pub state: ThreadState,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProcessLaunch {
    pub pid: ProcessId,
    pub process_handle: Handle,
    pub primary_thread_id: ThreadId,
    pub primary_thread_handle: Handle,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ThreadLaunch {
    pub tid: ThreadId,
    pub thread_handle: Handle,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct NtSnapshot {
    pub process_count: usize,
    pub thread_count: usize,
    pub running_threads: usize,
    pub waiting_threads: usize,
    pub terminated_threads: usize,
    pub handle_count: usize,
    pub memory_region_count: usize,
    pub allocated_bytes: usize,
    pub sync_object_count: usize,
    pub open_file_count: usize,
    pub registry_key_count: usize,
    pub registry_value_count: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum NtError {
    UnknownProcess(ProcessId),
    UnknownThread(ThreadId),
    ProcessTerminated(ProcessId),
    ThreadTerminated(ThreadId),
    UnknownMemoryRegion {
        pid: ProcessId,
        base: VirtualAddress,
    },
    MemoryOutOfBounds {
        pid: ProcessId,
        address: VirtualAddress,
        size: usize,
    },
    MemoryProtectionViolation {
        pid: ProcessId,
        address: VirtualAddress,
        protection: MemoryProtection,
    },
    InvalidMemorySize(usize),
    InvalidHandle(Handle),
    InvalidProcessHandle(Handle),
    InvalidThreadHandle(Handle),
    InvalidSyncHandle(Handle),
    InvalidFileHandle(Handle),
    FileNotFound(String),
    UnknownRegistryValue {
        key_path: String,
        value_name: String,
    },
}

impl fmt::Display for NtError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::UnknownProcess(pid) => write!(f, "unknown process id: {pid}"),
            Self::UnknownThread(tid) => write!(f, "unknown thread id: {tid}"),
            Self::ProcessTerminated(pid) => write!(f, "process is terminated: {pid}"),
            Self::ThreadTerminated(tid) => write!(f, "thread is terminated: {tid}"),
            Self::UnknownMemoryRegion { pid, base } => {
                write!(f, "unknown memory region for pid {pid}: 0x{base:016X}")
            }
            Self::MemoryOutOfBounds { pid, address, size } => write!(
                f,
                "memory access out of bounds for pid {pid}: addr=0x{address:016X}, size={size}"
            ),
            Self::MemoryProtectionViolation {
                pid,
                address,
                protection,
            } => write!(
                f,
                "memory protection violation for pid {pid}: addr=0x{address:016X}, protection={protection:?}"
            ),
            Self::InvalidMemorySize(size) => write!(f, "invalid memory size: {size}"),
            Self::InvalidHandle(handle) => write!(f, "invalid handle: 0x{handle:08X}"),
            Self::InvalidProcessHandle(handle) => {
                write!(f, "invalid process handle: 0x{handle:08X}")
            }
            Self::InvalidThreadHandle(handle) => {
                write!(f, "invalid thread handle: 0x{handle:08X}")
            }
            Self::InvalidSyncHandle(handle) => {
                write!(f, "invalid sync handle: 0x{handle:08X}")
            }
            Self::InvalidFileHandle(handle) => {
                write!(f, "invalid file handle: 0x{handle:08X}")
            }
            Self::FileNotFound(path) => write!(f, "file not found: {path}"),
            Self::UnknownRegistryValue {
                key_path,
                value_name,
            } => {
                write!(f, "registry value not found: {key_path}::{value_name}")
            }
        }
    }
}

impl std::error::Error for NtError {}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum HandleTarget {
    Process(ProcessId),
    Thread(ThreadId),
    Sync(SyncId),
    File(FileId),
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct MemoryRegionRecord {
    meta: MemoryRegion,
    bytes: Vec<u8>,
}

type SyncId = u32;
type FileId = u32;

#[derive(Debug, Clone, PartialEq, Eq)]
enum SyncObject {
    Event {
        manual_reset: bool,
        signaled: bool,
        name: Option<String>,
    },
    Mutex {
        owner_tid: Option<ThreadId>,
        name: Option<String>,
    },
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct FileHandleRecord {
    path: String,
    cursor: usize,
}

#[derive(Debug)]
pub struct NtCore {
    next_pid: ProcessId,
    next_tid: ThreadId,
    next_handle: Handle,
    next_mem_base: VirtualAddress,
    next_sync_id: SyncId,
    next_file_id: FileId,
    processes: HashMap<ProcessId, ProcessRecord>,
    threads: HashMap<ThreadId, ThreadRecord>,
    handles: HashMap<Handle, HandleTarget>,
    memory_regions: HashMap<ProcessId, Vec<MemoryRegionRecord>>,
    sync_objects: HashMap<SyncId, SyncObject>,
    file_contents: HashMap<String, Vec<u8>>,
    open_files: HashMap<FileId, FileHandleRecord>,
    registry: HashMap<String, HashMap<String, Vec<u8>>>,
}

impl Default for NtCore {
    fn default() -> Self {
        Self {
            next_pid: 1_000,
            next_tid: 10_000,
            next_handle: 0x100,
            next_mem_base: 0x0000_0000_1000_0000,
            next_sync_id: 1,
            next_file_id: 1,
            processes: HashMap::new(),
            threads: HashMap::new(),
            handles: HashMap::new(),
            memory_regions: HashMap::new(),
            sync_objects: HashMap::new(),
            file_contents: HashMap::new(),
            open_files: HashMap::new(),
            registry: HashMap::new(),
        }
    }
}

impl NtCore {
    pub fn new() -> Self {
        Self::default()
    }

    fn align_up(value: u64, align: u64) -> u64 {
        if value % align == 0 {
            value
        } else {
            value + (align - (value % align))
        }
    }

    fn alloc_handle(&mut self, target: HandleTarget) -> Handle {
        let handle = self.next_handle;
        self.next_handle = self.next_handle.saturating_add(4);
        self.handles.insert(handle, target);
        handle
    }

    fn process_running(&self, pid: ProcessId) -> Result<(), NtError> {
        let process = self
            .processes
            .get(&pid)
            .ok_or(NtError::UnknownProcess(pid))?;
        if matches!(process.state, ProcessState::Terminated { .. }) {
            return Err(NtError::ProcessTerminated(pid));
        }
        Ok(())
    }

    fn find_region_index(
        regions: &[MemoryRegionRecord],
        address: VirtualAddress,
        size: usize,
    ) -> Option<(usize, usize)> {
        let end = address.checked_add(size as u64)?;
        regions.iter().enumerate().find_map(|(idx, region)| {
            let start = region.meta.base;
            let region_end = start + region.meta.size as u64;
            if address >= start && end <= region_end {
                Some((idx, (address - start) as usize))
            } else {
                None
            }
        })
    }

    fn resolve_sync_id(&self, handle: Handle) -> Result<SyncId, NtError> {
        match self.handles.get(&handle) {
            Some(HandleTarget::Sync(id)) => Ok(*id),
            _ => Err(NtError::InvalidSyncHandle(handle)),
        }
    }

    fn resolve_file_id(&self, handle: Handle) -> Result<FileId, NtError> {
        match self.handles.get(&handle) {
            Some(HandleTarget::File(id)) => Ok(*id),
            _ => Err(NtError::InvalidFileHandle(handle)),
        }
    }

    fn is_handle_signaled(
        &self,
        handle: Handle,
        waiter_tid: Option<ThreadId>,
    ) -> Result<bool, NtError> {
        match self.handles.get(&handle).copied() {
            Some(HandleTarget::Process(pid)) => Ok(self
                .processes
                .get(&pid)
                .is_some_and(|p| matches!(p.state, ProcessState::Terminated { .. }))),
            Some(HandleTarget::Thread(tid)) => Ok(self
                .threads
                .get(&tid)
                .is_some_and(|t| matches!(t.state, ThreadState::Terminated { .. }))),
            Some(HandleTarget::Sync(sync_id)) => match self.sync_objects.get(&sync_id) {
                Some(SyncObject::Event { signaled, .. }) => Ok(*signaled),
                Some(SyncObject::Mutex { owner_tid, .. }) => {
                    Ok(owner_tid.is_none() || *owner_tid == waiter_tid)
                }
                None => Err(NtError::InvalidSyncHandle(handle)),
            },
            Some(HandleTarget::File(_)) => Ok(true),
            None => Err(NtError::InvalidHandle(handle)),
        }
    }

    fn consume_handle_signal(
        &mut self,
        handle: Handle,
        waiter_tid: Option<ThreadId>,
    ) -> Result<(), NtError> {
        match self.handles.get(&handle).copied() {
            Some(HandleTarget::Process(_))
            | Some(HandleTarget::Thread(_))
            | Some(HandleTarget::File(_)) => Ok(()),
            Some(HandleTarget::Sync(sync_id)) => {
                let sync = self
                    .sync_objects
                    .get_mut(&sync_id)
                    .ok_or(NtError::InvalidSyncHandle(handle))?;
                match sync {
                    SyncObject::Event {
                        manual_reset,
                        signaled,
                        ..
                    } => {
                        if *signaled && !*manual_reset {
                            *signaled = false;
                        }
                    }
                    SyncObject::Mutex { owner_tid, .. } => {
                        if owner_tid.is_none() {
                            *owner_tid = Some(waiter_tid.unwrap_or(0));
                        }
                    }
                }
                Ok(())
            }
            None => Err(NtError::InvalidHandle(handle)),
        }
    }

    pub fn launch_process(&mut self, image_name: &str, entry_point_rva: u32) -> ProcessLaunch {
        let pid = self.next_pid;
        self.next_pid = self.next_pid.saturating_add(1);

        let tid = self.next_tid;
        self.next_tid = self.next_tid.saturating_add(1);

        let process = ProcessRecord {
            pid,
            image_name: image_name.to_string(),
            state: ProcessState::Running,
            threads: vec![tid],
        };

        let thread = ThreadRecord {
            tid,
            owner_pid: pid,
            start_rva: entry_point_rva,
            state: ThreadState::Running,
        };

        self.processes.insert(pid, process);
        self.threads.insert(tid, thread);

        let process_handle = self.alloc_handle(HandleTarget::Process(pid));
        let primary_thread_handle = self.alloc_handle(HandleTarget::Thread(tid));

        ProcessLaunch {
            pid,
            process_handle,
            primary_thread_id: tid,
            primary_thread_handle,
        }
    }

    pub fn spawn_thread(
        &mut self,
        pid: ProcessId,
        start_rva: u32,
    ) -> Result<ThreadLaunch, NtError> {
        self.process_running(pid)?;

        let tid = self.next_tid;
        self.next_tid = self.next_tid.saturating_add(1);

        self.threads.insert(
            tid,
            ThreadRecord {
                tid,
                owner_pid: pid,
                start_rva,
                state: ThreadState::Running,
            },
        );

        if let Some(process) = self.processes.get_mut(&pid) {
            process.threads.push(tid);
        }

        Ok(ThreadLaunch {
            tid,
            thread_handle: self.alloc_handle(HandleTarget::Thread(tid)),
        })
    }

    pub fn set_thread_waiting(&mut self, tid: ThreadId, reason: &str) -> Result<(), NtError> {
        let owner_pid = self
            .threads
            .get(&tid)
            .ok_or(NtError::UnknownThread(tid))?
            .owner_pid;
        self.process_running(owner_pid)?;

        let thread = self
            .threads
            .get_mut(&tid)
            .ok_or(NtError::UnknownThread(tid))?;
        if matches!(thread.state, ThreadState::Terminated { .. }) {
            return Err(NtError::ThreadTerminated(tid));
        }

        thread.state = ThreadState::Waiting {
            reason: reason.to_string(),
        };
        Ok(())
    }

    pub fn resume_thread(&mut self, tid: ThreadId) -> Result<(), NtError> {
        let owner_pid = self
            .threads
            .get(&tid)
            .ok_or(NtError::UnknownThread(tid))?
            .owner_pid;
        self.process_running(owner_pid)?;

        let thread = self
            .threads
            .get_mut(&tid)
            .ok_or(NtError::UnknownThread(tid))?;
        if matches!(thread.state, ThreadState::Terminated { .. }) {
            return Err(NtError::ThreadTerminated(tid));
        }

        thread.state = ThreadState::Running;
        Ok(())
    }

    pub fn exit_thread(&mut self, tid: ThreadId, exit_code: u32) -> Result<(), NtError> {
        let owner_pid = {
            let thread = self
                .threads
                .get_mut(&tid)
                .ok_or(NtError::UnknownThread(tid))?;
            if matches!(thread.state, ThreadState::Terminated { .. }) {
                return Err(NtError::ThreadTerminated(tid));
            }
            thread.state = ThreadState::Terminated { exit_code };
            thread.owner_pid
        };

        let process_thread_ids = self
            .processes
            .get(&owner_pid)
            .map(|p| p.threads.clone())
            .ok_or(NtError::UnknownProcess(owner_pid))?;

        let all_terminated = process_thread_ids.iter().all(|thread_id| {
            self.threads
                .get(thread_id)
                .is_some_and(|t| matches!(t.state, ThreadState::Terminated { .. }))
        });

        if all_terminated {
            if let Some(process) = self.processes.get_mut(&owner_pid) {
                process.state = ProcessState::Terminated { exit_code };
            }
            self.memory_regions.remove(&owner_pid);
        }

        Ok(())
    }

    pub fn terminate_process(&mut self, pid: ProcessId, exit_code: u32) -> Result<(), NtError> {
        let thread_ids = self
            .processes
            .get(&pid)
            .map(|p| p.threads.clone())
            .ok_or(NtError::UnknownProcess(pid))?;

        for tid in thread_ids {
            if let Some(thread) = self.threads.get_mut(&tid) {
                thread.state = ThreadState::Terminated { exit_code };
            }
        }

        if let Some(process) = self.processes.get_mut(&pid) {
            process.state = ProcessState::Terminated { exit_code };
        }

        self.memory_regions.remove(&pid);
        Ok(())
    }

    pub fn alloc_memory(
        &mut self,
        pid: ProcessId,
        size: usize,
        protection: MemoryProtection,
        label: Option<&str>,
    ) -> Result<MemoryRegion, NtError> {
        self.process_running(pid)?;
        if size == 0 {
            return Err(NtError::InvalidMemorySize(size));
        }

        let aligned_size = Self::align_up(size as u64, PAGE_SIZE) as usize;
        let base = Self::align_up(self.next_mem_base, PAGE_SIZE);
        self.next_mem_base = base
            .saturating_add(aligned_size as u64)
            .saturating_add(PAGE_SIZE);

        let meta = MemoryRegion {
            owner_pid: pid,
            base,
            size: aligned_size,
            protection,
            label: label.map(|s| s.to_string()),
        };

        self.memory_regions
            .entry(pid)
            .or_default()
            .push(MemoryRegionRecord {
                meta: meta.clone(),
                bytes: vec![0u8; aligned_size],
            });

        Ok(meta)
    }

    pub fn free_memory(&mut self, pid: ProcessId, base: VirtualAddress) -> Result<(), NtError> {
        self.process_running(pid)?;

        let regions = self
            .memory_regions
            .get_mut(&pid)
            .ok_or(NtError::UnknownMemoryRegion { pid, base })?;

        let Some(idx) = regions.iter().position(|r| r.meta.base == base) else {
            return Err(NtError::UnknownMemoryRegion { pid, base });
        };

        regions.remove(idx);
        if regions.is_empty() {
            self.memory_regions.remove(&pid);
        }

        Ok(())
    }

    pub fn set_memory_protection(
        &mut self,
        pid: ProcessId,
        base: VirtualAddress,
        protection: MemoryProtection,
    ) -> Result<MemoryRegion, NtError> {
        self.process_running(pid)?;

        let regions = self
            .memory_regions
            .get_mut(&pid)
            .ok_or(NtError::UnknownMemoryRegion { pid, base })?;

        let Some(region) = regions.iter_mut().find(|r| r.meta.base == base) else {
            return Err(NtError::UnknownMemoryRegion { pid, base });
        };

        region.meta.protection = protection;
        Ok(region.meta.clone())
    }

    pub fn write_memory(
        &mut self,
        pid: ProcessId,
        address: VirtualAddress,
        data: &[u8],
    ) -> Result<usize, NtError> {
        self.process_running(pid)?;

        let regions = self
            .memory_regions
            .get_mut(&pid)
            .ok_or(NtError::MemoryOutOfBounds {
                pid,
                address,
                size: data.len(),
            })?;

        let Some((idx, offset)) = Self::find_region_index(regions, address, data.len()) else {
            return Err(NtError::MemoryOutOfBounds {
                pid,
                address,
                size: data.len(),
            });
        };

        if matches!(regions[idx].meta.protection, MemoryProtection::ReadOnly) {
            return Err(NtError::MemoryProtectionViolation {
                pid,
                address,
                protection: regions[idx].meta.protection,
            });
        }

        let end = offset + data.len();
        regions[idx].bytes[offset..end].copy_from_slice(data);
        Ok(data.len())
    }

    pub fn read_memory(
        &self,
        pid: ProcessId,
        address: VirtualAddress,
        size: usize,
    ) -> Result<Vec<u8>, NtError> {
        self.process_running(pid)?;

        let regions = self
            .memory_regions
            .get(&pid)
            .ok_or(NtError::MemoryOutOfBounds { pid, address, size })?;

        let Some((idx, offset)) = Self::find_region_index(regions, address, size) else {
            return Err(NtError::MemoryOutOfBounds { pid, address, size });
        };

        let end = offset + size;
        Ok(regions[idx].bytes[offset..end].to_vec())
    }

    pub fn memory_region(
        &self,
        pid: ProcessId,
        base: VirtualAddress,
    ) -> Result<MemoryRegion, NtError> {
        let process = self
            .processes
            .get(&pid)
            .ok_or(NtError::UnknownProcess(pid))?;
        if matches!(process.state, ProcessState::Terminated { .. }) {
            return Err(NtError::ProcessTerminated(pid));
        }

        self.memory_regions
            .get(&pid)
            .and_then(|regions| regions.iter().find(|r| r.meta.base == base))
            .map(|r| r.meta.clone())
            .ok_or(NtError::UnknownMemoryRegion { pid, base })
    }

    pub fn list_memory_regions(&self, pid: ProcessId) -> Result<Vec<MemoryRegion>, NtError> {
        let process = self
            .processes
            .get(&pid)
            .ok_or(NtError::UnknownProcess(pid))?;
        if matches!(process.state, ProcessState::Terminated { .. }) {
            return Err(NtError::ProcessTerminated(pid));
        }

        let mut out = self
            .memory_regions
            .get(&pid)
            .map(|regions| regions.iter().map(|r| r.meta.clone()).collect::<Vec<_>>())
            .unwrap_or_default();
        out.sort_by_key(|r| r.base);
        Ok(out)
    }

    pub fn create_event(
        &mut self,
        manual_reset: bool,
        initial_state: bool,
        name: Option<&str>,
    ) -> Handle {
        let sync_id = self.next_sync_id;
        self.next_sync_id = self.next_sync_id.saturating_add(1);
        self.sync_objects.insert(
            sync_id,
            SyncObject::Event {
                manual_reset,
                signaled: initial_state,
                name: name.map(|s| s.to_string()),
            },
        );
        self.alloc_handle(HandleTarget::Sync(sync_id))
    }

    pub fn create_mutex(
        &mut self,
        initial_owner_tid: Option<ThreadId>,
        name: Option<&str>,
    ) -> Handle {
        let sync_id = self.next_sync_id;
        self.next_sync_id = self.next_sync_id.saturating_add(1);
        self.sync_objects.insert(
            sync_id,
            SyncObject::Mutex {
                owner_tid: initial_owner_tid,
                name: name.map(|s| s.to_string()),
            },
        );
        self.alloc_handle(HandleTarget::Sync(sync_id))
    }

    pub fn set_event(&mut self, event_handle: Handle) -> Result<(), NtError> {
        let sync_id = self.resolve_sync_id(event_handle)?;
        let sync = self
            .sync_objects
            .get_mut(&sync_id)
            .ok_or(NtError::InvalidSyncHandle(event_handle))?;
        match sync {
            SyncObject::Event { signaled, .. } => {
                *signaled = true;
                Ok(())
            }
            _ => Err(NtError::InvalidSyncHandle(event_handle)),
        }
    }

    pub fn reset_event(&mut self, event_handle: Handle) -> Result<(), NtError> {
        let sync_id = self.resolve_sync_id(event_handle)?;
        let sync = self
            .sync_objects
            .get_mut(&sync_id)
            .ok_or(NtError::InvalidSyncHandle(event_handle))?;
        match sync {
            SyncObject::Event { signaled, .. } => {
                *signaled = false;
                Ok(())
            }
            _ => Err(NtError::InvalidSyncHandle(event_handle)),
        }
    }

    pub fn release_mutex(&mut self, mutex_handle: Handle) -> Result<(), NtError> {
        let sync_id = self.resolve_sync_id(mutex_handle)?;
        let sync = self
            .sync_objects
            .get_mut(&sync_id)
            .ok_or(NtError::InvalidSyncHandle(mutex_handle))?;
        match sync {
            SyncObject::Mutex { owner_tid, .. } => {
                *owner_tid = None;
                Ok(())
            }
            _ => Err(NtError::InvalidSyncHandle(mutex_handle)),
        }
    }

    pub fn wait_for_single_object(
        &mut self,
        handle: Handle,
        _timeout_ms: u32,
        waiter_tid: Option<ThreadId>,
    ) -> Result<WaitStatus, NtError> {
        if self.is_handle_signaled(handle, waiter_tid)? {
            self.consume_handle_signal(handle, waiter_tid)?;
            Ok(WaitStatus::Signaled)
        } else {
            Ok(WaitStatus::Timeout)
        }
    }

    pub fn wait_for_multiple_objects(
        &mut self,
        handles: &[Handle],
        wait_all: bool,
        _timeout_ms: u32,
        waiter_tid: Option<ThreadId>,
    ) -> Result<WaitMultipleStatus, NtError> {
        if handles.is_empty() {
            return Ok(WaitMultipleStatus::Timeout);
        }

        if wait_all {
            for handle in handles {
                if !self.is_handle_signaled(*handle, waiter_tid)? {
                    return Ok(WaitMultipleStatus::Timeout);
                }
            }
            for handle in handles {
                self.consume_handle_signal(*handle, waiter_tid)?;
            }
            Ok(WaitMultipleStatus::AllSignaled)
        } else {
            for (idx, handle) in handles.iter().enumerate() {
                if self.is_handle_signaled(*handle, waiter_tid)? {
                    self.consume_handle_signal(*handle, waiter_tid)?;
                    return Ok(WaitMultipleStatus::SignaledIndex(idx));
                }
            }
            Ok(WaitMultipleStatus::Timeout)
        }
    }

    pub fn open_file(&mut self, path: &str, create_if_missing: bool) -> Result<Handle, NtError> {
        if create_if_missing {
            self.file_contents.entry(path.to_string()).or_default();
        } else if !self.file_contents.contains_key(path) {
            return Err(NtError::FileNotFound(path.to_string()));
        }

        let file_id = self.next_file_id;
        self.next_file_id = self.next_file_id.saturating_add(1);
        self.open_files.insert(
            file_id,
            FileHandleRecord {
                path: path.to_string(),
                cursor: 0,
            },
        );

        Ok(self.alloc_handle(HandleTarget::File(file_id)))
    }

    pub fn write_file(&mut self, file_handle: Handle, data: &[u8]) -> Result<usize, NtError> {
        let file_id = self.resolve_file_id(file_handle)?;
        let file = self
            .open_files
            .get_mut(&file_id)
            .ok_or(NtError::InvalidFileHandle(file_handle))?;

        let content = self.file_contents.entry(file.path.clone()).or_default();

        if file.cursor > content.len() {
            content.resize(file.cursor, 0);
        }

        let end = file.cursor + data.len();
        if end > content.len() {
            content.resize(end, 0);
        }

        content[file.cursor..end].copy_from_slice(data);
        file.cursor = end;
        Ok(data.len())
    }

    pub fn read_file(&mut self, file_handle: Handle, size: usize) -> Result<Vec<u8>, NtError> {
        let file_id = self.resolve_file_id(file_handle)?;
        let file = self
            .open_files
            .get_mut(&file_id)
            .ok_or(NtError::InvalidFileHandle(file_handle))?;

        let content = self
            .file_contents
            .get(&file.path)
            .ok_or_else(|| NtError::FileNotFound(file.path.clone()))?;

        let start = file.cursor;
        let end = start.saturating_add(size).min(content.len());
        file.cursor = end;
        Ok(content[start..end].to_vec())
    }

    pub fn set_file_pointer(
        &mut self,
        file_handle: Handle,
        position: usize,
    ) -> Result<u64, NtError> {
        let file_id = self.resolve_file_id(file_handle)?;
        let file = self
            .open_files
            .get_mut(&file_id)
            .ok_or(NtError::InvalidFileHandle(file_handle))?;
        file.cursor = position;
        Ok(position as u64)
    }

    pub fn file_content(&self, path: &str) -> Option<Vec<u8>> {
        self.file_contents.get(path).cloned()
    }

    pub fn registry_set_value(&mut self, key_path: &str, value_name: &str, data: &[u8]) {
        self.registry
            .entry(key_path.to_string())
            .or_default()
            .insert(value_name.to_string(), data.to_vec());
    }

    pub fn registry_get_value(&self, key_path: &str, value_name: &str) -> Result<Vec<u8>, NtError> {
        self.registry
            .get(key_path)
            .and_then(|values| values.get(value_name))
            .cloned()
            .ok_or_else(|| NtError::UnknownRegistryValue {
                key_path: key_path.to_string(),
                value_name: value_name.to_string(),
            })
    }

    pub fn registry_delete_value(
        &mut self,
        key_path: &str,
        value_name: &str,
    ) -> Result<(), NtError> {
        let Some(values) = self.registry.get_mut(key_path) else {
            return Err(NtError::UnknownRegistryValue {
                key_path: key_path.to_string(),
                value_name: value_name.to_string(),
            });
        };
        if values.remove(value_name).is_none() {
            return Err(NtError::UnknownRegistryValue {
                key_path: key_path.to_string(),
                value_name: value_name.to_string(),
            });
        }
        if values.is_empty() {
            self.registry.remove(key_path);
        }
        Ok(())
    }

    pub fn close_handle(&mut self, handle: Handle) -> Result<(), NtError> {
        let Some(target) = self.handles.remove(&handle) else {
            return Err(NtError::InvalidHandle(handle));
        };

        if let HandleTarget::File(file_id) = target {
            self.open_files.remove(&file_id);
        }

        Ok(())
    }

    pub fn process(&self, pid: ProcessId) -> Option<&ProcessRecord> {
        self.processes.get(&pid)
    }

    pub fn thread(&self, tid: ThreadId) -> Option<&ThreadRecord> {
        self.threads.get(&tid)
    }

    pub fn process_id_from_handle(&self, handle: Handle) -> Result<ProcessId, NtError> {
        match self.handles.get(&handle) {
            Some(HandleTarget::Process(pid)) => Ok(*pid),
            _ => Err(NtError::InvalidProcessHandle(handle)),
        }
    }

    pub fn thread_id_from_handle(&self, handle: Handle) -> Result<ThreadId, NtError> {
        match self.handles.get(&handle) {
            Some(HandleTarget::Thread(tid)) => Ok(*tid),
            _ => Err(NtError::InvalidThreadHandle(handle)),
        }
    }

    pub fn snapshot(&self) -> NtSnapshot {
        let mut running_threads = 0usize;
        let mut waiting_threads = 0usize;
        let mut terminated_threads = 0usize;

        for thread in self.threads.values() {
            match thread.state {
                ThreadState::Running => running_threads += 1,
                ThreadState::Waiting { .. } => waiting_threads += 1,
                ThreadState::Terminated { .. } => terminated_threads += 1,
            }
        }

        let memory_region_count = self.memory_regions.values().map(Vec::len).sum();
        let allocated_bytes = self
            .memory_regions
            .values()
            .flat_map(|regions| regions.iter())
            .map(|r| r.meta.size)
            .sum();

        let registry_key_count = self.registry.len();
        let registry_value_count = self.registry.values().map(HashMap::len).sum();

        NtSnapshot {
            process_count: self.processes.len(),
            thread_count: self.threads.len(),
            running_threads,
            waiting_threads,
            terminated_threads,
            handle_count: self.handles.len(),
            memory_region_count,
            allocated_bytes,
            sync_object_count: self.sync_objects.len(),
            open_file_count: self.open_files.len(),
            registry_key_count,
            registry_value_count,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{
        MemoryProtection, NtCore, NtError, ProcessState, ThreadState, WaitMultipleStatus,
        WaitStatus,
    };

    #[test]
    fn launch_process_creates_primary_thread_and_handles() {
        let mut nt = NtCore::new();
        let launch = nt.launch_process("setup.exe", 0x1000);

        assert_eq!(launch.pid, 1_000);
        assert_eq!(launch.primary_thread_id, 10_000);
        assert_eq!(
            nt.process_id_from_handle(launch.process_handle)
                .expect("valid process handle"),
            launch.pid
        );
        assert_eq!(
            nt.thread_id_from_handle(launch.primary_thread_handle)
                .expect("valid thread handle"),
            launch.primary_thread_id
        );

        let process = nt.process(launch.pid).expect("process must exist");
        assert_eq!(process.image_name, "setup.exe");
        assert_eq!(process.threads, vec![launch.primary_thread_id]);
        assert_eq!(process.state, ProcessState::Running);
    }

    #[test]
    fn thread_wait_and_resume_transitions() {
        let mut nt = NtCore::new();
        let launch = nt.launch_process("setup.exe", 0x1000);
        let worker = nt
            .spawn_thread(launch.pid, 0x2000)
            .expect("worker thread must launch");

        nt.set_thread_waiting(worker.tid, "io wait")
            .expect("must switch to waiting");
        let waiting = nt.thread(worker.tid).expect("worker must exist");
        assert_eq!(
            waiting.state,
            ThreadState::Waiting {
                reason: "io wait".to_string()
            }
        );

        nt.resume_thread(worker.tid)
            .expect("must switch to running");
        let running = nt.thread(worker.tid).expect("worker must exist");
        assert_eq!(running.state, ThreadState::Running);
    }

    #[test]
    fn exiting_last_thread_terminates_process() {
        let mut nt = NtCore::new();
        let launch = nt.launch_process("setup.exe", 0x1000);
        nt.exit_thread(launch.primary_thread_id, 11)
            .expect("must exit primary thread");

        let process = nt.process(launch.pid).expect("process must exist");
        assert_eq!(process.state, ProcessState::Terminated { exit_code: 11 });
    }

    #[test]
    fn terminate_process_cascades_to_threads() {
        let mut nt = NtCore::new();
        let launch = nt.launch_process("setup.exe", 0x1000);
        let worker = nt
            .spawn_thread(launch.pid, 0x2000)
            .expect("worker thread must launch");

        nt.terminate_process(launch.pid, 42)
            .expect("must terminate process");

        let process = nt.process(launch.pid).expect("process must exist");
        assert_eq!(process.state, ProcessState::Terminated { exit_code: 42 });

        assert_eq!(
            nt.thread(launch.primary_thread_id)
                .expect("primary thread must exist")
                .state,
            ThreadState::Terminated { exit_code: 42 }
        );
        assert_eq!(
            nt.thread(worker.tid)
                .expect("worker thread must exist")
                .state,
            ThreadState::Terminated { exit_code: 42 }
        );
    }

    #[test]
    fn cannot_spawn_thread_in_terminated_process() {
        let mut nt = NtCore::new();
        let launch = nt.launch_process("setup.exe", 0x1000);
        nt.terminate_process(launch.pid, 1)
            .expect("must terminate process");

        let err = nt
            .spawn_thread(launch.pid, 0x2000)
            .expect_err("terminated process cannot spawn threads");
        assert_eq!(err, NtError::ProcessTerminated(launch.pid));
    }

    #[test]
    fn virtual_memory_alloc_write_read_protect_and_free() {
        let mut nt = NtCore::new();
        let launch = nt.launch_process("setup.exe", 0x1000);

        let region = nt
            .alloc_memory(
                launch.pid,
                3000,
                MemoryProtection::ReadWrite,
                Some("installer heap"),
            )
            .expect("allocation should succeed");
        assert_eq!(region.size, 0x1000);

        nt.write_memory(launch.pid, region.base, b"ABCD")
            .expect("write should succeed");
        let data = nt
            .read_memory(launch.pid, region.base, 4)
            .expect("read should succeed");
        assert_eq!(data, b"ABCD".to_vec());

        let ro = nt
            .set_memory_protection(launch.pid, region.base, MemoryProtection::ReadOnly)
            .expect("protect should succeed");
        assert_eq!(ro.protection, MemoryProtection::ReadOnly);

        let err = nt
            .write_memory(launch.pid, region.base, b"E")
            .expect_err("readonly memory must reject writes");
        assert!(matches!(err, NtError::MemoryProtectionViolation { .. }));

        nt.free_memory(launch.pid, region.base)
            .expect("free should succeed");
        let list = nt
            .list_memory_regions(launch.pid)
            .expect("list should succeed");
        assert!(list.is_empty());
    }

    #[test]
    fn closing_handle_invalidates_resolution() {
        let mut nt = NtCore::new();
        let launch = nt.launch_process("setup.exe", 0x1000);

        nt.close_handle(launch.process_handle)
            .expect("first close succeeds");
        let err = nt
            .process_id_from_handle(launch.process_handle)
            .expect_err("closed handle should be invalid");
        assert_eq!(err, NtError::InvalidProcessHandle(launch.process_handle));

        let err = nt
            .close_handle(launch.process_handle)
            .expect_err("closing twice must fail");
        assert_eq!(err, NtError::InvalidHandle(launch.process_handle));
    }

    #[test]
    fn process_termination_releases_memory_regions() {
        let mut nt = NtCore::new();
        let launch = nt.launch_process("setup.exe", 0x1000);

        nt.alloc_memory(launch.pid, 4096, MemoryProtection::ReadWrite, None)
            .expect("allocation should succeed");
        assert_eq!(nt.snapshot().memory_region_count, 1);

        nt.terminate_process(launch.pid, 9)
            .expect("process terminate should succeed");
        assert_eq!(nt.snapshot().memory_region_count, 0);

        let err = nt
            .alloc_memory(launch.pid, 4096, MemoryProtection::ReadWrite, None)
            .expect_err("terminated process should reject new memory alloc");
        assert_eq!(err, NtError::ProcessTerminated(launch.pid));
    }

    #[test]
    fn event_and_mutex_waits_are_deterministic() {
        let mut nt = NtCore::new();
        let launch = nt.launch_process("setup.exe", 0x1000);

        let evt = nt.create_event(false, false, Some("bootstrap-ready"));
        assert_eq!(
            nt.wait_for_single_object(evt, 0, Some(launch.primary_thread_id))
                .expect("wait should succeed"),
            WaitStatus::Timeout
        );

        nt.set_event(evt).expect("set event should succeed");
        assert_eq!(
            nt.wait_for_single_object(evt, 0, Some(launch.primary_thread_id))
                .expect("wait should succeed"),
            WaitStatus::Signaled
        );
        assert_eq!(
            nt.wait_for_single_object(evt, 0, Some(launch.primary_thread_id))
                .expect("auto-reset event should no longer be signaled"),
            WaitStatus::Timeout
        );

        let mtx = nt.create_mutex(None, Some("global-lock"));
        assert_eq!(
            nt.wait_for_single_object(mtx, 0, Some(launch.primary_thread_id))
                .expect("mutex wait should acquire"),
            WaitStatus::Signaled
        );
        assert_eq!(
            nt.wait_for_single_object(mtx, 0, Some(99_999))
                .expect("mutex wait should report timeout for other owner"),
            WaitStatus::Timeout
        );
        nt.release_mutex(mtx).expect("release mutex should succeed");

        let all = nt
            .wait_for_multiple_objects(&[evt, mtx], true, 0, Some(launch.primary_thread_id))
            .expect("wait multiple should succeed");
        assert_eq!(all, WaitMultipleStatus::Timeout);
        nt.set_event(evt).expect("set event should succeed");
        let all = nt
            .wait_for_multiple_objects(&[evt, mtx], true, 0, Some(launch.primary_thread_id))
            .expect("wait multiple should succeed");
        assert_eq!(all, WaitMultipleStatus::AllSignaled);
    }

    #[test]
    fn file_and_registry_adapters_store_roundtrip_data() {
        let mut nt = NtCore::new();

        let file = nt
            .open_file("C:/temp/setup.log", true)
            .expect("open file should succeed");
        nt.write_file(file, b"hello")
            .expect("write file should succeed");
        nt.set_file_pointer(file, 0)
            .expect("seek file should succeed");
        let data = nt.read_file(file, 5).expect("read file should succeed");
        assert_eq!(data, b"hello".to_vec());
        assert_eq!(
            nt.file_content("C:/temp/setup.log")
                .expect("content should exist"),
            b"hello".to_vec()
        );

        nt.registry_set_value("HKCU\\Software\\AIWR", "InstallDir", b"C:\\Apps");
        assert_eq!(
            nt.registry_get_value("HKCU\\Software\\AIWR", "InstallDir")
                .expect("registry value should exist"),
            b"C:\\Apps".to_vec()
        );
        nt.registry_delete_value("HKCU\\Software\\AIWR", "InstallDir")
            .expect("delete registry value should succeed");
        let err = nt
            .registry_get_value("HKCU\\Software\\AIWR", "InstallDir")
            .expect_err("deleted registry value should be gone");
        assert!(matches!(err, NtError::UnknownRegistryValue { .. }));
    }
}
