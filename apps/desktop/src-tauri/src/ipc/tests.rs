//! Tests for the IPC surface: DTO validation, the command allowlist, and the security settings
//! in `tauri.conf.json` and the capability files (LL-002, LL-005, NFR-014).

use std::path::{Path, PathBuf};

use serde_json::Value;

use super::commands::ping;
use super::dto::{IpcCommand, IpcErrorCode, MAX_NONCE_LEN, PingRequest};

fn manifest_dir() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

fn read_json(path: &Path) -> Value {
    let text = std::fs::read_to_string(path).unwrap();
    serde_json::from_str(&text).unwrap()
}

fn request(nonce: &str) -> PingRequest {
    PingRequest {
        nonce: nonce.to_owned(),
    }
}

#[test]
fn ping_echoes_valid_nonce_and_reports_version() {
    let response = ping(request("abc-123")).unwrap();
    assert_eq!(response.nonce, "abc-123");
    assert_eq!(response.core_version, env!("CARGO_PKG_VERSION"));
}

#[test]
fn ping_rejects_invalid_nonces() {
    let too_long = "a".repeat(MAX_NONCE_LEN + 1);
    for nonce in [
        "",
        too_long.as_str(),
        "has space",
        "<script>",
        "ünïcode",
        "a/b",
        "nul\0",
    ] {
        let error = ping(request(nonce)).unwrap_err();
        assert_eq!(error.code, IpcErrorCode::InvalidArgument, "nonce {nonce:?}");
    }
    assert!(ping(request(&"a".repeat(MAX_NONCE_LEN))).is_ok());
}

#[test]
fn ping_request_rejects_unknown_fields() {
    let result: Result<PingRequest, _> = serde_json::from_str(r#"{"nonce":"a","command":"rm"}"#);
    assert!(result.is_err());
    let result: Result<PingRequest, _> = serde_json::from_str(r#"{"nonce":"a"}"#);
    assert!(result.is_ok());
}

#[test]
fn error_serializes_to_the_shape_the_ui_expects() {
    let error = ping(request("")).unwrap_err();
    let value = serde_json::to_value(&error).unwrap();
    assert_eq!(value["code"], "invalid_argument");
    assert!(value["message"].as_str().unwrap().contains("nonce"));
}

/// The command allowlist is declared in four places; they must agree exactly.
#[test]
fn command_allowlist_agrees_everywhere() {
    let commands: Vec<&str> = IpcCommand::ALL.iter().map(|c| c.name()).collect();

    let build_rs = std::fs::read_to_string(manifest_dir().join("build.rs")).unwrap();
    let declared = format!(
        ".commands(&[{}])",
        commands
            .iter()
            .map(|c| format!("\"{c}\""))
            .collect::<Vec<_>>()
            .join(", ")
    );
    assert!(
        build_rs.contains(&declared),
        "build.rs must declare exactly {declared}"
    );

    let capability = read_json(&manifest_dir().join("capabilities/main.json"));
    let granted: Vec<&str> = capability["permissions"]
        .as_array()
        .unwrap()
        .iter()
        .map(|p| p.as_str().unwrap())
        .collect();
    let expected: Vec<String> = commands
        .iter()
        .map(|c| format!("allow-{}", c.replace('_', "-")))
        .collect();
    assert_eq!(
        granted, expected,
        "capability must grant exactly the allowlisted commands and nothing else"
    );

    let isolation = std::fs::read_to_string(manifest_dir().join("../isolation/index.js")).unwrap();
    let listed = format!(
        "Object.freeze([{}])",
        commands
            .iter()
            .map(|c| format!("\"{c}\""))
            .collect::<Vec<_>>()
            .join(", ")
    );
    assert!(
        isolation.contains(&listed),
        "isolation hook must allow exactly {listed}"
    );
}

#[test]
fn only_one_capability_file_exists() {
    let files: Vec<_> = std::fs::read_dir(manifest_dir().join("capabilities"))
        .unwrap()
        .map(|e| e.unwrap().file_name())
        .collect();
    assert_eq!(files, vec![std::ffi::OsString::from("main.json")]);
}

#[test]
fn security_configuration_is_strict() {
    let config = read_json(&manifest_dir().join("tauri.conf.json"));
    let security = &config["app"]["security"];
    for key in ["csp", "devCsp"] {
        let csp = &security[key];
        assert_eq!(csp["default-src"], "'self'", "{key}");
        assert_eq!(csp["script-src"], "'self'", "{key}");
        assert_eq!(csp["object-src"], "'none'", "{key}");
        for (_, value) in csp.as_object().unwrap() {
            let value = value.as_str().unwrap();
            for remote in ["https:", "http:*", "*", "'unsafe-eval'"] {
                assert!(
                    !value.split_whitespace().any(|token| token == remote),
                    "{key} allows {remote}"
                );
            }
            assert!(
                !value.contains("https://"),
                "{key} allows a remote origin: {value}"
            );
        }
    }
    assert_eq!(security["csp"]["style-src"], "'self'");
    assert_eq!(security["freezePrototype"], true);
    assert_eq!(security["pattern"]["use"], "isolation");
    assert_eq!(config["app"]["withGlobalTauri"], false);
    assert!(
        config
            .get("plugins")
            .is_none_or(|p| p.as_object().is_none_or(serde_json::Map::is_empty))
    );
}

#[test]
fn shared_index_exports_every_generated_type() {
    let shared = manifest_dir().join("../../../packages/shared/src");
    let index = std::fs::read_to_string(shared.join("index.ts")).unwrap();
    for entry in std::fs::read_dir(shared.join("generated")).unwrap() {
        let name = entry
            .unwrap()
            .file_name()
            .to_string_lossy()
            .trim_end_matches(".ts")
            .to_owned();
        assert!(
            index.contains(&format!("from \"./generated/{name}\"")),
            "index.ts must re-export {name}"
        );
    }
}

/// Drives the real command handler and ACL through Tauri's mock runtime: `ping` is answered and
/// any other command is refused (TC-110 groundwork; the full IPC test is LL-052).
#[test]
fn mock_runtime_answers_ping_and_refuses_other_commands() {
    use tauri::ipc::{CallbackFn, InvokeBody};
    use tauri::test::{INVOKE_KEY, get_ipc_response, mock_builder};
    use tauri::webview::InvokeRequest;

    // The real generated context, so the real capability file and ACL apply.
    let app = crate::builder_with(mock_builder())
        .build(crate::context())
        .unwrap();
    let webview = tauri::WebviewWindowBuilder::new(&app, "main", Default::default())
        .build()
        .unwrap();
    let invoke = |cmd: &str| {
        get_ipc_response(
            &webview,
            InvokeRequest {
                cmd: cmd.into(),
                callback: CallbackFn(0),
                error: CallbackFn(1),
                url: if cfg!(windows) {
                    "http://tauri.localhost"
                } else {
                    "tauri://localhost"
                }
                .parse()
                .unwrap(),
                body: InvokeBody::Json(serde_json::json!({ "request": { "nonce": "n-1" } })),
                headers: Default::default(),
                invoke_key: INVOKE_KEY.to_string(),
            },
        )
    };
    let pong = invoke("ping").unwrap().deserialize::<Value>().unwrap();
    assert_eq!(pong["nonce"], "n-1");
    for refused in [
        "shell_exec",
        "plugin:fs|read_file",
        "plugin:shell|execute",
        "PING",
    ] {
        assert!(invoke(refused).is_err(), "{refused} must be refused");
    }
}
