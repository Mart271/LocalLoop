//! SPIKE (LL-010, D-07): encryption at rest. Throwaway code; never shipped.
//!
//! Build and run once per option:
//!   cargo run --release --features option-a-sqlcipher
//!   cargo run --release --features option-b-app-level
//!
//! Both options keep a random 256-bit key in the OS credential store (keyring crate) and encrypt
//! evidence files with XChaCha20-Poly1305. They differ in how the database is protected:
//!   A: SQLCipher encrypts every database page.
//!   B: plain SQLite; only columns classified *sensitive* are encrypted by the application.
//! Prints MEASURE lines for docs/development/spikes/D-07-encryption.md.

#[cfg(all(feature = "option-a-sqlcipher", feature = "option-b-app-level"))]
compile_error!("enable exactly one option feature");

use std::path::{Path, PathBuf};
use std::time::Instant;

use chacha20poly1305::aead::{Aead, KeyInit, Payload};
use chacha20poly1305::{XChaCha20Poly1305, XNonce};
use rand::RngCore;
use rusqlite::{Connection, params};

const ROWS: usize = 10_000;
const EVIDENCE_FILES: usize = 20;
const EVIDENCE_SIZE: usize = 256 * 1024;
const SEED_SECRET: &str = "SEEDSECRET-7f3a";
const SEED_INTERNAL: &str = "Bluefin Office Supplies Co.";
const SERVICE: &str = "LocalLoop spike LL-010";

#[cfg(feature = "option-a-sqlcipher")]
const OPTION: &str = "A-sqlcipher";
#[cfg(feature = "option-b-app-level")]
const OPTION: &str = "B-app-level";

fn ms(started: Instant) -> f64 {
    started.elapsed().as_secs_f64() * 1000.0
}

fn measure(label: &str, value: impl std::fmt::Display) {
    println!("MEASURE {OPTION} {label}: {value}");
}

struct Sealer(XChaCha20Poly1305);

impl Sealer {
    /// nonce (24 bytes) || ciphertext+tag. The associated data binds the value to where it is
    /// stored, so ciphertext cannot be moved between rows, columns, or files unnoticed.
    fn seal(&self, plaintext: &[u8], aad: &[u8]) -> Vec<u8> {
        let mut nonce = [0u8; 24];
        rand::rng().fill_bytes(&mut nonce);
        let mut out = nonce.to_vec();
        out.extend(self.0.encrypt(XNonce::from_slice(&nonce), Payload { msg: plaintext, aad }).unwrap());
        out
    }

    fn open(&self, sealed: &[u8], aad: &[u8]) -> Option<Vec<u8>> {
        let (nonce, body) = sealed.split_at_checked(24)?;
        self.0.decrypt(XNonce::from_slice(nonce), Payload { msg: body, aad }).ok()
    }
}

fn open_db(path: &Path, key: &[u8; 32]) -> Connection {
    let conn = Connection::open(path).unwrap();
    #[cfg(feature = "option-a-sqlcipher")]
    {
        let hex: String = key.iter().map(|b| format!("{b:02x}")).collect();
        conn.execute_batch(&format!("PRAGMA key = \"x'{hex}'\";")).unwrap();
    }
    #[cfg(feature = "option-b-app-level")]
    let _ = key;
    conn.execute_batch("PRAGMA journal_mode = WAL; PRAGMA foreign_keys = ON;").unwrap();
    conn
}

fn files_in(dir: &Path) -> Vec<PathBuf> {
    let mut out = Vec::new();
    for entry in std::fs::read_dir(dir).unwrap() {
        let path = entry.unwrap().path();
        if path.is_dir() {
            out.extend(files_in(&path));
        } else {
            out.push(path);
        }
    }
    out
}

fn count_occurrences(dir: &Path, needle: &str) -> usize {
    files_in(dir)
        .iter()
        .map(|file| std::fs::read(file).unwrap().windows(needle.len()).filter(|w| *w == needle.as_bytes()).count())
        .sum()
}

fn main() {
    // 1. Key in the OS credential store.
    let entry = keyring::Entry::new(SERVICE, "data-key").unwrap();
    let mut key = [0u8; 32];
    rand::rng().fill_bytes(&mut key);
    let started = Instant::now();
    let stored = entry.set_secret(&key);
    measure("keyring_store_ms", format!("{:.2} ({})", ms(started), if stored.is_ok() { "ok" } else { "FAILED" }));
    if let Err(error) = &stored {
        measure("keyring_error", error);
    }
    let started = Instant::now();
    let loaded = entry.get_secret();
    measure("keyring_load_ms", format!("{:.2}", ms(started)));
    let key: [u8; 32] = match loaded {
        Ok(bytes) if bytes.len() == 32 => bytes.try_into().unwrap(),
        _ => {
            measure("keyring_roundtrip", "FAILED; continuing with an in-memory key");
            key
        }
    };
    let sealer = Sealer(XChaCha20Poly1305::new((&key).into()));

    // 2. Database with sensitive and internal columns.
    let dir = std::env::temp_dir().join(format!("localloop-spike-ll010-{OPTION}"));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(dir.join("evidence")).unwrap();
    let db_path = dir.join("localloop.db");
    let conn = open_db(&db_path, &key);
    conn.execute_batch(
        "CREATE TABLE records (id INTEGER PRIMARY KEY, vendor TEXT NOT NULL, invoice_no TEXT NOT NULL UNIQUE,
                               total BLOB NOT NULL, note BLOB NOT NULL);",
    )
    .unwrap();

    let started = Instant::now();
    let tx = conn.unchecked_transaction().unwrap();
    {
        let mut insert = tx.prepare("INSERT INTO records (id, vendor, invoice_no, total, note) VALUES (?1, ?2, ?3, ?4, ?5)").unwrap();
        for i in 0..ROWS {
            let id = i as i64;
            let total = format!("{}.{:02}", 1000 + i, i % 100).into_bytes();
            let note = format!("{SEED_SECRET} row {i}").into_bytes();
            #[cfg(feature = "option-b-app-level")]
            let (total, note) = (
                sealer.seal(&total, format!("records.total.{id}").as_bytes()),
                sealer.seal(&note, format!("records.note.{id}").as_bytes()),
            );
            insert.execute(params![id, SEED_INTERNAL, format!("BOS-2026-{i:05}"), total, note]).unwrap();
        }
    }
    tx.commit().unwrap();
    measure("insert_10k_rows_ms", format!("{:.1}", ms(started)));

    let started = Instant::now();
    let mut read = conn.prepare("SELECT id, total, note FROM records").unwrap();
    let mut decrypted = 0usize;
    let rows = read.query_map([], |r| Ok((r.get::<_, i64>(0)?, r.get::<_, Vec<u8>>(1)?, r.get::<_, Vec<u8>>(2)?))).unwrap();
    for row in rows {
        let (id, total, note) = row.unwrap();
        #[cfg(feature = "option-b-app-level")]
        let (total, note) = (
            sealer.open(&total, format!("records.total.{id}").as_bytes()).unwrap(),
            sealer.open(&note, format!("records.note.{id}").as_bytes()).unwrap(),
        );
        let _ = id;
        decrypted += total.len() + note.len();
    }
    measure("read_all_10k_rows_ms", format!("{:.1} ({decrypted} plaintext bytes)", ms(started)));

    let started = Instant::now();
    for i in (0..ROWS).step_by(10) {
        let _: i64 = conn.query_row("SELECT id FROM records WHERE invoice_no = ?1", [format!("BOS-2026-{i:05}")], |r| r.get(0)).unwrap();
    }
    measure("1000_point_lookups_ms", format!("{:.1}", ms(started)));

    // Tampering with a row's ciphertext (B) is detected.
    #[cfg(feature = "option-b-app-level")]
    {
        let sealed: Vec<u8> = conn.query_row("SELECT note FROM records WHERE id = 1", [], |r| r.get(0)).unwrap();
        let moved = sealer.open(&sealed, b"records.note.2").is_none();
        let mut flipped = sealed.clone();
        if let Some(last) = flipped.last_mut() {
            *last ^= 1;
        }
        let tampered = sealer.open(&flipped, b"records.note.1").is_none();
        measure("tamper_detected", format!("moved_between_rows={moved} bit_flip={tampered}"));
    }
    drop(read);

    // 3. Evidence files (both options use the same file encryption).
    let started = Instant::now();
    let mut payload = vec![b'x'; EVIDENCE_SIZE];
    payload[..SEED_SECRET.len()].copy_from_slice(SEED_SECRET.as_bytes());
    for i in 0..EVIDENCE_FILES {
        let name = format!("evidence-{i}.bin");
        std::fs::write(dir.join("evidence").join(&name), sealer.seal(&payload, name.as_bytes())).unwrap();
    }
    measure("encrypt_evidence_ms", format!("{:.1} ({EVIDENCE_FILES} x {} KiB)", ms(started), EVIDENCE_SIZE / 1024));
    let started = Instant::now();
    for i in 0..EVIDENCE_FILES {
        let name = format!("evidence-{i}.bin");
        let sealed = std::fs::read(dir.join("evidence").join(&name)).unwrap();
        assert_eq!(sealer.open(&sealed, name.as_bytes()).unwrap().len(), EVIDENCE_SIZE);
    }
    measure("decrypt_evidence_ms", format!("{:.1}", ms(started)));

    // 4. Checkpoint the WAL, then scan every file for plaintext.
    conn.execute_batch("PRAGMA wal_checkpoint(TRUNCATE);").unwrap();
    let db_size = std::fs::metadata(&db_path).unwrap().len();
    measure("db_size_kib", db_size / 1024);
    let header = std::fs::read(&db_path).unwrap();
    measure("db_has_plain_sqlite_header", header.starts_with(b"SQLite format 3\0"));
    measure("plaintext_sensitive_hits_with_db_open", count_occurrences(&dir, SEED_SECRET));
    drop(conn);
    measure("plaintext_sensitive_hits_after_close", count_occurrences(&dir, SEED_SECRET));
    measure("plaintext_internal_metadata_hits", count_occurrences(&dir, SEED_INTERNAL));

    // Opening without the key must fail (A) or yield only ciphertext for sensitive columns (B).
    let stranger = Connection::open(&db_path).unwrap();
    let outcome = stranger.query_row("SELECT count(*) FROM records", [], |r| r.get::<_, i64>(0));
    measure("open_without_key", match outcome {
        Ok(n) => format!("readable ({n} rows; sensitive columns are ciphertext)"),
        Err(error) => format!("refused: {error}"),
    });
    drop(stranger);

    // 5. Clean up the credential store entry and the temporary folder.
    measure("keyring_delete", if entry.delete_credential().is_ok() { "ok" } else { "FAILED" });
    let _ = std::fs::remove_dir_all(&dir);
    measure("os", format!("{} {}", std::env::consts::OS, std::env::consts::ARCH));
}
