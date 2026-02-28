use crate::dispatcher::{ApiDispatcher, DispatchDecision, DispatchError};
use crate::pe::{PeError, PeMetadata, parse_pe_metadata};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LoadReport {
    pub metadata: PeMetadata,
    pub imports_checked: usize,
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
        let metadata = parse_pe_metadata(bytes)?;
        Ok(LoadReport {
            metadata,
            imports_checked: 0,
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
        let mut b = vec![0u8; 512];
        b[0] = b'M';
        b[1] = b'Z';
        b[0x3C..0x40].copy_from_slice(&(0x80u32).to_le_bytes());

        b[0x80..0x84].copy_from_slice(&0x0000_4550u32.to_le_bytes());
        b[0x84..0x86].copy_from_slice(&0x8664u16.to_le_bytes());
        b[0x86..0x88].copy_from_slice(&2u16.to_le_bytes());
        b[0x94..0x96].copy_from_slice(&0xF0u16.to_le_bytes());

        let optional = 0x98usize;
        b[optional + 16..optional + 20].copy_from_slice(&0x1234u32.to_le_bytes());
        b[optional + 56..optional + 60].copy_from_slice(&0x9000u32.to_le_bytes());
        b
    }

    #[test]
    fn runtime_loads_pe_metadata() {
        let core = RuntimeCore::new();
        let report = core.load_pe_image(&minimal_pe()).expect("must parse PE");
        assert_eq!(report.metadata.entry_point_rva, 0x1234);
        assert_eq!(report.metadata.size_of_image, 0x9000);
    }
}
