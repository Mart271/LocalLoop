//! SPIKE (LL-011): a stand-in for the document worker.
//!
//! A dedicated thread reads framed requests from stdin and **exits the process as soon as stdin
//! closes**, even while the main thread is busy or hung in a parser. That is how the worker
//! notices that its parent has gone on every OS. Set LOCALLOOP_SPIKE_NO_WATCHDOG=1 to read stdin
//! on the main thread instead (negative control).

#![forbid(unsafe_code)]

use std::io::{self, BufReader, BufWriter};
use std::process::{Command, Stdio};
use std::sync::mpsc;

use spike_child_process::{read_frame, write_frame};

fn handle(request: &str, grandchildren: &mut Vec<std::process::Child>) -> String {
    match request {
        "health" => "ok".to_owned(),
        "hang" => loop {
            std::thread::sleep(std::time::Duration::from_secs(3600));
        },
        "crash" => std::process::abort(),
        "spawn_grandchild" => {
            // A grandchild whose stdin is a pipe owned by this worker. It must also die.
            let executable = match std::env::current_exe() {
                Ok(path) => path,
                Err(error) => return format!("error {error}"),
            };
            match Command::new(executable)
                .stdin(Stdio::piped())
                .stdout(Stdio::null())
                .spawn()
            {
                Ok(child) => {
                    let id = child.id();
                    grandchildren.push(child);
                    format!("grandchild {id}")
                }
                Err(error) => format!("error {error}"),
            }
        }
        other => format!("error unknown request {other:?}"),
    }
}

fn main() {
    let mut output = BufWriter::new(io::stdout().lock());
    let mut grandchildren = Vec::new();
    if write_frame(&mut output, &format!("pid {}", std::process::id())).is_err() {
        return;
    }
    let watchdog = std::env::var_os("LOCALLOOP_SPIKE_NO_WATCHDOG").is_none();
    let (tx, rx) = mpsc::channel::<String>();
    if watchdog {
        std::thread::spawn(move || {
            let mut input = BufReader::new(io::stdin().lock());
            while let Ok(Some(request)) = read_frame(&mut input) {
                if tx.send(request).is_err() {
                    break;
                }
            }
            std::process::exit(0); // parent gone or protocol error: stop now, whatever main is doing
        });
    } else {
        drop(tx);
    }
    // Only take the stdin lock here when no watchdog thread owns it.
    let mut input = if watchdog {
        None
    } else {
        Some(BufReader::new(io::stdin().lock()))
    };
    loop {
        let request = if let Some(input) = input.as_mut() {
            match read_frame(input) {
                Ok(Some(request)) => request,
                Ok(None) | Err(_) => return,
            }
        } else {
            match rx.recv() {
                Ok(request) => request,
                Err(_) => return,
            }
        };
        let reply = handle(&request, &mut grandchildren);
        if write_frame(&mut output, &reply).is_err() {
            return;
        }
    }
}
