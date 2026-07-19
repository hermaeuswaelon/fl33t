# Warp Channel Config Stub — OSS Workaround

## Problem
`warp-tui-oss` binary panics at startup:
```
thread 'main' panicked at crates/warp_channel_config/src/lib.rs:83:17:
'warp-channel-config' was not found on PATH.
To build internal channels, run:
  ./script/install_channel_config
```

The `install_channel_config` script requires SSH access to `ssh://git@github.com/warpdotdev/warp-channel-config.git` — an internal Warp repo that OSS contributors (and most users) cannot access.

## Solution
Compile a tiny Rust stub that outputs valid OSS ChannelConfig JSON. The TUI only needs `warp-channel-config` on PATH; it does **not** validate that the binary is the original one.

### Build the Stub
```rust
use std::io::Read;

fn main() {
    let mut args = std::env::args().skip(1);
    let mut channel = String::new();
    let mut target_family = String::new();
    let mut target_os = String::new();

    while let Some(arg) = args.next() {
        match arg.as_str() {
            "--channel" => channel = args.next().unwrap_or_default(),
            "--target-family" => target_family = args.next().unwrap_or_default(),
            "--target-os" => target_os = args.next().unwrap_or_default(),
            _ => {}
        }
    }

    let config = r#"{"app_id":"dev.warp.WarpOss","logfile_name":"","server_config":{"server_root_url":"https://app.warp.dev","rtc_server_url":"wss://rtc.app.warp.dev/graphql/v2","session_sharing_server_url":"wss://sessions.app.warp.dev","firebase_auth_api_key":"","iap_config":null},"oz_config":{"oz_root_url":"https://oz.warp.dev","workload_audience_url":null},"telemetry_config":null,"autoupdate_config":null,"crash_reporting_config":null,"mcp_static_config":null}"#;

    println!("{}", config);
}
```

### Install
```bash
rustc /path/to/stub.rs -o ~/.local/bin/warp-channel-config
```

The binary takes `--channel`, `--target-family`, `--target-os` args (parsed but ignored — OSS config is static).

## How the config maps to ChannelState::init()
The JSON matches the hardcoded OSS defaults in `crates/warp_core/src/channel/state.rs`:
```
Channel::Oss → AppId::new("dev", "warp", "WarpOss")
                logfile_name: ""
                server_config: WarpServerConfig::production()
                oz_config: OzConfig::production()
                telemetry_config: None
                crash_reporting_config: None
                autoupdate_config: None
                mcp_static_config: None
```

## Pitfalls
- The stub must be **on PATH BEFORE** launching `warp-tui-oss`
- Works for OSS channel only (`warp-tui-oss`). Dev/preview/stable channels may expect different config fields
- If the channel config struct changes in a future build, update the JSON accordingly
- **Do NOT** commit the stub to the warp repo — it's a local dev workaround, not a patch for upstream
