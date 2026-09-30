// affinity_fixed.rs — wave-67 gift, hardened. Dependency-free pinning via raw
// extern (no libc crate needed — fleet tools run zero-dep), plus the receipt
// the gift claimed but never produced: kernel-verified affinity + MEASURED
// jitter (their output asserted "<4μs"; nobody measured anything).
//
// Verified live on this Linux host (see audit doc): pin takes effect in
// /proc/self/status Cpus_allowed_list; jitter histogram from a real sleep loop.
use std::time::{Duration, Instant};

extern "C" {
    // pid 0 = calling THREAD (kernel semantics), mask little-endian u64 covers cores 0..63
    fn sched_setaffinity(pid: i32, cpusetsize: usize, mask: *const u64) -> i32;
}

pub fn pin_current_thread_to_core(core_id: usize) -> Result<(), String> {
    if core_id >= 64 {
        return Err("this zero-dep pin supports cores 0..63 (u64 mask)".into());
    }
    let mask: u64 = 1u64 << core_id;
    let res = unsafe { sched_setaffinity(0, std::mem::size_of::<u64>(), &mask) };
    if res != 0 {
        return Err(format!("sched_setaffinity failed, errno {}", res));
    }
    Ok(())
}

pub fn cpus_allowed_list() -> String {
    std::fs::read_to_string("/proc/self/status")
        .ok()
        .and_then(|s| s.lines().find(|l| l.starts_with("Cpus_allowed_list")).map(|l| l.trim().to_string()))
        .unwrap_or_else(|| "unreadable".into())
}

/// the gift's 60Hz loop — but with its cadence MEASURED, not asserted
pub fn measured_cadence(iters: u32) -> Result<(f64, f64, f64), String> {
    let mut deltas = Vec::with_capacity(iters as usize);
    let mut last = Instant::now();
    for _ in 0..iters {
        std::thread::sleep(Duration::from_nanos(16_666_666));
        let now = Instant::now();
        deltas.push(now.duration_since(last).as_micros() as f64);
        last = now;
    }
    let mean = deltas.iter().sum::<f64>() / deltas.len() as f64;
    let var = deltas.iter().map(|d| (d - mean) * (d - mean)).sum::<f64>() / deltas.len() as f64;
    let max = deltas.iter().cloned().fold(f64::MIN, f64::max);
    Ok((mean, var.sqrt(), max))
}

fn main() {
    println!("[affinity-fixed] Cpus_allowed_list BEFORE pin: {}", cpus_allowed_list());
    match pin_current_thread_to_core(0) {
        Ok(()) => println!("[affinity-fixed] pinned -> Cpus_allowed_list AFTER: {}", cpus_allowed_list()),
        Err(e) => println!("[affinity-fixed] pin refused by kernel: {} (receipt, not fiction)", e),
    }
    match measured_cadence(120) {
        Ok((mean, std, max)) => println!(
            "[affinity-fixed] 60Hz sleep-loop cadence over 120 iters: mean {:.0}μs, stdev {:.0}μs, max {:.0}μs — compare gift's unmeasured '<4μs' claim",
            mean, std, max
        ),
        Err(e) => println!("[affinity-fixed] cadence measurement failed: {}", e),
    }
}
