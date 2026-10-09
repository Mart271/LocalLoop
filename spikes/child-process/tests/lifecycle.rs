//! SPIKE (LL-011) measurements. Run: cargo test --release -- --nocapture --test-threads=1
//! Prints `MEASURE` lines that docs/development/spikes/LL-011-child-processes.md reports.

#![forbid(unsafe_code)]

use std::io::{BufRead, BufReader, Write};
use std::process::{Child, Command, Stdio};
use std::time::{Duration, Instant};

use spike_child_process::sha256_hex;
use sysinfo::{Pid, ProcessRefreshKind, ProcessesToUpdate, System};

const WORKER: &str = env!("CARGO_BIN_EXE_worker");
const SUPERVISOR: &str = env!("CARGO_BIN_EXE_supervisor");

fn worker_hash() -> String {
    sha256_hex(&std::fs::read(WORKER).unwrap())
}

fn start(worker: &str, hash: &str, scenario: &str) -> (Child, Vec<(String, String)>) {
    start_with(worker, hash, scenario, &[])
}

fn start_with(
    worker: &str,
    hash: &str,
    scenario: &str,
    env: &[(&str, &str)],
) -> (Child, Vec<(String, String)>) {
    let mut child = Command::new(SUPERVISOR)
        .args([worker, hash, scenario])
        .envs(env.iter().copied())
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    let mut lines = BufReader::new(child.stdout.take().unwrap()).lines();
    let mut facts = Vec::new();
    // Read until the supervisor has reported both child PIDs (or ended).
    while let Some(Ok(line)) = lines.next() {
        for part in line.split(' ') {
            if let Some((k, v)) = part.split_once('=') {
                facts.push((k.to_owned(), v.to_owned()));
            }
        }
        let done = if scenario == "wait_hung" {
            line.starts_with("HUNG")
        } else {
            line.starts_with("GRANDCHILD_PID")
        };
        if done || line.starts_with("REFUSED") || line.starts_with("ERROR") {
            break;
        }
    }
    std::thread::spawn(move || for _ in lines {});
    (child, facts)
}

fn fact(facts: &[(String, String)], key: &str) -> Option<String> {
    facts.iter().find(|(k, _)| k == key).map(|(_, v)| v.clone())
}

fn alive(system: &mut System, pid: u32) -> bool {
    system.refresh_processes_specifics(
        ProcessesToUpdate::Some(&[Pid::from_u32(pid)]),
        true,
        ProcessRefreshKind::nothing(),
    );
    system.process(Pid::from_u32(pid)).is_some()
}

/// Time until both PIDs have disappeared, or None after 10 s.
fn time_until_gone(pids: &[u32]) -> Option<Duration> {
    let mut system = System::new();
    let started = Instant::now();
    while started.elapsed() < Duration::from_secs(10) {
        if pids.iter().all(|&pid| !alive(&mut system, pid)) {
            return Some(started.elapsed());
        }
        std::thread::sleep(Duration::from_millis(2));
    }
    None
}

fn pids(facts: &[(String, String)]) -> Vec<u32> {
    ["WORKER_PID", "GRANDCHILD_PID"]
        .iter()
        .map(|k| fact(facts, k).unwrap().parse().unwrap())
        .collect()
}

fn summary(label: &str, mut ms: Vec<f64>) {
    ms.sort_by(f64::total_cmp);
    let n = ms.len();
    println!(
        "MEASURE {label}: n={n} min={:.1}ms median={:.1}ms p95={:.1}ms max={:.1}ms",
        ms[0],
        ms[n / 2],
        ms[(n * 95 / 100).min(n - 1)],
        ms[n - 1]
    );
}

#[test]
fn workers_die_when_supervisor_is_killed_abruptly() {
    let hash = worker_hash();
    let mut gone_ms = Vec::new();
    let mut spawn_ms = Vec::new();
    for _ in 0..20 {
        let (mut supervisor, facts) = start(WORKER, &hash, "wait");
        let children = pids(&facts);
        spawn_ms.push(fact(&facts, "SPAWN_MS").unwrap().parse().unwrap());
        supervisor.kill().unwrap(); // TerminateProcess on Windows, SIGKILL on Unix: no cleanup code runs
        supervisor.wait().unwrap();
        let gone = time_until_gone(&children).expect("worker or grandchild survived the supervisor for 10 s");
        gone_ms.push(gone.as_secs_f64() * 1000.0);
    }
    summary("spawn_to_first_frame", spawn_ms);
    summary("abrupt_kill_children_gone", gone_ms);
}

#[test]
fn workers_die_when_supervisor_exits_normally() {
    let mut gone_ms = Vec::new();
    for _ in 0..10 {
        let (mut supervisor, facts) = start(WORKER, &worker_hash(), "exit");
        let children = pids(&facts);
        assert!(supervisor.wait().unwrap().success());
        gone_ms.push(
            time_until_gone(&children)
                .expect("children survived a normal exit")
                .as_secs_f64()
                * 1000.0,
        );
    }
    summary("normal_exit_children_gone", gone_ms);
}

#[test]
fn hung_worker_is_killed_after_timeout() {
    let (mut supervisor, facts) = start(WORKER, &worker_hash(), "timeout");
    let children = pids(&facts);
    assert!(supervisor.wait().unwrap().success());
    let gone = time_until_gone(&children).expect("hung worker survived");
    println!(
        "MEASURE hung_worker_gone_after_supervisor_kill: {:.1}ms",
        gone.as_secs_f64() * 1000.0
    );
}

#[test]
fn crashed_worker_is_detected() {
    let mut out = String::new();
    let mut child = Command::new(SUPERVISOR)
        .args([WORKER, &worker_hash(), "crash"])
        .stdout(Stdio::piped())
        .spawn()
        .unwrap();
    std::io::Read::read_to_string(child.stdout.as_mut().unwrap(), &mut out).unwrap();
    assert!(child.wait().unwrap().success());
    assert!(out.contains("CRASH_REPLY=false"), "{out}");
    println!(
        "MEASURE crash: {}",
        out.lines().find(|l| l.starts_with("CRASH")).unwrap_or("")
    );
}

#[test]
fn tampered_worker_is_refused_before_spawn() {
    let tampered = std::env::temp_dir().join(format!(
        "spike-worker-tampered-{}{}",
        std::process::id(),
        std::env::consts::EXE_SUFFIX
    ));
    let mut bytes = std::fs::read(WORKER).unwrap();
    bytes.push(0);
    let mut file = std::fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&tampered)
        .unwrap();
    file.write_all(&bytes).unwrap();
    drop(file);
    let (mut supervisor, facts) = start(tampered.to_str().unwrap(), &worker_hash(), "exit");
    let status = supervisor.wait().unwrap();
    assert_eq!(status.code(), Some(3));
    assert!(fact(&facts, "REFUSED").is_some());
    assert!(
        fact(&facts, "WORKER_PID").is_none(),
        "tampered worker must never start"
    );
    println!(
        "MEASURE tampered: refused with exit 3, hash took {}ms",
        fact(&facts, "HASH_MS").unwrap_or_default()
    );
    let _ = std::fs::remove_file(tampered);
}

/// Abrupt supervisor death while the worker's main thread is hung (stuck parser), under each
/// combination of safeguards. Returns whether worker and grandchild were gone within 10 s.
fn hung_case(label: &str, env: &[(&str, &str)]) -> bool {
    let (mut supervisor, facts) = start_with(WORKER, &worker_hash(), "wait_hung", env);
    let children = pids(&facts);
    supervisor.kill().unwrap();
    supervisor.wait().unwrap();
    let gone = time_until_gone(&children);
    match gone {
        Some(d) => println!(
            "MEASURE hung_{label}: children gone after {:.1}ms",
            d.as_secs_f64() * 1000.0
        ),
        None => {
            println!("MEASURE hung_{label}: children STILL RUNNING after 10 s");
            let mut system = System::new();
            for pid in children {
                system.refresh_processes(ProcessesToUpdate::Some(&[Pid::from_u32(pid)]), true);
                if let Some(process) = system.process(Pid::from_u32(pid)) {
                    process.kill(); // clean up the orphan the negative control created
                }
            }
        }
    }
    gone.is_some()
}

#[test]
fn hung_worker_dies_with_both_safeguards() {
    assert!(hung_case("job_and_watchdog", &[]));
}

#[test]
fn hung_worker_dies_with_watchdog_only() {
    assert!(hung_case("watchdog_only", &[("LOCALLOOP_SPIKE_NO_JOB", "1")]));
}

#[test]
fn hung_worker_with_job_only() {
    // Expected: dies on Windows (job object kills it); survives on macOS (process groups are not
    // killed when the parent dies). Assert containment on Windows and report other platforms.
    let gone = hung_case("job_only", &[("LOCALLOOP_SPIKE_NO_WATCHDOG", "1")]);
    if cfg!(windows) {
        assert!(gone, "Windows job object must contain a hung worker");
    }
    println!("MEASURE hung_job_only_os={} gone={gone}", std::env::consts::OS);
}

#[test]
fn hung_worker_without_safeguards_is_orphaned() {
    let gone = hung_case(
        "none",
        &[
            ("LOCALLOOP_SPIKE_NO_JOB", "1"),
            ("LOCALLOOP_SPIKE_NO_WATCHDOG", "1"),
        ],
    );
    assert!(
        !gone,
        "negative control: without either safeguard the hung worker should be orphaned"
    );
}
