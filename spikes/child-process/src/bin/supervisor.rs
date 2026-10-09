//! SPIKE (LL-011): a stand-in for LocalLoop's worker supervisor, on Tokio like the real app.
//!
//! Usage: supervisor <worker path> <expected sha256> <scenario>
//! Scenarios: wait (idle until killed), exit (return normally), timeout (kill a hung worker),
//! crash (observe a worker crash). Prints `KEY=value` lines for the test harness.
//!
//! Finding: process-wrap's *std* JobObject never sets JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE; only
//! the Tokio frontend's `KillOnDrop` does. LocalLoop must use the Tokio frontend.

use std::io::Write;
use std::process::{ExitCode, Stdio};
use std::time::{Duration, Instant};

use process_wrap::tokio::*;
use spike_child_process::sha256_hex;
use tokio::io::{AsyncReadExt, AsyncWriteExt};

fn say(line: &str) {
    let mut out = std::io::stdout().lock();
    let _ = writeln!(out, "{line}");
    let _ = out.flush();
}

async fn send(stdin: &mut tokio::process::ChildStdin, text: &str) -> std::io::Result<()> {
    let len = u32::try_from(text.len()).map_err(std::io::Error::other)?;
    stdin.write_all(&len.to_be_bytes()).await?;
    stdin.write_all(text.as_bytes()).await?;
    stdin.flush().await
}

async fn recv(stdout: &mut tokio::process::ChildStdout) -> Option<String> {
    let mut len = [0u8; 4];
    stdout.read_exact(&mut len).await.ok()?;
    let mut buf = vec![0u8; u32::from_be_bytes(len) as usize];
    stdout.read_exact(&mut buf).await.ok()?;
    String::from_utf8(buf).ok()
}

async fn ask(
    stdin: &mut tokio::process::ChildStdin,
    stdout: &mut tokio::process::ChildStdout,
    text: &str,
    timeout: Duration,
) -> Option<String> {
    send(stdin, text).await.ok()?;
    tokio::time::timeout(timeout, recv(stdout)).await.ok().flatten()
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> ExitCode {
    let args: Vec<String> = std::env::args().collect();
    let [_, worker, expected, scenario] = args.as_slice() else {
        eprintln!("usage: supervisor <worker> <sha256> <scenario>");
        return ExitCode::from(2);
    };

    // NFR-018: verify the worker binary before starting it.
    let started = Instant::now();
    let actual = match std::fs::read(worker) {
        Ok(bytes) => sha256_hex(&bytes),
        Err(error) => {
            say(&format!("ERROR=cannot read worker: {error}"));
            return ExitCode::from(3);
        }
    };
    say(&format!("HASH_MS={:.2}", started.elapsed().as_secs_f64() * 1000.0));
    if &actual != expected {
        say("REFUSED=checksum mismatch");
        return ExitCode::from(3);
    }

    let spawn_started = Instant::now();
    let mut command = CommandWrap::with_new(worker, |c| {
        c.stdin(Stdio::piped()).stdout(Stdio::piped()).stderr(Stdio::null());
    });
    // LOCALLOOP_SPIKE_NO_JOB=1 disables the OS-level containment (negative control).
    if std::env::var_os("LOCALLOOP_SPIKE_NO_JOB").is_none() {
        #[cfg(windows)]
        command.wrap(JobObject);
        #[cfg(unix)]
        command.wrap(ProcessGroup::leader());
        command.wrap(KillOnDrop);
    }
    let mut child = match command.spawn() {
        Ok(child) => child,
        Err(error) => {
            say(&format!("ERROR=spawn failed: {error}"));
            return ExitCode::from(4);
        }
    };
    let (Some(mut stdin), Some(mut stdout)) = (child.stdin().take(), child.stdout().take()) else {
        say("ERROR=no pipes");
        return ExitCode::from(4);
    };

    let Ok(Some(hello)) = tokio::time::timeout(Duration::from_secs(10), recv(&mut stdout)).await else {
        say("ERROR=worker did not start");
        return ExitCode::from(4);
    };
    say(&format!("SPAWN_MS={:.2}", spawn_started.elapsed().as_secs_f64() * 1000.0));
    say(&format!("WORKER_PID={}", hello.trim_start_matches("pid ")));
    let health = Instant::now();
    let ok = ask(&mut stdin, &mut stdout, "health", Duration::from_secs(5)).await;
    say(&format!("HEALTH={} ROUNDTRIP_MS={:.3}", ok.unwrap_or_default(), health.elapsed().as_secs_f64() * 1000.0));
    if let Some(reply) = ask(&mut stdin, &mut stdout, "spawn_grandchild", Duration::from_secs(5)).await {
        say(&format!("GRANDCHILD_PID={}", reply.trim_start_matches("grandchild ")));
    }

    match scenario.as_str() {
        "wait" => loop {
            tokio::time::sleep(Duration::from_secs(3600)).await;
        },
        "wait_hung" => {
            // The worker's main thread hangs (as in a stuck parser) while the supervisor idles.
            let _ = send(&mut stdin, "hang").await;
            say("HUNG=1");
            loop {
                tokio::time::sleep(Duration::from_secs(3600)).await;
            }
        }
        "exit" => {
            say("EXITING=1");
            ExitCode::SUCCESS // dropping `child` closes the job / kills the process group
        }
        "timeout" => {
            let sent = Instant::now();
            let reply = ask(&mut stdin, &mut stdout, "hang", Duration::from_millis(500)).await;
            say(&format!("HANG_REPLY={}", reply.is_some()));
            let kill_started = Instant::now();
            let _ = Box::into_pin(child.kill()).await;
            let status = child.wait().await;
            say(&format!(
                "KILLED_AFTER_MS={:.1} KILL_TO_EXIT_MS={:.2} STATUS={}",
                sent.elapsed().as_secs_f64() * 1000.0,
                kill_started.elapsed().as_secs_f64() * 1000.0,
                status.map(|s| s.to_string().replace(' ', "_")).unwrap_or_default()
            ));
            ExitCode::SUCCESS
        }
        "crash" => {
            let reply = ask(&mut stdin, &mut stdout, "crash", Duration::from_secs(5)).await;
            let status = child.wait().await;
            say(&format!(
                "CRASH_REPLY={} CRASH_STATUS={}",
                reply.is_some(),
                status.map(|s| s.to_string().replace(' ', "_")).unwrap_or_default()
            ));
            ExitCode::SUCCESS
        }
        other => {
            say(&format!("ERROR=unknown scenario {other}"));
            ExitCode::from(2)
        }
    }
}
