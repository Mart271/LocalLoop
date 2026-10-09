//! Declares the application's IPC commands so that each needs an explicit permission in a
//! capability file. A command missing from this list cannot be granted (NFR-014).
fn main() {
    tauri_build::try_build(
        tauri_build::Attributes::new()
            .app_manifest(tauri_build::AppManifest::new().commands(&["ping"])),
    )
    .unwrap_or_else(|error| {
        eprintln!("tauri build script failed: {error:#}");
        std::process::exit(1);
    });
}
