//! Visual Software defaults. Keep upstream application identifiers and data paths
//! so upgrading the existing fork retains device IDs and user configuration.
use hbb_common::config;
use std::sync::Once;

// Generated before compilation by tools/visual-software/configure_server.py.
// Missing configuration intentionally prevents building a client for the wrong server.
include!("visual_software_server.rs");

pub fn init() {
    static INIT: Once = Once::new();
    INIT.call_once(|| {
        let mut defaults = config::DEFAULT_SETTINGS.write().unwrap();
        for (key, value) in SERVER_DEFAULTS {
            if !value.is_empty() {
                defaults.insert((*key).to_owned(), (*value).to_owned());
            }
        }
        // Updates for this branded fork are delivered by Visual Software.
        config::DEFAULT_LOCAL_SETTINGS
            .write()
            .unwrap()
            .insert("enable-check-update".to_owned(), "N".to_owned());
    });
}
