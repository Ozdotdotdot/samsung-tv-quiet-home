// Quiet Slint hello: a desktop-buildable probe for whether a Rust/Slint UI can
// open a window on the AU8000 (Tizen 6.0, ARMv7 softfp). It launches nothing;
// OK only reports the selection. Timing and memory print to stderr and on screen.
use std::time::{Instant, SystemTime, UNIX_EPOCH};

slint::include_modules!();

const ITEMS: [&str; 7] = [
    "YouTube",
    "Netflix",
    "Prime Video",
    "Disney+",
    "Jellyfin",
    "NBC News",
    "Live news channels",
];

fn proc_status(field: &str) -> String {
    std::fs::read_to_string("/proc/self/status")
        .ok()
        .and_then(|s| {
            s.lines()
                .find(|l| l.starts_with(field))
                .map(|l| l[field.len()..].trim().to_string())
        })
        .unwrap_or_else(|| "?".into())
}

fn clock() -> String {
    // Local time needs tz data; UTC keeps the probe dependency-free.
    let secs = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);
    format!("{:02}:{:02} UTC", (secs / 3600) % 24, (secs / 60) % 60)
}

fn set_items(ui: &Hello) {
    let items: Vec<slint::SharedString> = ITEMS.iter().map(|s| (*s).into()).collect();
    ui.set_items(slint::ModelRc::new(slint::VecModel::from(items)));
}

/// Renders one 1920x1080 frame offscreen through the software renderer, with no
/// windowing system, and writes it as a binary PPM.
#[cfg(feature = "snapshot")]
fn snapshot(path: &str) -> Result<(), slint::PlatformError> {
    use slint::platform::software_renderer::{MinimalSoftwareWindow, RepaintBufferType};
    use slint::Rgb8Pixel;
    use std::rc::Rc;
    struct Headless(Rc<MinimalSoftwareWindow>);
    impl slint::platform::Platform for Headless {
        fn create_window_adapter(
            &self,
        ) -> Result<Rc<dyn slint::platform::WindowAdapter>, slint::PlatformError> {
            Ok(self.0.clone())
        }
    }
    let (w, h) = (1920usize, 1080usize);
    let window = MinimalSoftwareWindow::new(RepaintBufferType::NewBuffer);
    slint::platform::set_platform(Box::new(Headless(window.clone())))
        .map_err(|e| slint::PlatformError::Other(e.to_string()))?;
    let ui = Hello::new()?;
    set_items(&ui);
    ui.set_selected(1);
    ui.set_clock(clock().into());
    ui.set_stats("offscreen snapshot · software renderer".into());
    window.set_size(slint::PhysicalSize::new(w as u32, h as u32));
    ui.show()?;
    slint::platform::update_timers_and_animations();
    let mut buf = vec![Rgb8Pixel::default(); w * h];
    let t = Instant::now();
    window.draw_if_needed(|r| {
        r.render(&mut buf, w);
    });
    eprintln!("[hello] snapshot frame rendered in {} ms", t.elapsed().as_millis());
    let mut out = format!("P6 {w} {h} 255\n").into_bytes();
    out.extend(buf.iter().flat_map(|p| [p.r, p.g, p.b]));
    std::fs::write(path, out).map_err(|e| slint::PlatformError::Other(e.to_string()))
}

fn main() -> Result<(), slint::PlatformError> {
    #[cfg(feature = "snapshot")]
    if let Some(path) = std::env::args().skip_while(|a| a != "--snapshot").nth(1) {
        return snapshot(&path);
    }
    let start = Instant::now();
    eprintln!("[hello] start pid={}", std::process::id());
    eprintln!(
        "[hello] WAYLAND_DISPLAY={:?} XDG_RUNTIME_DIR={:?}",
        std::env::var("WAYLAND_DISPLAY").ok(),
        std::env::var("XDG_RUNTIME_DIR").ok()
    );

    let ui = Hello::new()?;
    eprintln!("[hello] window created in {} ms", start.elapsed().as_millis());
    set_items(&ui);
    ui.set_clock(clock().into());

    let weak = ui.as_weak();
    ui.on_activate(move |i| {
        eprintln!("[hello] OK on {}", ITEMS[i as usize]);
        if let Some(ui) = weak.upgrade() {
            ui.set_stats(format!("Selected {} (this probe launches nothing)", ITEMS[i as usize]).into());
        }
    });
    ui.on_quit(|| {
        let _ = slint::quit_event_loop();
    });

    // First tick of the running event loop: a close proxy for "on screen".
    let weak = ui.as_weak();
    slint::Timer::single_shot(std::time::Duration::ZERO, move || {
        let ms = start.elapsed().as_millis();
        eprintln!("[hello] event loop running at {} ms, VmRSS {}", ms, proc_status("VmRSS:"));
        if let Some(ui) = weak.upgrade() {
            ui.set_stats(format!("event loop at {ms} ms").into());
        }
    });

    let weak = ui.as_weak();
    let stats_timer = slint::Timer::default();
    stats_timer.start(slint::TimerMode::Repeated, std::time::Duration::from_secs(2), move || {
        let line = format!(
            "up {} s · RSS {} · peak {} · threads {}",
            start.elapsed().as_secs(),
            proc_status("VmRSS:"),
            proc_status("VmHWM:"),
            proc_status("Threads:")
        );
        eprintln!("[hello] {line}");
        if let Some(ui) = weak.upgrade() {
            ui.set_stats(line.into());
            ui.set_clock(clock().into());
        }
    });

    ui.run()
}
