use crate::dispatcher::{ApiDispatcher, DispatchDecision, DispatchError};
use crate::pe::{PeError, PeMetadata, load_pe_image};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LoadReport {
    pub metadata: PeMetadata,
    pub mapped_image_size: usize,
    pub sections_loaded: usize,
    pub imports_checked: usize,
    pub imported_dlls: Vec<String>,
}

#[derive(Debug, Default)]
pub struct RuntimeCore {
    dispatcher: ApiDispatcher,
}

impl RuntimeCore {
    pub fn new() -> Self {
        Self {
            dispatcher: ApiDispatcher::new(),
        }
    }

    pub fn dispatcher_mut(&mut self) -> &mut ApiDispatcher {
        &mut self.dispatcher
    }

    pub fn load_pe_image(&self, bytes: &[u8]) -> Result<LoadReport, PeError> {
        let loaded = load_pe_image(bytes)?;
        let imported_dlls = loaded.imports.iter().map(|i| i.dll_name.clone()).collect();

        Ok(LoadReport {
            metadata: loaded.metadata,
            mapped_image_size: loaded.mapped_image.len(),
            sections_loaded: loaded.sections.len(),
            imports_checked: loaded.imports.len(),
            imported_dlls,
        })
    }

    pub fn dispatch_api(&self, api: &str) -> Result<DispatchDecision, DispatchError> {
        self.dispatcher.call(api)
    }
}

#[cfg(test)]
mod tests {
    use crate::runtime::RuntimeCore;

    fn minimal_pe() -> Vec<u8> {
        let mut b = vec![0u8; 0x600];
        b[0] = b'M';
        b[1] = b'Z';
        b[0x3C..0x40].copy_from_slice(&(0x80u32).to_le_bytes());

        b[0x80..0x84].copy_from_slice(&0x0000_4550u32.to_le_bytes());
        b[0x84..0x86].copy_from_slice(&0x8664u16.to_le_bytes());
        b[0x86..0x88].copy_from_slice(&1u16.to_le_bytes());
        b[0x94..0x96].copy_from_slice(&0xF0u16.to_le_bytes());

        let optional = 0x98usize;
        b[optional..optional + 2].copy_from_slice(&0x20Bu16.to_le_bytes());
        b[optional + 16..optional + 20].copy_from_slice(&0x1234u32.to_le_bytes());
        b[optional + 56..optional + 60].copy_from_slice(&0x5000u32.to_le_bytes());
        b[optional + 60..optional + 64].copy_from_slice(&0x200u32.to_le_bytes());
        b[optional + 108..optional + 112].copy_from_slice(&16u32.to_le_bytes());

        let sh = optional + 0xF0;
        b[sh..sh + 8].copy_from_slice(b".text\0\0\0");
        b[sh + 8..sh + 12].copy_from_slice(&0x100u32.to_le_bytes());
        b[sh + 12..sh + 16].copy_from_slice(&0x1000u32.to_le_bytes());
        b[sh + 16..sh + 20].copy_from_slice(&0x200u32.to_le_bytes());
        b[sh + 20..sh + 24].copy_from_slice(&0x200u32.to_le_bytes());

        b
    }

    #[test]
    fn runtime_loads_pe_metadata() {
        let core = RuntimeCore::new();
        let report = core.load_pe_image(&minimal_pe()).expect("must parse PE");
        assert_eq!(report.metadata.entry_point_rva, 0x1234);
        assert_eq!(report.metadata.size_of_image, 0x5000);
        assert_eq!(report.sections_loaded, 1);
        assert_eq!(report.imports_checked, 0);
        assert_eq!(report.mapped_image_size, 0x5000);
    }
}
