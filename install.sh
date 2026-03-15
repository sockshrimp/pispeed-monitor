[Unit]
Description=PiSpeed Monitor Web Server
After=network.target
Documentation=https://github.com/your-username/pispeed-monitor

[Service]
Type=simple
User=pispeed
Group=pispeed
ExecStart=/usr/bin/python3 /usr/local/bin/pispeed-server
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pispeed

# Security hardening
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
