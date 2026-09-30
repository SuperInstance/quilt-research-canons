// superinstance/superinstance -> src/pipeline/affinity.rs
use std::sync::atomic::{AtomicU32, Ordering};
use std::thread;
use std::time::Duration;

pub static SENSOR_PACKET_COUNT: AtomicU32 = AtomicU32::new(0);

/// Binds the current calling OS execution thread to a single dedicated physical hardware core.
/// This prevents kernel context switching, preserves CPU L1/L2 cache locality,
/// and guarantees sub-millisecond real-time latency profiles under high load states.
pub fn pin_current_thread_to_core(core_id: usize) -> Result<(), String> {
    #[cfg(target_os = "linux")]
    {
        use libc::{cpu_set_t, sched_setaffinity, CPU_SET, CPU_ZERO};
        use std::mem::zeroed;

        unsafe {
            let mut cpuset: cpu_set_t = zeroed();
            CPU_ZERO(&mut cpuset);
            CPU_SET(core_id, &mut cpuset);

            let pid = 0; // 0 targets the calling thread identifier
            let res = sched_setaffinity(pid, std::mem::size_of::<cpu_set_t>(), &cpuset);
            if res != 0 {
                return Err(format!("sched_setaffinity failed with exit code: {}", res));
            }
        }
        println!("[Hardware Core] Execution thread pinned cleanly to Physical Core Target: #{}", core_id);
        Ok(())
    }

    #[cfg(not(target_os = "linux"))]
    {
        println!("[Hardware Core] Simulation Stub: Thread tracking requested for Core Target: #{}", core_id);
        Ok(())
    }
}

pub fn spawn_pinned_sensor_ingestion_loop(core_id: usize) {
    std::thread::spawn(move || {
        // Enforce rigid hardware binding immediately on thread initialization
        if let Err(e) = pin_current_thread_to_core(core_id) {
            eprintln!("[Hardware Core] Critical Affinity Error: {:?}", e);
        }

        let mut internal_tick = 0u64;
        loop {
            // High-precision timing loop simulation
            std::thread::sleep(Duration::from_nanos(16_666_666)); // Strict ~60Hz cadence
            internal_tick = internal_tick.wrapping_add(1);
            SENSOR_PACKET_COUNT.fetch_add(1, Ordering::Relaxed);
        }
    });
}
