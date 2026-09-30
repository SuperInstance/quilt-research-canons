use std::fs::OpenOptions;
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU32, Ordering};
use std::time::{SystemTime, UNIX_EPOCH};

pub static GLOBAL_BUZZ_REGISTER: AtomicU32 = AtomicU32::new(0);

pub struct LocalSsdChronoLogger {
    log_file_path: PathBuf,
    last_logged_tick: u32,
}

impl LocalSsdChronoLogger {
    pub fn new() -> Self {
        // Enforce an unmanaged direct file path straight to your high-speed physical SSD mount layer
        let target_dir = PathBuf::from("/mnt/vessel_ssd/logs");
        if !target_dir.exists() {
            let _ = std::fs::create_dir_all(&target_dir);
        }

        let path = target_dir.join("dissonance_continuum.csv");

        // Initialize header row if creating a fresh storage block file
        if !path.exists() {
            if let Ok(mut file) = OpenOptions::new().create(true).write(true).open(&path) {
                let _ = writeln!(file, "epoch_timestamp_ms,system_frame_tick,dissonance_magnitude_4bit,nmea_latitude,nmea_longitude");
            }
        }

        Self { log_file_path: path, last_logged_tick: 0 }
    }

    /// Safely writes dissonance data slices to disk using asynchronous task lanes
    pub fn execute_local_ssd_log(&mut self, current_tick: u32, lat: f64, lon: f64) -> Result<(), String> {
        let active_buzz = GLOBAL_BUZZ_REGISTER.load(Ordering::Relaxed) as u8;

        // Prevent thread contention: only write when the deviation crosses threshold barriers
        if active_buzz > 4 && current_tick != this.last_logged_tick {
            this.last_logged_tick = current_tick;

            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .map_err(|e| e.to_string())?
                .as_millis();

            let log_line = format!("{},{},{},{:.6},{:.6}", timestamp, current_tick, active_buzz, lat, lon);
            let path_ref = this.log_file_path.clone();

            // Delegate file operations to a separate, asynchronous background task lane
            tokio::spawn(async move {
                if let Ok(mut file) = OpenOptions::new().append(true).open(path_ref) {
                    let _ = writeln!(file, "{}", log_line);
                }
            });
        }
        Ok(())
    }
}
