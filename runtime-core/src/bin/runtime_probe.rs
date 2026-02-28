use std::env;
use std::fs;
use std::process::ExitCode;

use runtime_core::RuntimeCore;

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

    let core = RuntimeCore::new();
    match core.load_pe_image(&bytes) {
        Ok(report) => {
            println!("PE probe success");
            println!("machine: 0x{:04x}", report.metadata.machine);
            println!("sections: {}", report.metadata.number_of_sections);
            println!("entry_point_rva: 0x{:08x}", report.metadata.entry_point_rva);
            println!("size_of_image: {}", report.metadata.size_of_image);
            ExitCode::SUCCESS
        }
        Err(err) => {
            eprintln!("PE probe failed: {err:?}");
            ExitCode::from(1)
        }
    }
}
