use std::fmt;
use tracing_subscriber::fmt::format::Writer;
use tracing_subscriber::fmt::time::FormatTime;

// Custom monotonic timestamp using Clock::now()
pub struct MonotonicClockTime {
    start: std::time::Instant,
}

impl MonotonicClockTime {
    pub fn new() -> Self {
        Self {
            start: std::time::Instant::now(),
        }
    }
}

impl FormatTime for MonotonicClockTime {
    fn format_time(&self, w: &mut Writer<'_>) -> fmt::Result {
        let elapsed = std::time::Instant::now() - self.start;
        write!(w, "{}", elapsed.as_micros())
    }
}
