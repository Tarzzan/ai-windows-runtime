use std::env;
use std::fs;
use std::process::ExitCode;

use runtime_core::{PeImportSymbol, load_pe_image};

fn main() -> ExitCode {
    let path = match env::args().nth(1) {
        Some(p) => p,
        None => {
            eprintln!("usage: runtime_probe <path-to-exe>");
            return ExitCode::from(2);
        }
    };

    let bytes = match fs::read(&path) {
        Ok(b) => b,
        Err(err) => {
            eprintln!("read failed for {path}: {err}");
            return ExitCode::from(3);
        }
    };

    match load_pe_image(&bytes) {
        Ok(image) => {
            println!("PE probe success");
            println!("machine: 0x{:04x}", image.metadata.machine);
            println!("sections: {}", image.sections.len());
            println!("imports: {}", image.imports.len());
            println!("entry_point_rva: 0x{:08x}", image.metadata.entry_point_rva);
            println!("size_of_image: {}", image.metadata.size_of_image);
            for import in &image.imports {
                println!("import dll: {}", import.dll_name);
                for f in &import.functions {
                    match &f.symbol {
                        PeImportSymbol::Name { hint, name } => {
                            println!("  - {name} (hint {hint})");
                        }
                        PeImportSymbol::Ordinal(ord) => {
                            println!("  - ordinal #{ord}");
                        }
                    }
                }
            }
            ExitCode::SUCCESS
        }
        Err(err) => {
            eprintln!("PE probe failed: {err:?}");
            ExitCode::from(1)
        }
    }
}
