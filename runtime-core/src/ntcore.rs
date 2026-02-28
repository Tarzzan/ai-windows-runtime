use std::collections::HashMap;
use std::fmt;

pub type ProcessId = u32;
pub type ThreadId = u32;
pub type Handle = u32;

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
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum NtError {
    UnknownProcess(ProcessId),
    UnknownThread(ThreadId),
    ProcessTerminated(ProcessId),
    ThreadTerminated(ThreadId),
    InvalidProcessHandle(Handle),
    InvalidThreadHandle(Handle),
}

impl fmt::Display for NtError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::UnknownProcess(pid) => write!(f, "unknown process id: {pid}"),
            Self::UnknownThread(tid) => write!(f, "unknown thread id: {tid}"),
            Self::ProcessTerminated(pid) => write!(f, "process is terminated: {pid}"),
            Self::ThreadTerminated(tid) => write!(f, "thread is terminated: {tid}"),
            Self::InvalidProcessHandle(handle) => {
                write!(f, "invalid process handle: 0x{handle:08X}")
            }
            Self::InvalidThreadHandle(handle) => {
                write!(f, "invalid thread handle: 0x{handle:08X}")
            }
        }
    }
}

impl std::error::Error for NtError {}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum HandleTarget {
    Process(ProcessId),
    Thread(ThreadId),
}

#[derive(Debug)]
pub struct NtCore {
    next_pid: ProcessId,
    next_tid: ThreadId,
    next_handle: Handle,
    processes: HashMap<ProcessId, ProcessRecord>,
    threads: HashMap<ThreadId, ThreadRecord>,
    handles: HashMap<Handle, HandleTarget>,
}

impl Default for NtCore {
    fn default() -> Self {
        Self {
            next_pid: 1_000,
            next_tid: 10_000,
            next_handle: 0x100,
            processes: HashMap::new(),
            threads: HashMap::new(),
            handles: HashMap::new(),
        }
    }
}

impl NtCore {
    pub fn new() -> Self {
        Self::default()
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

        NtSnapshot {
            process_count: self.processes.len(),
            thread_count: self.threads.len(),
            running_threads,
            waiting_threads,
            terminated_threads,
            handle_count: self.handles.len(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{NtCore, NtError, ProcessState, ThreadState};

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
}
