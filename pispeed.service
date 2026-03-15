[Unit]
Description=PiSpeed Monitor - Run Speedtest
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=pispeed
Group=pispeed
ExecStart=/usr/local/bin/pispeed-run
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pispeed-run
TimeoutStartSec=180

# Security hardening
NoNewPrivileges=yes
PrivateTmp=yes
