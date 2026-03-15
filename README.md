# PiSpeed Monitor

Internet speed monitoring for Raspberry Pi with Pi-hole. A modern replacement for the pihole-speedtest mod, fully compatible with Pi-hole v6.

## Features
- 📊 Live dashboard with interactive graphs
- 📡 Automatic scheduled speedtests (configurable interval)
- ▶ Manual "Run Now" button in the UI
- 📈 Download, upload & ping over time with hover tooltips
- 🎯 ISP plan speed reference line on graph
- ⚠ Threshold alerts — visually flags results below your paid speed
- 🚨 Violations page — ISP accountability log with exportable evidence
- 📴 Outage detection — flags periods of no connectivity
- 💾 Export data as CSV or JSON
- ⚙ All settings configurable from the web UI
- 🔧 systemd timer for reliable scheduling
- 🆓 Supports both speedtest-cli (Ookla) and librespeed-cli

## Requirements
- Raspberry Pi running Raspberry Pi OS (Bullseye or Bookworm)
- Pi-hole installed (optional — PiSpeed is completely independent)
- Internet connection

## Quick Install
```bash
git clone https://github.com/your-username/pispeed-monitor.git
cd pispeed-monitor
sudo bash install.sh
```
Then open your browser at `http://<your-pi-ip>:8080`

## Manual Commands
```bash
# Run a speedtest right now
sudo pispeed-run

# Check service status
sudo systemctl status pispeed

# Watch live logs
sudo journalctl -u pispeed -f

# Watch speedtest logs
sudo journalctl -u pispeed-run -f

# Restart the web server
sudo systemctl restart pispeed

# Check timer schedule
sudo systemctl list-timers pispeed-timer.timer
```

## Configuration
All settings can be changed from the web UI → Settings page. Configuration is saved to `/etc/pispeed/config.json`.

| Setting | Default | Description |
|---|---|---|
| ISP Download | 100 Mbps | Your plan's download speed |
| ISP Upload | 20 Mbps | Your plan's upload speed |
| Threshold | 80% | Alert when speed drops below this % of plan |
| Interval | 60 min | How often to auto-run tests |
| Backend | auto | speedtest-cli or librespeed-cli |
| Port | 8080 | Web UI port |

## Data Storage
- Results: `/var/lib/pispeed/results.json`
- Config: `/etc/pispeed/config.json`
- Logs: `journalctl -u pispeed`

## Uninstall
```bash
sudo bash uninstall.sh
```

## Disclaimer
I have no idea what im doing. This is a Claude vibe code project.
