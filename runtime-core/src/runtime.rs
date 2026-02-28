use std::collections::{HashMap, HashSet};

use crate::dispatcher::{ApiDispatcher, DispatchDecision, DispatchError};
use crate::ntcore::{
    Handle, NtCore, NtError, NtSnapshot, ProcessId, ProcessLaunch, ProcessRecord, ThreadId,
    ThreadLaunch, ThreadRecord,
};
use crate::pe::{LoadedPeImage, PeError, PeExport, PeImportSymbol, PeMetadata, load_pe_image};

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

impl RuntimeCore {
    pub fn new() -> Self {
        Self {
            dispatcher: ApiDispatcher::new(),
            nt_core: NtCore::new(),
        }
    }

    pub fn dispatcher_mut(&mut self) -> &mut ApiDispatcher {
        &mut self.dispatcher
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
    use crate::ntcore::{ProcessState, ThreadState};
    use crate::runtime::RuntimeCore;

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
}
