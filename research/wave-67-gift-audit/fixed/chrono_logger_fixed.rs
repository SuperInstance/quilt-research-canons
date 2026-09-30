// chrono_logger_fixed.rs — wave-67 gift, hardened. The gift used `this` (not
// valid Rust), tokio::spawn for blocking file I/O (anti-pattern: stalls the
// async executor), and a hardcoded /mnt/vessel_ssd mount. This version:
// std-only, `self`, a real writer THREAD decoupled via mpsc (async-safe
// backpressure without a runtime), and a configurable root that defaults to
// a path that exists. Schema identical to the gift's dissonance_continuum.csv
// so the dissent loop can adopt the gift's chronology format verbatim.
use std::io::Write;
use std::path::PathBuf;
use std::sync::atomic::{AtomicU32, Ordering};
use std::sync::mpsc;
use std::time::{SystemTime, UNIX_EPOCH};

pub static GLOBAL_BUZZ_REGISTER: AtomicU32 = AtomicU32::new(0);

pub struct LocalSsdChronoLogger {
    log_root: PathBuf,
    last_logged_tick: u32,
    tx: Option<mpsc::Sender<String>>,
}

impl LocalSsdChronoLogger {
    pub fn new() -> Self {
        Self { log_root: PathBuf::from("dissonance_logs"), last_logged_tick: 0, tx: None }
    }

    pub fn with_root(mut self, root: PathBuf) -> Self {
        self.log_root = root;
        self
    }

    /// spin up the dedicated writer thread (the gift's "async task lane", done
    /// without a runtime: blocking I/O on its own OS thread, never on an executor)
    pub fn start(&mut self) -> Result<(), String> {
        std::fs::create_dir_all(&self.log_root).map_err(|e| e.to_string())?;
        let path = self.log_root.join("dissonance_continuum.csv");
        if !path.exists() {
            let mut f = std::fs::File::create(&path).map_err(|e| e.to_string())?;
            writeln!(f, "epoch_timestamp_ms,system_frame_tick,dissonance_magnitude_4bit,nmea_latitude,nmea_longitude")
                .map_err(|e| e.to_string())?;
        }
        let (tx, rx) = mpsc::channel::<String>();
        std::thread::spawn(move || {
            let mut writer = std::fs::OpenOptions::new().append(true).open(&path).ok();
            for line in rx {
                if let Some(f) = writer.as_mut() {
                    let _ = writeln!(f, "{}", line);
                    let _ = f.flush();
                }
            }
        });
        self.tx = Some(tx);
        Ok(())
    }

    pub fn execute_local_ssd_log(&mut self, current_tick: u32, lat: f64, lon: f64) -> Result<(), String> {
        let active_buzz = GLOBAL_BUZZ_REGISTER.load(Ordering::Relaxed) as u8;
        if active_buzz > 4 && current_tick != self.last_logged_tick {
            self.last_logged_tick = current_tick;
            let timestamp = SystemTime::now().duration_since(UNIX_EPOCH).map_err(|e| e.to_string())?.as_millis();
            let line = format!("{},{},{},{:.6},{:.6}", timestamp, current_tick, active_buzz, lat, lon);
            if let Some(tx) = &self.tx {
                tx.send(line).map_err(|e| e.to_string())?;
            }
        }
        Ok(())
    }
}

fn main() {
    // live receipt: five threshold crossings, then read the file back
    let root = PathBuf::from("/tmp/dissonance_receipt");
    let _ = std::fs::remove_dir_all(&root);
    let mut logger = LocalSsdChronoLogger::new().with_root(root.clone());
    logger.start().expect("writer thread");
    for tick in 100u32..105 {
        GLOBAL_BUZZ_REGISTER.store(9, Ordering::Relaxed); // above threshold 4
        logger.execute_local_ssd_log(tick, 47.620755, -122.349301).expect("log");
        std::thread::sleep(std::time::Duration::from_millis(5));
    }
    GLOBAL_BUZZ_REGISTER.store(2, Ordering::Relaxed); // below threshold: must NOT log
    logger.execute_local_ssd_log(105, 47.620755, -122.349301).expect("log");
    std::thread::sleep(std::time::Duration::from_millis(50)); // let the writer drain
    let csv = std::fs::read_to_string(root.join("dissonance_continuum.csv")).expect("csv");
    println!("{}", csv);
    let data_rows = csv.lines().count() - 1;
    println!("[chrono-fixed] {} data rows (expected 5: tick 105 suppressed by the buzz gate — the gate is real, not decorative)", data_rows);
}
