#!/bin/bash
# PiSpeed Monitor — Uninstaller

set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run as root: sudo bash uninstall.sh${NC}"
    exit 1
fi

echo -e "${YELLOW}${BOLD}PiSpeed Monitor — Uninstaller${NC}"
echo ""
echo "This will remove PiSpeed Monitor from your Raspberry Pi."
read -p "Do you want to keep your speedtest data/logs? [Y/n]: " KEEP_DATA

echo ""
echo -e "${CYAN}Stopping and disabling services...${NC}"
systemctl stop pispeed.service 2>/dev/null || true
systemctl stop pispeed-timer.timer 2>/dev/null || true
systemctl disable pispeed.service 2>/dev/null || true
systemctl disable pispeed-timer.timer 2>/dev/null || true

echo -e "${CYAN}Removing files...${NC}"
rm -f /etc/systemd/system/pispeed.service
rm -f /etc/systemd/system/pispeed-timer.timer
rm -f /etc/systemd/system/pispeed-run.service
rm -f /usr/local/bin/pispeed-server
rm -f /usr/local/bin/pispeed-run
rm -rf /usr/share/pispeed
rm -rf /etc/pispeed

if [[ "$KEEP_DATA" =~ ^[Nn]$ ]]; then
    rm -rf /var/lib/pispeed
    echo -e "${CYAN}Data removed.${NC}"
else
    echo -e "${GREEN}Data kept at /var/lib/pispeed${NC}"
fi

systemctl daemon-reload

# Remove user if it exists
userdel pispeed 2>/dev/null || true

echo ""
echo -e "${GREEN}${BOLD}✅ PiSpeed Monitor has been uninstalled.${NC}"
