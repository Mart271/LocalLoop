//! LocalLoop desktop entry point.
#![forbid(unsafe_code)]
// Hide the console window on Windows release builds.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() -> std::process::ExitCode {
    match localloop_desktop_lib::run() {
        Ok(()) => std::process::ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("LocalLoop could not start: {error}");
            std::process::ExitCode::FAILURE
        }
    }
}
