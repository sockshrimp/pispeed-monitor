#!/bin/bash
# ============================================================
#  PiSpeed Monitor — Installer
#  Compatible with Raspberry Pi OS (Bullseye / Bookworm)
# ============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

INSTALL_DIR="/usr/share/pispeed"
BIN_DIR="/usr/local/bin"
CONFIG_DIR="/etc/pispeed"
DATA_DIR="/var/lib/pispeed"
SYSTEMD_DIR="/etc/systemd/system"
SERVICE_USER="pispeed"

print_banner() {
    echo ""
    echo -e "${CYAN}${BOLD}"
    echo "  ____  _ ____                      _ "
    echo " |  _ \(_) ___| _ __   ___  ___  __| |"
    echo " | |_) | \___ \| '_ \ / _ \/ _ \/ _\` |"
    echo " |  __/| |___) | |_) |  __/  __/ (_| |"
    echo " |_|   |_|____/| .__/ \___|\___|\__,_|"
    echo "                |_|   Monitor v1.0"
    echo -e "${NC}"
    echo -e " Internet Speed Monitor for Raspberry Pi"
    echo -e " Pi-hole friendly · Built with ❤ for Pi users"
    echo ""
}

log()    { echo -e "${GREEN}[✓]${NC} $1"; }
warn()   { echo -e "${YELLOW}[!]${NC} $1"; }
error()  { echo -e "${RED}[✗] ERROR: $1${NC}"; exit 1; }
info()   { echo -e "${CYAN}[→]${NC} $1"; }
header() { echo -e "\n${BOLD}${CYAN}── $1 ──${NC}"; }

# ─── Root check ──────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    error "Please run as root: sudo bash install.sh"
fi

print_banner

# ─── Detect OS ───────────────────────────────────────────────
header "Checking system"
if [ ! -f /etc/os-release ]; then
    error "Cannot detect OS. Is this a Raspberry Pi?"
fi
source /etc/os-release
info "Detected: $PRETTY_NAME"

if ! command -v python3 &> /dev/null; then
    error "Python 3 not found. Please install: sudo apt install python3"
fi
PY_VER=$(python3 --version 2>&1)
log "Python: $PY_VER"

# ─── Ask for configuration ───────────────────────────────────
header "Configuration"

# Port
DEFAULT_PORT=8080
echo -e "\n${BOLD}What port should the web UI run on?${NC}"
echo -e "  (Pi-hole uses 80/443. Port 8080 is safe and recommended.)"
read -p "  Port [default: 8080]: " INPUT_PORT
PORT=${INPUT_PORT:-$DEFAULT_PORT}

# ISP speeds
echo -e "\n${BOLD}What download speed does your ISP plan include? (Mbps)${NC}"
echo -e "  (e.g. if you pay for 100 Mbps, enter 100)"
read -p "  ISP Download [default: 100]: " INPUT_DOWN
ISP_DOWN=${INPUT_DOWN:-100}

echo -e "\n${BOLD}What upload speed does your ISP plan include? (Mbps)${NC}"
read -p "  ISP Upload [default: 20]: " INPUT_UP
ISP_UP=${INPUT_UP:-20}

# Alert threshold
echo -e "\n${BOLD}Alert threshold: flag results below what % of your plan speed?${NC}"
echo -e "  (e.g. 80 means flag anything below 80 Mbps on a 100 Mbps plan)"
read -p "  Threshold % [default: 80]: " INPUT_THRESH
THRESHOLD=${INPUT_THRESH:-80}

# Test interval
echo -e "\n${BOLD}How often should automatic speedtests run? (minutes)${NC}"
echo -e "  (Recommended: 60. Minimum: 5)"
read -p "  Interval in minutes [default: 60]: " INPUT_INTERVAL
INTERVAL=${INPUT_INTERVAL:-60}
if [ "$INTERVAL" -lt 5 ]; then
    warn "Minimum interval is 5 minutes. Setting to 5."
    INTERVAL=5
fi

# Speedtest backend
echo -e "\n${BOLD}Which speedtest backend would you like?${NC}"
echo "  1) Auto-detect (try both, use what's available) [recommended]"
echo "  2) speedtest-cli (Ookla official)"
echo "  3) librespeed-cli (open source, no account needed)"
read -p "  Choice [default: 1]: " INPUT_BACKEND
case $INPUT_BACKEND in
    2) BACKEND="speedtest-cli" ;;
    3) BACKEND="librespeed-cli" ;;
    *) BACKEND="auto" ;;
esac

echo ""
echo -e "${BOLD}Summary:${NC}"
echo -e "  Web UI port:      ${CYAN}$PORT${NC}"
echo -e "  ISP Download:     ${CYAN}${ISP_DOWN} Mbps${NC}"
echo -e "  ISP Upload:       ${CYAN}${ISP_UP} Mbps${NC}"
echo -e "  Alert threshold:  ${CYAN}${THRESHOLD}%${NC}"
echo -e "  Test interval:    ${CYAN}every ${INTERVAL} minutes${NC}"
echo -e "  Backend:          ${CYAN}${BACKEND}${NC}"
echo ""
read -p "Proceed with installation? [Y/n]: " CONFIRM
if [[ "$CONFIRM" =~ ^[Nn]$ ]]; then
    echo "Installation cancelled."
    exit 0
fi

# ─── Install dependencies ────────────────────────────────────
header "Installing dependencies"
info "Updating package lists..."
apt-get update -qq

info "Installing required packages..."
apt-get install -y -qq curl wget python3 python3-pip bc net-tools

# ─── Install speedtest backends ──────────────────────────────
header "Installing speedtest backend(s)"

install_speedtest_cli() {
    if command -v speedtest-cli &> /dev/null; then
        log "speedtest-cli already installed"
        return 0
    fi
    info "Installing speedtest-cli..."
    pip3 install speedtest-cli --break-system-packages 2>/dev/null || pip3 install speedtest-cli 2>/dev/null || {
        warn "pip3 install failed, trying apt..."
        apt-get install -y -qq speedtest-cli || warn "speedtest-cli install failed"
    }
    if command -v speedtest-cli &> /dev/null; then
        log "speedtest-cli installed successfully"
        return 0
    fi
    return 1
}

install_librespeed() {
    if command -v librespeed-cli &> /dev/null; then
        log "librespeed-cli already installed"
        return 0
    fi
    info "Installing librespeed-cli..."
    ARCH=$(uname -m)
    case $ARCH in
        armv7*|armv6*)  LSP_ARCH="armv7" ;;
        aarch64|arm64)  LSP_ARCH="arm64" ;;
        x86_64)         LSP_ARCH="amd64" ;;
        *)              warn "Unknown arch $ARCH, skipping librespeed"; return 1 ;;
    esac

    LSP_URL="https://github.com/librespeed/speedtest-cli/releases/latest/download/librespeed-cli_linux_${LSP_ARCH}.tar.gz"
    TMP_DIR=$(mktemp -d)
    if wget -q "$LSP_URL" -O "$TMP_DIR/librespeed.tar.gz"; then
        tar -xzf "$TMP_DIR/librespeed.tar.gz" -C "$TMP_DIR"
        mv "$TMP_DIR/librespeed-cli" /usr/local/bin/librespeed-cli
        chmod +x /usr/local/bin/librespeed-cli
        rm -rf "$TMP_DIR"
        log "librespeed-cli installed successfully"
        return 0
    else
        warn "Failed to download librespeed-cli"
        rm -rf "$TMP_DIR"
        return 1
    fi
}

INSTALLED_BACKENDS=()
case $BACKEND in
    "speedtest-cli")
        install_speedtest_cli && INSTALLED_BACKENDS+=("speedtest-cli")
        ;;
    "librespeed-cli")
        install_librespeed && INSTALLED_BACKENDS+=("librespeed-cli")
        ;;
    "auto")
        install_speedtest_cli && INSTALLED_BACKENDS+=("speedtest-cli")
        install_librespeed && INSTALLED_BACKENDS+=("librespeed-cli")
        ;;
esac

if [ ${#INSTALLED_BACKENDS[@]} -eq 0 ]; then
    error "No speedtest backend could be installed. Please install speedtest-cli manually and retry."
fi

# ─── Create system user ──────────────────────────────────────
header "Setting up system user"
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd --system --no-create-home --shell /bin/false "$SERVICE_USER"
    log "Created system user: $SERVICE_USER"
else
    log "User $SERVICE_USER already exists"
fi

# ─── Create directories ───────────────────────────────────────
header "Creating directories"
mkdir -p "$INSTALL_DIR/web/static" "$CONFIG_DIR" "$DATA_DIR"
log "Created $INSTALL_DIR"
log "Created $CONFIG_DIR"
log "Created $DATA_DIR"

# ─── Write config ────────────────────────────────────────────
header "Writing configuration"
cat > "$CONFIG_DIR/config.json" << EOF
{
  "port": $PORT,
  "interval_minutes": $INTERVAL,
  "backend": "$BACKEND",
  "isp_download": $ISP_DOWN,
  "isp_upload": $ISP_UP,
  "threshold_percent": $THRESHOLD,
  "display_name": "PiSpeed Monitor"
}
EOF
log "Config written to $CONFIG_DIR/config.json"

# ─── Install files ────────────────────────────────────────────
header "Installing application files"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Copy web files
cp -r "$SCRIPT_DIR/web/"* "$INSTALL_DIR/web/"
log "Web files installed to $INSTALL_DIR/web/"

# Install Python server
cp "$SCRIPT_DIR/scripts/pispeed_server.py" "$BIN_DIR/pispeed-server"
chmod +x "$BIN_DIR/pispeed-server"
log "Server script installed to $BIN_DIR/pispeed-server"

# Install speedtest runner
cp "$SCRIPT_DIR/scripts/run_speedtest.sh" "$BIN_DIR/pispeed-run"
chmod +x "$BIN_DIR/pispeed-run"
log "Runner script installed to $BIN_DIR/pispeed-run"

# Fix permissions
chown -R "$SERVICE_USER:$SERVICE_USER" "$DATA_DIR" "$CONFIG_DIR"
chown -R root:"$SERVICE_USER" "$INSTALL_DIR"
chmod -R 750 "$INSTALL_DIR"
chmod 770 "$DATA_DIR"
chown root:"$SERVICE_USER" "$BIN_DIR/pispeed-run"
chmod 750 "$BIN_DIR/pispeed-run"

log "Permissions set"

# ─── Update systemd timer interval ───────────────────────────
header "Installing systemd services"

# Generate timer with correct interval
cat > "$SYSTEMD_DIR/pispeed-timer.timer" << EOF
[Unit]
Description=PiSpeed Monitor - Scheduled Speedtest Timer

[Timer]
OnBootSec=2min
OnUnitActiveSec=${INTERVAL}min
RandomizedDelaySec=30
Unit=pispeed-run.service

[Install]
WantedBy=timers.target
EOF

cp "$SCRIPT_DIR/systemd/pispeed.service" "$SYSTEMD_DIR/pispeed.service"
cp "$SCRIPT_DIR/systemd/pispeed-run.service" "$SYSTEMD_DIR/pispeed-run.service"
log "Systemd unit files installed"

systemctl daemon-reload

systemctl enable pispeed.service
systemctl enable pispeed-timer.timer
systemctl start pispeed.service
systemctl start pispeed-timer.timer

log "Services enabled and started"

# ─── Detect Pi IP ────────────────────────────────────────────
PI_IP=$(hostname -I | awk '{print $1}')

# ─── Done! ───────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}════════════════════════════════════════════${NC}"
echo -e "${GREEN}${BOLD}  ✅  PiSpeed Monitor installed successfully!${NC}"
echo -e "${GREEN}${BOLD}════════════════════════════════════════════${NC}"
echo ""
echo -e "  📡  Open your browser and go to:"
echo -e "      ${CYAN}${BOLD}http://${PI_IP}:${PORT}${NC}"
echo ""
echo -e "  ⏱   Speedtests will run automatically every ${BOLD}${INTERVAL} minutes${NC}"
echo -e "  📊  First scheduled test will run in ~2 minutes"
echo ""
echo -e "  ${YELLOW}Useful commands:${NC}"
echo -e "    Run a test now:     ${CYAN}sudo pispeed-run${NC}"
echo -e "    View logs:          ${CYAN}sudo journalctl -u pispeed -f${NC}"
echo -e "    Service status:     ${CYAN}sudo systemctl status pispeed${NC}"
echo -e "    Restart service:    ${CYAN}sudo systemctl restart pispeed${NC}"
echo -e "    Uninstall:          ${CYAN}sudo bash uninstall.sh${NC}"
echo ""
