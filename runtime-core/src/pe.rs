#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PeMetadata {
    pub machine: u16,
    pub number_of_sections: u16,
    pub entry_point_rva: u32,
    pub size_of_image: u32,
    pub image_base: u64,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PeSection {
    pub name: String,
    pub virtual_address: u32,
    pub virtual_size: u32,
    pub raw_data_ptr: u32,
    pub raw_data_size: u32,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PeImportSymbol {
    Name { hint: u16, name: String },
    Ordinal(u16),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PeImportFunction {
    pub thunk_rva: u32,
    pub symbol: PeImportSymbol,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PeImport {
    pub dll_name: String,
    pub name_rva: u32,
    pub first_thunk_rva: u32,
    pub functions: Vec<PeImportFunction>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PeExport {
    pub ordinal: u32,
    pub rva: u32,
    pub name: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PeRelocationEntry {
    pub kind: u8,
    pub offset: u16,
    pub target_rva: u32,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct LoadedPeImage {
    pub metadata: PeMetadata,
    pub sections: Vec<PeSection>,
    pub imports: Vec<PeImport>,
    pub export_dll_name: Option<String>,
    pub exports: Vec<PeExport>,
    pub relocations: Vec<PeRelocationEntry>,
    pub mapped_image: Vec<u8>,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum PeError {
    TooSmall,
    InvalidDosSignature,
    InvalidPeOffset,
    InvalidPeSignature,
    OptionalHeaderTooSmall,
    UnsupportedOptionalHeaderMagic(u16),
    InvalidSectionTable,
    InvalidImageSize,
    ImageTooLarge,
    SectionRawOutOfBounds,
    SectionVirtualOutOfBounds,
    RvaNotMapped(u32),
    UnterminatedCString,
    ImportThunkListTooLong,
    ExportTableTooLarge,
    RelocationOutOfBounds(u32),
}

#[derive(Debug, Clone)]
struct PeParsedHeaders {
    metadata: PeMetadata,
    section_table_offset: usize,
    number_of_sections: u16,
    size_of_headers: u32,
    import_dir_rva: u32,
    import_dir_size: u32,
    export_dir_rva: u32,
    export_dir_size: u32,
    reloc_dir_rva: u32,
    reloc_dir_size: u32,
    is_pe32_plus: bool,
}

const DOS_SIGNATURE: u16 = 0x5A4D;
const PE_SIGNATURE: u32 = 0x0000_4550;
const DOS_E_LFANEW: usize = 0x3C;
const SECTION_HEADER_SIZE: usize = 40;
const MAX_IMAGE_SIZE: usize = 512 * 1024 * 1024;
const MAX_IMPORT_DESCRIPTORS: usize = 256;
const MAX_IMPORT_THUNKS: usize = 4096;
const MAX_EXPORT_FUNCTIONS: usize = 65536;
const MAX_EXPORT_NAMES: usize = 65536;

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

fn read_u64_le(bytes: &[u8], offset: usize) -> Result<u64, PeError> {
    let end = offset.checked_add(8).ok_or(PeError::InvalidPeOffset)?;
    if end > bytes.len() {
        return Err(PeError::TooSmall);
    }
    Ok(u64::from_le_bytes([
        bytes[offset],
        bytes[offset + 1],
        bytes[offset + 2],
        bytes[offset + 3],
        bytes[offset + 4],
        bytes[offset + 5],
        bytes[offset + 6],
        bytes[offset + 7],
    ]))
}

fn parse_pe_headers(bytes: &[u8]) -> Result<PeParsedHeaders, PeError> {
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

    let optional_magic = read_u16_le(bytes, optional_header)?;
    let (data_dir_start, is_pe32_plus) = match optional_magic {
        0x10B => (optional_header + 96, false),
        0x20B => (optional_header + 112, true),
        other => return Err(PeError::UnsupportedOptionalHeaderMagic(other)),
    };

    let needed_for_data_dir = data_dir_start
        .checked_add(48)
        .ok_or(PeError::OptionalHeaderTooSmall)?;
    if needed_for_data_dir > optional_end {
        return Err(PeError::OptionalHeaderTooSmall);
    }

    let entry_point_rva = read_u32_le(bytes, optional_header + 16)?;
    let image_base = if is_pe32_plus {
        read_u64_le(bytes, optional_header + 24)?
    } else {
        read_u32_le(bytes, optional_header + 28)? as u64
    };
    let size_of_image = read_u32_le(bytes, optional_header + 56)?;
    let size_of_headers = read_u32_le(bytes, optional_header + 60)?;

    if size_of_image == 0 {
        return Err(PeError::InvalidImageSize);
    }
    if (size_of_image as usize) > MAX_IMAGE_SIZE {
        return Err(PeError::ImageTooLarge);
    }

    let export_dir_rva = read_u32_le(bytes, data_dir_start)?;
    let export_dir_size = read_u32_le(bytes, data_dir_start + 4)?;
    let import_dir_rva = read_u32_le(bytes, data_dir_start + 8)?;
    let import_dir_size = read_u32_le(bytes, data_dir_start + 12)?;
    let reloc_dir_rva = read_u32_le(bytes, data_dir_start + 40)?;
    let reloc_dir_size = read_u32_le(bytes, data_dir_start + 44)?;

    let section_table_offset = optional_end;
    let section_table_size = (number_of_sections as usize)
        .checked_mul(SECTION_HEADER_SIZE)
        .ok_or(PeError::InvalidSectionTable)?;
    let section_table_end = section_table_offset
        .checked_add(section_table_size)
        .ok_or(PeError::InvalidSectionTable)?;
    if section_table_end > bytes.len() {
        return Err(PeError::InvalidSectionTable);
    }

    Ok(PeParsedHeaders {
        metadata: PeMetadata {
            machine,
            number_of_sections,
            entry_point_rva,
            size_of_image,
            image_base,
        },
        section_table_offset,
        number_of_sections,
        size_of_headers,
        import_dir_rva,
        import_dir_size,
        export_dir_rva,
        export_dir_size,
        reloc_dir_rva,
        reloc_dir_size,
        is_pe32_plus,
    })
}

fn parse_section_name(raw: &[u8]) -> String {
    let end = raw.iter().position(|&c| c == 0).unwrap_or(raw.len());
    String::from_utf8_lossy(&raw[..end]).to_string()
}

fn parse_sections(bytes: &[u8], headers: &PeParsedHeaders) -> Result<Vec<PeSection>, PeError> {
    let mut sections = Vec::with_capacity(headers.number_of_sections as usize);

    for i in 0..headers.number_of_sections as usize {
        let off = headers.section_table_offset + i * SECTION_HEADER_SIZE;
        let name = parse_section_name(&bytes[off..off + 8]);
        let virtual_size = read_u32_le(bytes, off + 8)?;
        let virtual_address = read_u32_le(bytes, off + 12)?;
        let raw_data_size = read_u32_le(bytes, off + 16)?;
        let raw_data_ptr = read_u32_le(bytes, off + 20)?;

        sections.push(PeSection {
            name,
            virtual_address,
            virtual_size,
            raw_data_ptr,
            raw_data_size,
        });
    }

    Ok(sections)
}

fn map_image(
    bytes: &[u8],
    headers: &PeParsedHeaders,
    sections: &[PeSection],
) -> Result<Vec<u8>, PeError> {
    let mut mapped = vec![0u8; headers.metadata.size_of_image as usize];

    let header_copy_len = usize::min(
        usize::min(headers.size_of_headers as usize, bytes.len()),
        mapped.len(),
    );
    mapped[..header_copy_len].copy_from_slice(&bytes[..header_copy_len]);

    for section in sections {
        if section.raw_data_size == 0 {
            continue;
        }

        let src_start = section.raw_data_ptr as usize;
        let src_end = src_start
            .checked_add(section.raw_data_size as usize)
            .ok_or(PeError::SectionRawOutOfBounds)?;
        if src_end > bytes.len() {
            return Err(PeError::SectionRawOutOfBounds);
        }

        let dst_start = section.virtual_address as usize;
        let dst_end = dst_start
            .checked_add(section.raw_data_size as usize)
            .ok_or(PeError::SectionVirtualOutOfBounds)?;
        if dst_end > mapped.len() {
            return Err(PeError::SectionVirtualOutOfBounds);
        }

        mapped[dst_start..dst_end].copy_from_slice(&bytes[src_start..src_end]);
    }

    Ok(mapped)
}

fn rva_to_file_offset(rva: u32, sections: &[PeSection], size_of_headers: u32) -> Option<usize> {
    if rva < size_of_headers {
        return Some(rva as usize);
    }

    for section in sections {
        let span = section.virtual_size.max(section.raw_data_size);
        let start = section.virtual_address;
        let end = start.checked_add(span)?;
        if rva >= start && rva < end {
            let delta = rva - start;
            let file = section.raw_data_ptr.checked_add(delta)?;
            return Some(file as usize);
        }
    }

    None
}

fn read_c_string(bytes: &[u8], offset: usize) -> Result<String, PeError> {
    if offset >= bytes.len() {
        return Err(PeError::TooSmall);
    }

    let mut end = offset;
    let max_end = usize::min(bytes.len(), offset.saturating_add(4096));
    while end < max_end {
        if bytes[end] == 0 {
            return Ok(String::from_utf8_lossy(&bytes[offset..end]).to_string());
        }
        end += 1;
    }

    Err(PeError::UnterminatedCString)
}

fn parse_import_thunks(
    bytes: &[u8],
    headers: &PeParsedHeaders,
    sections: &[PeSection],
    thunk_rva: u32,
) -> Result<Vec<PeImportFunction>, PeError> {
    if thunk_rva == 0 {
        return Ok(Vec::new());
    }

    let thunk_size = if headers.is_pe32_plus { 8u32 } else { 4u32 };
    let ordinal_flag = if headers.is_pe32_plus {
        0x8000_0000_0000_0000u64
    } else {
        0x8000_0000u64
    };

    let mut out = Vec::new();
    let mut current_rva = thunk_rva;

    for _ in 0..MAX_IMPORT_THUNKS {
        let off = rva_to_file_offset(current_rva, sections, headers.size_of_headers)
            .ok_or(PeError::RvaNotMapped(current_rva))?;

        let thunk_value = if headers.is_pe32_plus {
            read_u64_le(bytes, off)?
        } else {
            read_u32_le(bytes, off)? as u64
        };

        if thunk_value == 0 {
            return Ok(out);
        }

        let symbol = if (thunk_value & ordinal_flag) != 0 {
            PeImportSymbol::Ordinal((thunk_value & 0xFFFF) as u16)
        } else {
            let name_rva = thunk_value as u32;
            let name_off = rva_to_file_offset(name_rva, sections, headers.size_of_headers)
                .ok_or(PeError::RvaNotMapped(name_rva))?;
            let hint = read_u16_le(bytes, name_off)?;
            let name = read_c_string(bytes, name_off + 2)?;
            PeImportSymbol::Name { hint, name }
        };

        out.push(PeImportFunction {
            thunk_rva: current_rva,
            symbol,
        });

        current_rva = current_rva
            .checked_add(thunk_size)
            .ok_or(PeError::InvalidPeOffset)?;
    }

    Err(PeError::ImportThunkListTooLong)
}

fn parse_imports(
    bytes: &[u8],
    headers: &PeParsedHeaders,
    sections: &[PeSection],
) -> Result<Vec<PeImport>, PeError> {
    if headers.import_dir_rva == 0 || headers.import_dir_size == 0 {
        return Ok(Vec::new());
    }

    let table_offset =
        rva_to_file_offset(headers.import_dir_rva, sections, headers.size_of_headers)
            .ok_or(PeError::RvaNotMapped(headers.import_dir_rva))?;

    let max_descriptors = usize::min(
        (headers.import_dir_size as usize / 20).saturating_add(1),
        MAX_IMPORT_DESCRIPTORS,
    );
    let mut imports = Vec::new();

    for i in 0..max_descriptors {
        let off = table_offset.checked_add(i * 20).ok_or(PeError::TooSmall)?;
        let end = off.checked_add(20).ok_or(PeError::TooSmall)?;
        if end > bytes.len() {
            if i == 0 {
                return Err(PeError::TooSmall);
            }
            break;
        }

        let original_first_thunk = read_u32_le(bytes, off)?;
        let time_date_stamp = read_u32_le(bytes, off + 4)?;
        let forwarder_chain = read_u32_le(bytes, off + 8)?;
        let name_rva = read_u32_le(bytes, off + 12)?;
        let first_thunk_rva = read_u32_le(bytes, off + 16)?;

        if original_first_thunk == 0
            && time_date_stamp == 0
            && forwarder_chain == 0
            && name_rva == 0
            && first_thunk_rva == 0
        {
            break;
        }

        let name_offset = rva_to_file_offset(name_rva, sections, headers.size_of_headers)
            .ok_or(PeError::RvaNotMapped(name_rva))?;
        let dll_name = read_c_string(bytes, name_offset)?;

        let thunk_rva = if original_first_thunk != 0 {
            original_first_thunk
        } else {
            first_thunk_rva
        };
        let functions = parse_import_thunks(bytes, headers, sections, thunk_rva)?;

        imports.push(PeImport {
            dll_name,
            name_rva,
            first_thunk_rva,
            functions,
        });
    }

    Ok(imports)
}

fn parse_exports(
    bytes: &[u8],
    headers: &PeParsedHeaders,
    sections: &[PeSection],
) -> Result<(Option<String>, Vec<PeExport>), PeError> {
    if headers.export_dir_rva == 0 || headers.export_dir_size == 0 {
        return Ok((None, Vec::new()));
    }

    let dir_off = rva_to_file_offset(headers.export_dir_rva, sections, headers.size_of_headers)
        .ok_or(PeError::RvaNotMapped(headers.export_dir_rva))?;
    let dir_end = dir_off.checked_add(40).ok_or(PeError::TooSmall)?;
    if dir_end > bytes.len() {
        return Err(PeError::TooSmall);
    }

    let name_rva = read_u32_le(bytes, dir_off + 12)?;
    let base = read_u32_le(bytes, dir_off + 16)?;
    let number_of_functions = read_u32_le(bytes, dir_off + 20)? as usize;
    let number_of_names = read_u32_le(bytes, dir_off + 24)? as usize;
    let addr_functions_rva = read_u32_le(bytes, dir_off + 28)?;
    let addr_names_rva = read_u32_le(bytes, dir_off + 32)?;
    let addr_ordinals_rva = read_u32_le(bytes, dir_off + 36)?;

    if number_of_functions > MAX_EXPORT_FUNCTIONS || number_of_names > MAX_EXPORT_NAMES {
        return Err(PeError::ExportTableTooLarge);
    }

    let export_dll_name = if name_rva != 0 {
        let name_off = rva_to_file_offset(name_rva, sections, headers.size_of_headers)
            .ok_or(PeError::RvaNotMapped(name_rva))?;
        Some(read_c_string(bytes, name_off)?)
    } else {
        None
    };

    if number_of_functions == 0 {
        return Ok((export_dll_name, Vec::new()));
    }

    let funcs_off = rva_to_file_offset(addr_functions_rva, sections, headers.size_of_headers)
        .ok_or(PeError::RvaNotMapped(addr_functions_rva))?;

    let mut names_by_func = vec![None::<String>; number_of_functions];
    if number_of_names > 0 {
        let names_off = rva_to_file_offset(addr_names_rva, sections, headers.size_of_headers)
            .ok_or(PeError::RvaNotMapped(addr_names_rva))?;
        let ord_off = rva_to_file_offset(addr_ordinals_rva, sections, headers.size_of_headers)
            .ok_or(PeError::RvaNotMapped(addr_ordinals_rva))?;

        for i in 0..number_of_names {
            let name_rva_entry = read_u32_le(bytes, names_off + i * 4)?;
            let ordinal_index = read_u16_le(bytes, ord_off + i * 2)? as usize;
            if ordinal_index >= number_of_functions {
                continue;
            }
            let name_off = rva_to_file_offset(name_rva_entry, sections, headers.size_of_headers)
                .ok_or(PeError::RvaNotMapped(name_rva_entry))?;
            names_by_func[ordinal_index] = Some(read_c_string(bytes, name_off)?);
        }
    }

    let mut exports = Vec::new();
    for idx in 0..number_of_functions {
        let func_rva = read_u32_le(bytes, funcs_off + idx * 4)?;
        if func_rva == 0 {
            continue;
        }

        exports.push(PeExport {
            ordinal: base + idx as u32,
            rva: func_rva,
            name: names_by_func[idx].clone(),
        });
    }

    Ok((export_dll_name, exports))
}

fn parse_relocations(
    bytes: &[u8],
    headers: &PeParsedHeaders,
    sections: &[PeSection],
) -> Result<Vec<PeRelocationEntry>, PeError> {
    if headers.reloc_dir_rva == 0 || headers.reloc_dir_size == 0 {
        return Ok(Vec::new());
    }

    let table_offset = rva_to_file_offset(headers.reloc_dir_rva, sections, headers.size_of_headers)
        .ok_or(PeError::RvaNotMapped(headers.reloc_dir_rva))?;

    let mut cursor = table_offset;
    let table_end = table_offset
        .checked_add(headers.reloc_dir_size as usize)
        .ok_or(PeError::TooSmall)?;
    if table_end > bytes.len() {
        return Err(PeError::TooSmall);
    }

    let mut relocations = Vec::new();
    while cursor + 8 <= table_end {
        let block_va = read_u32_le(bytes, cursor)?;
        let block_size = read_u32_le(bytes, cursor + 4)? as usize;
        if block_va == 0 && block_size == 0 {
            break;
        }
        if block_size < 8 {
            break;
        }

        let block_end = cursor.checked_add(block_size).ok_or(PeError::TooSmall)?;
        if block_end > table_end {
            return Err(PeError::TooSmall);
        }

        let entry_count = (block_size - 8) / 2;
        let mut off = cursor + 8;
        for _ in 0..entry_count {
            let raw = read_u16_le(bytes, off)?;
            let kind = ((raw >> 12) & 0x0F) as u8;
            let offset = raw & 0x0FFF;
            off += 2;
            if kind == 0 {
                continue;
            }
            relocations.push(PeRelocationEntry {
                kind,
                offset,
                target_rva: block_va.wrapping_add(offset as u32),
            });
        }

        cursor = block_end;
    }

    Ok(relocations)
}

pub fn apply_relocations(image: &mut LoadedPeImage, new_image_base: u64) -> Result<usize, PeError> {
    let old_base = image.metadata.image_base;
    if old_base == new_image_base {
        return Ok(0);
    }

    let delta = new_image_base as i128 - old_base as i128;
    let mut applied = 0usize;

    for entry in &image.relocations {
        let target = entry.target_rva as usize;
        match entry.kind {
            10 => {
                let end = target
                    .checked_add(8)
                    .ok_or(PeError::RelocationOutOfBounds(entry.target_rva))?;
                if end > image.mapped_image.len() {
                    return Err(PeError::RelocationOutOfBounds(entry.target_rva));
                }
                let mut raw = [0u8; 8];
                raw.copy_from_slice(&image.mapped_image[target..end]);
                let value = u64::from_le_bytes(raw);
                let patched = if delta >= 0 {
                    value.wrapping_add(delta as u64)
                } else {
                    value.wrapping_sub((-delta) as u64)
                };
                image.mapped_image[target..end].copy_from_slice(&patched.to_le_bytes());
                applied += 1;
            }
            3 => {
                let end = target
                    .checked_add(4)
                    .ok_or(PeError::RelocationOutOfBounds(entry.target_rva))?;
                if end > image.mapped_image.len() {
                    return Err(PeError::RelocationOutOfBounds(entry.target_rva));
                }
                let mut raw = [0u8; 4];
                raw.copy_from_slice(&image.mapped_image[target..end]);
                let value = u32::from_le_bytes(raw);
                let patched = if delta >= 0 {
                    value.wrapping_add(delta as u32)
                } else {
                    value.wrapping_sub((-delta) as u32)
                };
                image.mapped_image[target..end].copy_from_slice(&patched.to_le_bytes());
                applied += 1;
            }
            _ => {}
        }
    }

    image.metadata.image_base = new_image_base;
    Ok(applied)
}

pub fn parse_pe_metadata(bytes: &[u8]) -> Result<PeMetadata, PeError> {
    let headers = parse_pe_headers(bytes)?;
    Ok(headers.metadata)
}

pub fn load_pe_image(bytes: &[u8]) -> Result<LoadedPeImage, PeError> {
    let headers = parse_pe_headers(bytes)?;
    let sections = parse_sections(bytes, &headers)?;
    let mapped_image = map_image(bytes, &headers, &sections)?;
    let imports = parse_imports(bytes, &headers, &sections)?;
    let (export_dll_name, exports) = parse_exports(bytes, &headers, &sections)?;
    let relocations = parse_relocations(bytes, &headers, &sections)?;

    Ok(LoadedPeImage {
        metadata: headers.metadata,
        sections,
        imports,
        export_dll_name,
        exports,
        relocations,
        mapped_image,
    })
}

#[cfg(test)]
mod tests {
    use super::{PeError, PeImportSymbol, load_pe_image, parse_pe_metadata};

    fn minimal_pe_with_imports() -> Vec<u8> {
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
        b[optional + 16..optional + 20].copy_from_slice(&0x1000u32.to_le_bytes());
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

    fn minimal_pe_with_exports() -> Vec<u8> {
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

        b[0x450..0x454].copy_from_slice(&0u32.to_le_bytes());
        b[0x454..0x458].copy_from_slice(&0u32.to_le_bytes());
        b[0x458..0x45C].copy_from_slice(&0u32.to_le_bytes());
        b[0x45C..0x460].copy_from_slice(&0x2222u32.to_le_bytes());

        b[0x460..0x464].copy_from_slice(&0x3068u32.to_le_bytes());
        b[0x464..0x466].copy_from_slice(&3u16.to_le_bytes());

        let dll = b"KERNEL32.dll\0";
        b[0x440..0x440 + dll.len()].copy_from_slice(dll);

        let name = b"Sleep\0";
        b[0x468..0x468 + name.len()].copy_from_slice(name);

        b
    }

    fn minimal_pe_with_relocs() -> Vec<u8> {
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
        b[optional + 152..optional + 156].copy_from_slice(&0x3000u32.to_le_bytes());
        b[optional + 156..optional + 160].copy_from_slice(&12u32.to_le_bytes());

        let sh = optional + 0xF0;
        b[sh..sh + 8].copy_from_slice(b".text\0\0\0");
        b[sh + 8..sh + 12].copy_from_slice(&0x100u32.to_le_bytes());
        b[sh + 12..sh + 16].copy_from_slice(&0x1000u32.to_le_bytes());
        b[sh + 16..sh + 20].copy_from_slice(&0x200u32.to_le_bytes());
        b[sh + 20..sh + 24].copy_from_slice(&0x200u32.to_le_bytes());

        let sh2 = sh + 40;
        b[sh2..sh2 + 8].copy_from_slice(b".reloc\0\0");
        b[sh2 + 8..sh2 + 12].copy_from_slice(&0x100u32.to_le_bytes());
        b[sh2 + 12..sh2 + 16].copy_from_slice(&0x3000u32.to_le_bytes());
        b[sh2 + 16..sh2 + 20].copy_from_slice(&0x200u32.to_le_bytes());
        b[sh2 + 20..sh2 + 24].copy_from_slice(&0x400u32.to_le_bytes());

        b[0x200..0x208].copy_from_slice(&0x0000_0001_8000_1000u64.to_le_bytes());

        b[0x400..0x404].copy_from_slice(&0x1000u32.to_le_bytes());
        b[0x404..0x408].copy_from_slice(&12u32.to_le_bytes());
        b[0x408..0x40A].copy_from_slice(&0xA000u16.to_le_bytes());
        b[0x40A..0x40C].copy_from_slice(&0u16.to_le_bytes());

        b
    }

    #[test]
    fn parses_minimal_pe_metadata() {
        let pe = minimal_pe_with_imports();
        let meta = parse_pe_metadata(&pe).expect("expected valid PE");
        assert_eq!(meta.machine, 0x8664);
        assert_eq!(meta.number_of_sections, 2);
        assert_eq!(meta.entry_point_rva, 0x1000);
        assert_eq!(meta.size_of_image, 0x4000);
        assert_eq!(meta.image_base, 0x0000_0001_8000_0000);
    }

    #[test]
    fn maps_sections_and_imports() {
        let pe = minimal_pe_with_imports();
        let loaded = load_pe_image(&pe).expect("must load PE");
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
    fn parses_export_table() {
        let pe = minimal_pe_with_exports();
        let loaded = load_pe_image(&pe).expect("must load export PE");
        assert_eq!(loaded.export_dll_name.as_deref(), Some("KERNEL32.dll"));
        assert_eq!(loaded.exports.len(), 1);
        assert_eq!(loaded.exports[0].ordinal, 0x123);
        assert_eq!(loaded.exports[0].rva, 0x2222);
        assert_eq!(loaded.exports[0].name.as_deref(), Some("Sleep"));
    }

    #[test]
    fn applies_dir64_relocation_delta() {
        let mut image = load_pe_image(&minimal_pe_with_relocs()).expect("must load reloc PE");
        assert_eq!(image.relocations.len(), 1);
        assert_eq!(image.relocations[0].kind, 10);
        assert_eq!(image.relocations[0].target_rva, 0x1000);

        let mut before_raw = [0u8; 8];
        before_raw.copy_from_slice(&image.mapped_image[0x1000..0x1008]);
        let before = u64::from_le_bytes(before_raw);
        assert_eq!(before, 0x0000_0001_8000_1000);

        let applied = super::apply_relocations(&mut image, 0x0000_0001_9000_0000)
            .expect("relocation apply must succeed");
        assert_eq!(applied, 1);
        assert_eq!(image.metadata.image_base, 0x0000_0001_9000_0000);

        let mut after_raw = [0u8; 8];
        after_raw.copy_from_slice(&image.mapped_image[0x1000..0x1008]);
        let after = u64::from_le_bytes(after_raw);
        assert_eq!(after, 0x0000_0001_9000_1000);
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
