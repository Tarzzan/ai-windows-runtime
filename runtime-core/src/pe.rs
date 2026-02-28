#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PeMetadata {
    pub machine: u16,
    pub number_of_sections: u16,
    pub entry_point_rva: u32,
    pub size_of_image: u32,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PeError {
    TooSmall,
    InvalidDosSignature,
    InvalidPeOffset,
    InvalidPeSignature,
    OptionalHeaderTooSmall,
}

fn read_u16_le(bytes: &[u8], offset: usize) -> Result<u16, PeError> {
    let end = offset.checked_add(2).ok_or(PeError::InvalidPeOffset)?;
    if end > bytes.len() {
        return Err(PeError::TooSmall);
    }
    Ok(u16::from_le_bytes([bytes[offset], bytes[offset + 1]]))
}

fn read_u32_le(bytes: &[u8], offset: usize) -> Result<u32, PeError> {
    let end = offset.checked_add(4).ok_or(PeError::InvalidPeOffset)?;
    if end > bytes.len() {
        return Err(PeError::TooSmall);
    }
    Ok(u32::from_le_bytes([
        bytes[offset],
        bytes[offset + 1],
        bytes[offset + 2],
        bytes[offset + 3],
    ]))
}

pub fn parse_pe_metadata(bytes: &[u8]) -> Result<PeMetadata, PeError> {
    const DOS_SIGNATURE: u16 = 0x5A4D;
    const PE_SIGNATURE: u32 = 0x0000_4550;
    const DOS_E_LFANEW: usize = 0x3C;

    if bytes.len() < 0x40 {
        return Err(PeError::TooSmall);
    }

    let mz = read_u16_le(bytes, 0)?;
    if mz != DOS_SIGNATURE {
        return Err(PeError::InvalidDosSignature);
    }

    let pe_offset = read_u32_le(bytes, DOS_E_LFANEW)? as usize;
    let pe_sig_end = pe_offset.checked_add(4).ok_or(PeError::InvalidPeOffset)?;
    if pe_sig_end > bytes.len() {
        return Err(PeError::InvalidPeOffset);
    }

    let signature = read_u32_le(bytes, pe_offset)?;
    if signature != PE_SIGNATURE {
        return Err(PeError::InvalidPeSignature);
    }

    let file_header = pe_offset + 4;
    let machine = read_u16_le(bytes, file_header)?;
    let number_of_sections = read_u16_le(bytes, file_header + 2)?;
    let size_of_optional_header = read_u16_le(bytes, file_header + 16)? as usize;

    let optional_header = file_header + 20;
    let optional_end = optional_header
        .checked_add(size_of_optional_header)
        .ok_or(PeError::InvalidPeOffset)?;
    if optional_end > bytes.len() {
        return Err(PeError::OptionalHeaderTooSmall);
    }

    let entry_point_rva = read_u32_le(bytes, optional_header + 16)?;
    let size_of_image = read_u32_le(bytes, optional_header + 56)?;

    Ok(PeMetadata {
        machine,
        number_of_sections,
        entry_point_rva,
        size_of_image,
    })
}

#[cfg(test)]
mod tests {
    use super::{PeError, parse_pe_metadata};

    fn minimal_pe() -> Vec<u8> {
        let mut b = vec![0u8; 512];
        b[0] = b'M';
        b[1] = b'Z';
        b[0x3C..0x40].copy_from_slice(&(0x80u32).to_le_bytes());

        b[0x80..0x84].copy_from_slice(&0x0000_4550u32.to_le_bytes());
        b[0x84..0x86].copy_from_slice(&0x8664u16.to_le_bytes());
        b[0x86..0x88].copy_from_slice(&3u16.to_le_bytes());
        b[0x94..0x96].copy_from_slice(&0xF0u16.to_le_bytes());

        let optional = 0x98usize;
        b[optional + 16..optional + 20].copy_from_slice(&0x1000u32.to_le_bytes());
        b[optional + 56..optional + 60].copy_from_slice(&0x5000u32.to_le_bytes());
        b
    }

    #[test]
    fn parses_minimal_pe_metadata() {
        let pe = minimal_pe();
        let meta = parse_pe_metadata(&pe).expect("expected valid PE");
        assert_eq!(meta.machine, 0x8664);
        assert_eq!(meta.number_of_sections, 3);
        assert_eq!(meta.entry_point_rva, 0x1000);
        assert_eq!(meta.size_of_image, 0x5000);
    }

    #[test]
    fn rejects_non_mz_payload() {
        let mut payload = vec![0u8; 128];
        payload[0] = b'N';
        payload[1] = b'O';
        let err = parse_pe_metadata(&payload).expect_err("expected invalid DOS signature");
        assert_eq!(err, PeError::InvalidDosSignature);
    }
}
