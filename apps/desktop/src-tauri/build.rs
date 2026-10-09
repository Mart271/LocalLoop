//! Declares the application's IPC commands so that each needs an explicit permission in a
//! capability file. A command missing from this list cannot be granted (NFR-014).
fn main() {
    let mut attributes =
        tauri_build::Attributes::new().app_manifest(tauri_build::AppManifest::new().commands(&["ping"]));
    // Test executables need the Common Controls v6 manifest too, or Windows refuses to start them
    // (STATUS_ENTRYPOINT_NOT_FOUND). Embed it through the linker for every target instead of
    // letting tauri-build add it to the application binary only.
    if std::env::var("CARGO_CFG_TARGET_ENV").as_deref() == Ok("msvc") {
        attributes =
            attributes.windows_attributes(tauri_build::WindowsAttributes::new_without_app_manifest());
        println!("cargo:rustc-link-arg=/MANIFEST:EMBED");
        println!(
            "cargo:rustc-link-arg=/MANIFESTDEPENDENCY:type='win32' name='Microsoft.Windows.Common-Controls' \
             version='6.0.0.0' processorArchitecture='*' publicKeyToken='6595b64144ccf1df' language='*'"
        );
    }
    tauri_build::try_build(attributes).unwrap_or_else(|error| {
        eprintln!("tauri build script failed: {error:#}");
        std::process::exit(1);
    });
}
