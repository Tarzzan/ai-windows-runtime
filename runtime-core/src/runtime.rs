use std::collections::{HashMap, HashSet};

use crate::dispatcher::{ApiDispatcher, DispatchDecision, DispatchError};
use crate::ntcore::{
    Handle, MemoryProtection, MemoryRegion, NtCore, NtError, NtSnapshot, ProcessId, ProcessLaunch,
    ProcessRecord, ProcessState, ThreadId, ThreadLaunch, ThreadRecord, VirtualAddress,
    WaitMultipleStatus, WaitStatus,
};
use crate::pe::{LoadedPeImage, PeError, PeExport, PeImportSymbol, PeMetadata, load_pe_image};
use crate::telemetry::{RuntimeTelemetryEvent, TelemetryRecorder};
use crate::win32::{STILL_ACTIVE, Win32Call, Win32CallResult};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct DllImportReport {
    pub dll_name: String,
    pub symbols: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LoadReport {
    pub metadata: PeMetadata,
    pub image_base: u64,
    pub mapped_image_size: usize,
    pub sections_loaded: usize,
    pub imports_checked: usize,
    pub import_symbol_count: usize,
    pub imported_dlls: Vec<String>,
    pub import_details: Vec<DllImportReport>,
    pub exports_checked: usize,
    pub exported_dll: Option<String>,
    pub relocations_count: usize,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ImportResolution {
    pub dll_name: String,
    pub symbol: String,
    pub resolved: bool,
    pub target_module: Option<String>,
    pub target_rva: Option<u32>,
    pub ambiguous: bool,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SymbolCollision {
    pub dll_name: String,
    pub symbol: String,
    pub candidate_modules: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LinkReport {
    pub total_symbols: usize,
    pub resolved_symbols: usize,
    pub unresolved_symbols: usize,
    pub ambiguous_symbols: usize,
    pub cache_hits: usize,
    pub resolutions: Vec<ImportResolution>,
    pub collisions: Vec<SymbolCollision>,
}

#[derive(Debug, Clone)]
struct CachedLookup {
    resolution: ImportResolution,
    collision_modules: Vec<String>,
}

#[derive(Debug, Default)]
pub struct RuntimeCore {
    dispatcher: ApiDispatcher,
    nt_core: NtCore,
    telemetry: TelemetryRecorder,
}

fn normalize_dll_name(name: &str) -> String {
    let lower = name.to_ascii_lowercase();
    lower
        .strip_suffix(".dll")
        .map_or(lower.clone(), |s| s.to_string())
}

fn symbol_label(symbol: &PeImportSymbol) -> String {
    match symbol {
        PeImportSymbol::Name { name, .. } => name.clone(),
        PeImportSymbol::Ordinal(ord) => format!("#{ord}"),
    }
}

fn resolve_export<'a>(exports: &'a [PeExport], symbol: &PeImportSymbol) -> Option<&'a PeExport> {
    match symbol {
        PeImportSymbol::Name { name, .. } => exports.iter().find(|e| {
            e.name
                .as_deref()
                .is_some_and(|n| n.eq_ignore_ascii_case(name))
        }),
        PeImportSymbol::Ordinal(ord) => exports.iter().find(|e| e.ordinal == *ord as u32),
    }
}

fn win32_call_name(call: &Win32Call) -> &'static str {
    match call {
        Win32Call::CreateProcess { .. } => "CreateProcessW",
        Win32Call::CreateThread { .. } => "CreateThread",
        Win32Call::VirtualAlloc { .. } => "VirtualAlloc",
        Win32Call::VirtualProtect { .. } => "VirtualProtect",
        Win32Call::VirtualFree { .. } => "VirtualFree",
        Win32Call::WriteProcessMemory { .. } => "WriteProcessMemory",
        Win32Call::ReadProcessMemory { .. } => "ReadProcessMemory",
        Win32Call::CreateEvent { .. } => "CreateEventW",
        Win32Call::SetEvent { .. } => "SetEvent",
        Win32Call::ResetEvent { .. } => "ResetEvent",
        Win32Call::CreateMutex { .. } => "CreateMutexW",
        Win32Call::ReleaseMutex { .. } => "ReleaseMutex",
        Win32Call::WaitForSingleObject { .. } => "WaitForSingleObject",
        Win32Call::WaitForMultipleObjects { .. } => "WaitForMultipleObjects",
        Win32Call::OpenFile { .. } => "CreateFileW",
        Win32Call::WriteFile { .. } => "WriteFile",
        Win32Call::ReadFile { .. } => "ReadFile",
        Win32Call::SetFilePointer { .. } => "SetFilePointerEx",
        Win32Call::RegSetValue { .. } => "RegSetValueExW",
        Win32Call::RegQueryValue { .. } => "RegQueryValueExW",
        Win32Call::RegDeleteValue { .. } => "RegDeleteValueW",
        Win32Call::TerminateProcess { .. } => "TerminateProcess",
        Win32Call::GetExitCodeProcess { .. } => "GetExitCodeProcess",
        Win32Call::CloseHandle { .. } => "CloseHandle",
    }
}

fn win32_result_label(result: &Win32CallResult) -> &'static str {
    match result {
        Win32CallResult::Process(_) => "process",
        Win32CallResult::Thread(_) => "thread",
        Win32CallResult::MemoryRegion { .. } => "memory-region",
        Win32CallResult::Handle(_) => "handle",
        Win32CallResult::Wait(_) => "wait",
        Win32CallResult::WaitMultiple(_) => "wait-multiple",
        Win32CallResult::Bytes(_) => "bytes",
        Win32CallResult::ExitCode(_) => "exit-code",
        Win32CallResult::Size(_) => "size",
        Win32CallResult::Position(_) => "position",
        Win32CallResult::None => "none",
    }
}

impl RuntimeCore {
    pub fn new() -> Self {
        Self {
            dispatcher: ApiDispatcher::new(),
            nt_core: NtCore::new(),
            telemetry: TelemetryRecorder::new(),
        }
    }

    pub fn dispatcher_mut(&mut self) -> &mut ApiDispatcher {
        &mut self.dispatcher
    }

    pub fn telemetry_events(&self) -> &[RuntimeTelemetryEvent] {
        self.telemetry.events()
    }

    pub fn take_telemetry_events(&mut self) -> Vec<RuntimeTelemetryEvent> {
        self.telemetry.take_events()
    }

    pub fn clear_telemetry_events(&mut self) {
        self.telemetry.clear();
    }

    pub fn launch_process(&mut self, image_name: &str, entry_point_rva: u32) -> ProcessLaunch {
        self.nt_core.launch_process(image_name, entry_point_rva)
    }

    pub fn spawn_thread(
        &mut self,
        pid: ProcessId,
        start_rva: u32,
    ) -> Result<ThreadLaunch, NtError> {
        self.nt_core.spawn_thread(pid, start_rva)
    }

    pub fn set_thread_waiting(&mut self, tid: ThreadId, reason: &str) -> Result<(), NtError> {
        self.nt_core.set_thread_waiting(tid, reason)
    }

    pub fn resume_thread(&mut self, tid: ThreadId) -> Result<(), NtError> {
        self.nt_core.resume_thread(tid)
    }

    pub fn exit_thread(&mut self, tid: ThreadId, exit_code: u32) -> Result<(), NtError> {
        self.nt_core.exit_thread(tid, exit_code)
    }

    pub fn terminate_process(&mut self, pid: ProcessId, exit_code: u32) -> Result<(), NtError> {
        self.nt_core.terminate_process(pid, exit_code)
    }

    pub fn process(&self, pid: ProcessId) -> Option<&ProcessRecord> {
        self.nt_core.process(pid)
    }

    pub fn thread(&self, tid: ThreadId) -> Option<&ThreadRecord> {
        self.nt_core.thread(tid)
    }

    pub fn process_id_from_handle(&self, handle: Handle) -> Result<ProcessId, NtError> {
        self.nt_core.process_id_from_handle(handle)
    }

    pub fn thread_id_from_handle(&self, handle: Handle) -> Result<ThreadId, NtError> {
        self.nt_core.thread_id_from_handle(handle)
    }

    pub fn nt_snapshot(&self) -> NtSnapshot {
        self.nt_core.snapshot()
    }

    pub fn alloc_memory(
        &mut self,
        pid: ProcessId,
        size: usize,
        protection: MemoryProtection,
        label: Option<&str>,
    ) -> Result<MemoryRegion, NtError> {
        self.nt_core.alloc_memory(pid, size, protection, label)
    }

    pub fn free_memory(&mut self, pid: ProcessId, base: VirtualAddress) -> Result<(), NtError> {
        self.nt_core.free_memory(pid, base)
    }

    pub fn set_memory_protection(
        &mut self,
        pid: ProcessId,
        base: VirtualAddress,
        protection: MemoryProtection,
    ) -> Result<MemoryRegion, NtError> {
        self.nt_core.set_memory_protection(pid, base, protection)
    }

    pub fn write_memory(
        &mut self,
        pid: ProcessId,
        address: VirtualAddress,
        data: &[u8],
    ) -> Result<usize, NtError> {
        self.nt_core.write_memory(pid, address, data)
    }

    pub fn read_memory(
        &self,
        pid: ProcessId,
        address: VirtualAddress,
        size: usize,
    ) -> Result<Vec<u8>, NtError> {
        self.nt_core.read_memory(pid, address, size)
    }

    pub fn create_event(
        &mut self,
        manual_reset: bool,
        initial_state: bool,
        name: Option<&str>,
    ) -> Handle {
        self.nt_core.create_event(manual_reset, initial_state, name)
    }

    pub fn create_mutex(
        &mut self,
        initial_owner_tid: Option<ThreadId>,
        name: Option<&str>,
    ) -> Handle {
        self.nt_core.create_mutex(initial_owner_tid, name)
    }

    pub fn set_event(&mut self, event_handle: Handle) -> Result<(), NtError> {
        self.nt_core.set_event(event_handle)
    }

    pub fn reset_event(&mut self, event_handle: Handle) -> Result<(), NtError> {
        self.nt_core.reset_event(event_handle)
    }

    pub fn release_mutex(&mut self, mutex_handle: Handle) -> Result<(), NtError> {
        self.nt_core.release_mutex(mutex_handle)
    }

    pub fn wait_for_single_object(
        &mut self,
        handle: Handle,
        timeout_ms: u32,
        waiter_tid: Option<ThreadId>,
    ) -> Result<WaitStatus, NtError> {
        self.nt_core
            .wait_for_single_object(handle, timeout_ms, waiter_tid)
    }

    pub fn wait_for_multiple_objects(
        &mut self,
        handles: &[Handle],
        wait_all: bool,
        timeout_ms: u32,
        waiter_tid: Option<ThreadId>,
    ) -> Result<WaitMultipleStatus, NtError> {
        self.nt_core
            .wait_for_multiple_objects(handles, wait_all, timeout_ms, waiter_tid)
    }

    pub fn open_file(&mut self, path: &str, create_if_missing: bool) -> Result<Handle, NtError> {
        self.nt_core.open_file(path, create_if_missing)
    }

    pub fn write_file(&mut self, file_handle: Handle, data: &[u8]) -> Result<usize, NtError> {
        self.nt_core.write_file(file_handle, data)
    }

    pub fn read_file(&mut self, file_handle: Handle, size: usize) -> Result<Vec<u8>, NtError> {
        self.nt_core.read_file(file_handle, size)
    }

    pub fn set_file_pointer(
        &mut self,
        file_handle: Handle,
        position: usize,
    ) -> Result<u64, NtError> {
        self.nt_core.set_file_pointer(file_handle, position)
    }

    pub fn file_content(&self, path: &str) -> Option<Vec<u8>> {
        self.nt_core.file_content(path)
    }

    pub fn registry_set_value(&mut self, key_path: &str, value_name: &str, data: &[u8]) {
        self.nt_core.registry_set_value(key_path, value_name, data)
    }

    pub fn registry_get_value(&self, key_path: &str, value_name: &str) -> Result<Vec<u8>, NtError> {
        self.nt_core.registry_get_value(key_path, value_name)
    }

    pub fn registry_delete_value(
        &mut self,
        key_path: &str,
        value_name: &str,
    ) -> Result<(), NtError> {
        self.nt_core.registry_delete_value(key_path, value_name)
    }

    pub fn close_handle(&mut self, handle: Handle) -> Result<(), NtError> {
        self.nt_core.close_handle(handle)
    }

    pub fn process_exit_code(&self, pid: ProcessId) -> Result<u32, NtError> {
        let process = self.process(pid).ok_or(NtError::UnknownProcess(pid))?;
        Ok(match process.state {
            ProcessState::Running => STILL_ACTIVE,
            ProcessState::Terminated { exit_code } => exit_code,
        })
    }

    pub fn register_phase8_kernel32_apis(&mut self) {
        for api in [
            "kernel32.CreateProcessW",
            "kernel32.CreateThread",
            "kernel32.VirtualAlloc",
            "kernel32.VirtualProtect",
            "kernel32.VirtualFree",
            "kernel32.WriteProcessMemory",
            "kernel32.ReadProcessMemory",
            "kernel32.GetExitCodeProcess",
            "kernel32.TerminateProcess",
            "kernel32.CloseHandle",
        ] {
            self.dispatcher_mut().register_implemented(api);
        }
    }

    pub fn register_phase9_runtime_apis(&mut self) {
        self.register_phase8_kernel32_apis();
        for api in [
            "kernel32.CreateEventW",
            "kernel32.SetEvent",
            "kernel32.ResetEvent",
            "kernel32.CreateMutexW",
            "kernel32.ReleaseMutex",
            "kernel32.WaitForSingleObject",
            "kernel32.WaitForMultipleObjects",
            "kernel32.CreateFileW",
            "kernel32.ReadFile",
            "kernel32.WriteFile",
            "kernel32.SetFilePointerEx",
            "advapi32.RegSetValueExW",
            "advapi32.RegQueryValueExW",
            "advapi32.RegDeleteValueW",
        ] {
            self.dispatcher_mut().register_implemented(api);
        }
    }

    pub fn register_phase10_runtime_apis(&mut self) {
        self.register_phase9_runtime_apis();
        for api in [
            "ntdll.NtTraceEvent",
            "advapi32.EventWrite",
            "advapi32.EventRegister",
        ] {
            self.dispatcher_mut().register_implemented(api);
        }
    }

    pub fn simulate_win32_call(&mut self, call: Win32Call) -> Result<Win32CallResult, NtError> {
        let action = win32_call_name(&call).to_string();
        self.telemetry.record_start("win32", &action);

        let result: Result<Win32CallResult, NtError> = (|| match call {
            Win32Call::CreateProcess {
                image_name,
                entry_point_rva,
            } => Ok(Win32CallResult::Process(
                self.launch_process(&image_name, entry_point_rva),
            )),
            Win32Call::CreateThread {
                process_handle,
                start_rva,
            } => {
                let pid = self.process_id_from_handle(process_handle)?;
                Ok(Win32CallResult::Thread(self.spawn_thread(pid, start_rva)?))
            }
            Win32Call::VirtualAlloc {
                process_handle,
                size,
                protection,
                label,
            } => {
                let pid = self.process_id_from_handle(process_handle)?;
                let region = self.alloc_memory(pid, size, protection, label.as_deref())?;
                Ok(Win32CallResult::MemoryRegion {
                    base: region.base,
                    size: region.size,
                })
            }
            Win32Call::VirtualProtect {
                process_handle,
                base,
                protection,
            } => {
                let pid = self.process_id_from_handle(process_handle)?;
                let region = self.set_memory_protection(pid, base, protection)?;
                Ok(Win32CallResult::MemoryRegion {
                    base: region.base,
                    size: region.size,
                })
            }
            Win32Call::VirtualFree {
                process_handle,
                base,
            } => {
                let pid = self.process_id_from_handle(process_handle)?;
                self.free_memory(pid, base)?;
                Ok(Win32CallResult::None)
            }
            Win32Call::WriteProcessMemory {
                process_handle,
                address,
                data,
            } => {
                let pid = self.process_id_from_handle(process_handle)?;
                let written = self.write_memory(pid, address, &data)?;
                Ok(Win32CallResult::Size(written))
            }
            Win32Call::ReadProcessMemory {
                process_handle,
                address,
                size,
            } => {
                let pid = self.process_id_from_handle(process_handle)?;
                Ok(Win32CallResult::Bytes(
                    self.read_memory(pid, address, size)?,
                ))
            }
            Win32Call::CreateEvent {
                manual_reset,
                initial_state,
                name,
            } => Ok(Win32CallResult::Handle(self.create_event(
                manual_reset,
                initial_state,
                name.as_deref(),
            ))),
            Win32Call::SetEvent { event_handle } => {
                self.set_event(event_handle)?;
                Ok(Win32CallResult::None)
            }
            Win32Call::ResetEvent { event_handle } => {
                self.reset_event(event_handle)?;
                Ok(Win32CallResult::None)
            }
            Win32Call::CreateMutex {
                initial_owner_tid,
                name,
            } => Ok(Win32CallResult::Handle(
                self.create_mutex(initial_owner_tid, name.as_deref()),
            )),
            Win32Call::ReleaseMutex { mutex_handle } => {
                self.release_mutex(mutex_handle)?;
                Ok(Win32CallResult::None)
            }
            Win32Call::WaitForSingleObject {
                handle,
                timeout_ms,
                waiter_tid,
            } => Ok(Win32CallResult::Wait(
                self.wait_for_single_object(handle, timeout_ms, waiter_tid)?,
            )),
            Win32Call::WaitForMultipleObjects {
                handles,
                wait_all,
                timeout_ms,
                waiter_tid,
            } => Ok(Win32CallResult::WaitMultiple(
                self.wait_for_multiple_objects(&handles, wait_all, timeout_ms, waiter_tid)?,
            )),
            Win32Call::OpenFile {
                path,
                create_if_missing,
            } => Ok(Win32CallResult::Handle(
                self.open_file(&path, create_if_missing)?,
            )),
            Win32Call::WriteFile { file_handle, data } => {
                Ok(Win32CallResult::Size(self.write_file(file_handle, &data)?))
            }
            Win32Call::ReadFile { file_handle, size } => {
                Ok(Win32CallResult::Bytes(self.read_file(file_handle, size)?))
            }
            Win32Call::SetFilePointer {
                file_handle,
                position,
            } => Ok(Win32CallResult::Position(
                self.set_file_pointer(file_handle, position)?,
            )),
            Win32Call::RegSetValue {
                key_path,
                value_name,
                data,
            } => {
                self.registry_set_value(&key_path, &value_name, &data);
                Ok(Win32CallResult::None)
            }
            Win32Call::RegQueryValue {
                key_path,
                value_name,
            } => Ok(Win32CallResult::Bytes(
                self.registry_get_value(&key_path, &value_name)?,
            )),
            Win32Call::RegDeleteValue {
                key_path,
                value_name,
            } => {
                self.registry_delete_value(&key_path, &value_name)?;
                Ok(Win32CallResult::None)
            }
            Win32Call::TerminateProcess {
                process_handle,
                exit_code,
            } => {
                let pid = self.process_id_from_handle(process_handle)?;
                self.terminate_process(pid, exit_code)?;
                Ok(Win32CallResult::None)
            }
            Win32Call::GetExitCodeProcess { process_handle } => {
                let pid = self.process_id_from_handle(process_handle)?;
                Ok(Win32CallResult::ExitCode(self.process_exit_code(pid)?))
            }
            Win32Call::CloseHandle { handle } => {
                self.close_handle(handle)?;
                Ok(Win32CallResult::None)
            }
        })();

        match &result {
            Ok(value) => self.telemetry.record_success(
                "win32",
                &action,
                Some(win32_result_label(value).to_string()),
            ),
            Err(err) => self
                .telemetry
                .record_error("win32", &action, err.to_string()),
        }

        result
    }

    pub fn load_pe_image(&self, bytes: &[u8]) -> Result<LoadReport, PeError> {
        let loaded = load_pe_image(bytes)?;
        let imported_dlls = loaded.imports.iter().map(|i| i.dll_name.clone()).collect();

        let import_details: Vec<DllImportReport> = loaded
            .imports
            .iter()
            .map(|imp| DllImportReport {
                dll_name: imp.dll_name.clone(),
                symbols: imp
                    .functions
                    .iter()
                    .map(|f| symbol_label(&f.symbol))
                    .collect(),
            })
            .collect();

        let import_symbol_count = import_details.iter().map(|d| d.symbols.len()).sum();

        Ok(LoadReport {
            metadata: loaded.metadata.clone(),
            image_base: loaded.metadata.image_base,
            mapped_image_size: loaded.mapped_image.len(),
            sections_loaded: loaded.sections.len(),
            imports_checked: loaded.imports.len(),
            import_symbol_count,
            imported_dlls,
            import_details,
            exports_checked: loaded.exports.len(),
            exported_dll: loaded.export_dll_name,
            relocations_count: loaded.relocations.len(),
        })
    }

    pub fn resolve_imports(&self, image: &LoadedPeImage, modules: &[LoadedPeImage]) -> LinkReport {
        let mut providers: HashMap<String, Vec<(String, &LoadedPeImage)>> = HashMap::new();
        for (idx, module) in modules.iter().enumerate() {
            if let Some(dll_name) = module.export_dll_name.as_deref() {
                let module_name = module
                    .export_dll_name
                    .clone()
                    .unwrap_or_else(|| format!("module@{idx}"));
                providers
                    .entry(normalize_dll_name(dll_name))
                    .or_default()
                    .push((module_name, module));
            }
        }

        let mut cache: HashMap<(String, String), CachedLookup> = HashMap::new();
        let mut cache_hits = 0usize;
        let mut resolutions = Vec::new();
        let mut collisions = Vec::new();
        let mut collision_keys = HashSet::new();

        for imp in &image.imports {
            let dll_key = normalize_dll_name(&imp.dll_name);

            for func in &imp.functions {
                let symbol = symbol_label(&func.symbol);
                let cache_key = (dll_key.clone(), symbol.clone());

                if let Some(cached) = cache.get(&cache_key) {
                    cache_hits += 1;
                    resolutions.push(cached.resolution.clone());
                    if !cached.collision_modules.is_empty() {
                        let key = format!("{}|{}", imp.dll_name, symbol);
                        if collision_keys.insert(key) {
                            collisions.push(SymbolCollision {
                                dll_name: imp.dll_name.clone(),
                                symbol: symbol.clone(),
                                candidate_modules: cached.collision_modules.clone(),
                            });
                        }
                    }
                    continue;
                }

                let lookup = if let Some(candidates) = providers.get(&dll_key) {
                    let mut matches: Vec<(String, u32)> = Vec::new();
                    for (module_name, module) in candidates {
                        if let Some(exp) = resolve_export(&module.exports, &func.symbol) {
                            matches.push((module_name.clone(), exp.rva));
                        }
                    }

                    if matches.len() == 1 {
                        let (module_name, rva) = &matches[0];
                        CachedLookup {
                            resolution: ImportResolution {
                                dll_name: imp.dll_name.clone(),
                                symbol: symbol.clone(),
                                resolved: true,
                                target_module: Some(module_name.clone()),
                                target_rva: Some(*rva),
                                ambiguous: false,
                            },
                            collision_modules: Vec::new(),
                        }
                    } else if matches.len() > 1 {
                        let mut modules: Vec<String> =
                            matches.into_iter().map(|(m, _)| m).collect();
                        modules.sort();
                        modules.dedup();
                        CachedLookup {
                            resolution: ImportResolution {
                                dll_name: imp.dll_name.clone(),
                                symbol: symbol.clone(),
                                resolved: false,
                                target_module: None,
                                target_rva: None,
                                ambiguous: true,
                            },
                            collision_modules: modules,
                        }
                    } else {
                        let provider_hint = if candidates.len() == 1 {
                            Some(candidates[0].0.clone())
                        } else {
                            None
                        };
                        CachedLookup {
                            resolution: ImportResolution {
                                dll_name: imp.dll_name.clone(),
                                symbol: symbol.clone(),
                                resolved: false,
                                target_module: provider_hint,
                                target_rva: None,
                                ambiguous: false,
                            },
                            collision_modules: Vec::new(),
                        }
                    }
                } else {
                    CachedLookup {
                        resolution: ImportResolution {
                            dll_name: imp.dll_name.clone(),
                            symbol: symbol.clone(),
                            resolved: false,
                            target_module: None,
                            target_rva: None,
                            ambiguous: false,
                        },
                        collision_modules: Vec::new(),
                    }
                };

                if !lookup.collision_modules.is_empty() {
                    let key = format!("{}|{}", imp.dll_name, symbol);
                    if collision_keys.insert(key) {
                        collisions.push(SymbolCollision {
                            dll_name: imp.dll_name.clone(),
                            symbol: symbol.clone(),
                            candidate_modules: lookup.collision_modules.clone(),
                        });
                    }
                }

                resolutions.push(lookup.resolution.clone());
                cache.insert(cache_key, lookup);
            }
        }

        let total_symbols = resolutions.len();
        let resolved_symbols = resolutions.iter().filter(|r| r.resolved).count();
        let ambiguous_symbols = resolutions.iter().filter(|r| r.ambiguous).count();

        LinkReport {
            total_symbols,
            resolved_symbols,
            unresolved_symbols: total_symbols.saturating_sub(resolved_symbols),
            ambiguous_symbols,
            cache_hits,
            resolutions,
            collisions,
        }
    }

    pub fn dispatch_api(&self, api: &str) -> Result<DispatchDecision, DispatchError> {
        self.dispatcher.call(api)
    }
}

#[cfg(test)]
mod tests {
    use crate::ntcore::{
        MemoryProtection, ProcessState, ThreadState, WaitMultipleStatus, WaitStatus,
    };
    use crate::runtime::RuntimeCore;
    use crate::telemetry::TelemetryStage;
    use crate::win32::{STILL_ACTIVE, Win32Call, Win32CallResult};

    fn minimal_export_pe() -> Vec<u8> {
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
    fn runtime_reports_exports() {
        let core = RuntimeCore::new();
        let report = core
            .load_pe_image(&minimal_export_pe())
            .expect("must parse PE");
        assert_eq!(report.exports_checked, 1);
        assert_eq!(report.exported_dll.as_deref(), Some("KERNEL32.dll"));
        assert_eq!(report.image_base, 0x0000_0001_8000_0000);
    }

    #[test]
    fn runtime_tracks_process_and_thread_lifecycle() {
        let mut core = RuntimeCore::new();
        let launch = core.launch_process("setup.exe", 0x1000);
        let worker = core
            .spawn_thread(launch.pid, 0x2000)
            .expect("worker thread must launch");

        core.set_thread_waiting(worker.tid, "io wait")
            .expect("worker switches to waiting");
        assert_eq!(
            core.thread(worker.tid).expect("worker exists").state,
            ThreadState::Waiting {
                reason: "io wait".to_string()
            }
        );

        core.resume_thread(worker.tid)
            .expect("worker resumes to running");
        assert_eq!(
            core.thread(worker.tid).expect("worker exists").state,
            ThreadState::Running
        );

        core.terminate_process(launch.pid, 17)
            .expect("process termination should succeed");
        assert_eq!(
            core.process(launch.pid).expect("process exists").state,
            ProcessState::Terminated { exit_code: 17 }
        );
        assert_eq!(
            core.thread(launch.primary_thread_id)
                .expect("primary thread exists")
                .state,
            ThreadState::Terminated { exit_code: 17 }
        );
    }

    #[test]
    fn runtime_simulates_first_kernel32_calls() {
        let mut core = RuntimeCore::new();

        let process = core
            .simulate_win32_call(Win32Call::CreateProcess {
                image_name: "installer.exe".to_string(),
                entry_point_rva: 0x1200,
            })
            .expect("create process should succeed");
        let Win32CallResult::Process(launch) = process else {
            panic!("expected process launch result");
        };

        let alloc = core
            .simulate_win32_call(Win32Call::VirtualAlloc {
                process_handle: launch.process_handle,
                size: 128,
                protection: MemoryProtection::ReadWrite,
                label: Some("bootstrap-buffer".to_string()),
            })
            .expect("virtual alloc should succeed");
        let Win32CallResult::MemoryRegion { base, .. } = alloc else {
            panic!("expected memory region result");
        };

        let write = core
            .simulate_win32_call(Win32Call::WriteProcessMemory {
                process_handle: launch.process_handle,
                address: base,
                data: b"PING".to_vec(),
            })
            .expect("write process memory should succeed");
        assert_eq!(write, Win32CallResult::Size(4));

        let read = core
            .simulate_win32_call(Win32Call::ReadProcessMemory {
                process_handle: launch.process_handle,
                address: base,
                size: 4,
            })
            .expect("read process memory should succeed");
        assert_eq!(read, Win32CallResult::Bytes(b"PING".to_vec()));

        let code = core
            .simulate_win32_call(Win32Call::GetExitCodeProcess {
                process_handle: launch.process_handle,
            })
            .expect("get exit code should succeed");
        assert_eq!(code, Win32CallResult::ExitCode(STILL_ACTIVE));
    }

    #[test]
    fn runtime_simulates_wait_file_and_registry_calls() {
        let mut core = RuntimeCore::new();
        let launch = core.launch_process("bootstrap.exe", 0x1000);

        let evt = core
            .simulate_win32_call(Win32Call::CreateEvent {
                manual_reset: false,
                initial_state: false,
                name: Some("ready".to_string()),
            })
            .expect("create event should succeed");
        let Win32CallResult::Handle(event_handle) = evt else {
            panic!("expected handle");
        };

        let wait = core
            .simulate_win32_call(Win32Call::WaitForSingleObject {
                handle: event_handle,
                timeout_ms: 0,
                waiter_tid: Some(launch.primary_thread_id),
            })
            .expect("wait should succeed");
        assert_eq!(wait, Win32CallResult::Wait(WaitStatus::Timeout));

        core.simulate_win32_call(Win32Call::SetEvent { event_handle })
            .expect("set event should succeed");

        let mutex = core
            .simulate_win32_call(Win32Call::CreateMutex {
                initial_owner_tid: None,
                name: Some("lock".to_string()),
            })
            .expect("create mutex should succeed");
        let Win32CallResult::Handle(mutex_handle) = mutex else {
            panic!("expected handle");
        };

        let wait_multi = core
            .simulate_win32_call(Win32Call::WaitForMultipleObjects {
                handles: vec![event_handle, mutex_handle],
                wait_all: true,
                timeout_ms: 0,
                waiter_tid: Some(launch.primary_thread_id),
            })
            .expect("wait multiple should succeed");
        assert_eq!(
            wait_multi,
            Win32CallResult::WaitMultiple(WaitMultipleStatus::AllSignaled)
        );

        let file = core
            .simulate_win32_call(Win32Call::OpenFile {
                path: "C:/temp/phase9.log".to_string(),
                create_if_missing: true,
            })
            .expect("open file should succeed");
        let Win32CallResult::Handle(file_handle) = file else {
            panic!("expected handle");
        };

        let write = core
            .simulate_win32_call(Win32Call::WriteFile {
                file_handle,
                data: b"phase9".to_vec(),
            })
            .expect("write file should succeed");
        assert_eq!(write, Win32CallResult::Size(6));
        core.simulate_win32_call(Win32Call::SetFilePointer {
            file_handle,
            position: 0,
        })
        .expect("set file pointer should succeed");
        let read = core
            .simulate_win32_call(Win32Call::ReadFile {
                file_handle,
                size: 6,
            })
            .expect("read file should succeed");
        assert_eq!(read, Win32CallResult::Bytes(b"phase9".to_vec()));

        core.simulate_win32_call(Win32Call::RegSetValue {
            key_path: "HKCU\\Software\\AIWR".to_string(),
            value_name: "Channel".to_string(),
            data: b"beta".to_vec(),
        })
        .expect("reg set should succeed");
        let reg = core
            .simulate_win32_call(Win32Call::RegQueryValue {
                key_path: "HKCU\\Software\\AIWR".to_string(),
                value_name: "Channel".to_string(),
            })
            .expect("reg query should succeed");
        assert_eq!(reg, Win32CallResult::Bytes(b"beta".to_vec()));
    }

    #[test]
    fn runtime_records_telemetry_for_success_and_error_paths() {
        let mut core = RuntimeCore::new();

        let create = core
            .simulate_win32_call(Win32Call::CreateProcess {
                image_name: "telemetry.exe".to_string(),
                entry_point_rva: 0x1000,
            })
            .expect("process creation should succeed");
        let Win32CallResult::Process(launch) = create else {
            panic!("expected process launch");
        };

        core.simulate_win32_call(Win32Call::CloseHandle {
            handle: launch.process_handle,
        })
        .expect("close handle should succeed");

        let err = core
            .simulate_win32_call(Win32Call::CreateThread {
                process_handle: launch.process_handle,
                start_rva: 0x2000,
            })
            .expect_err("closed process handle should fail");
        assert_eq!(err.to_string(), "invalid process handle: 0x00000100");

        let events = core.telemetry_events();
        assert_eq!(events.len(), 6);
        assert_eq!(events[0].action, "CreateProcessW");
        assert_eq!(events[0].stage, TelemetryStage::Start);
        assert_eq!(events[1].action, "CreateProcessW");
        assert_eq!(events[1].stage, TelemetryStage::Success);
        assert_eq!(events[4].action, "CreateThread");
        assert_eq!(events[4].stage, TelemetryStage::Start);
        assert_eq!(events[5].action, "CreateThread");
        assert_eq!(events[5].stage, TelemetryStage::Error);
    }
}
