#!/bin/bash
# PiSpeed Monitor - Speedtest Runner
# Runs a speedtest and logs results to JSON database

LOG_FILE="/var/lib/pispeed/results.json"
OUTAGE_LOG="/var/lib/pispeed/outages.json"
CONFIG_FILE="/etc/pispeed/config.json"
LOCK_FILE="/tmp/pispeed_running.lock"

# Prevent concurrent runs
if [ -f "$LOCK_FILE" ]; then
    echo "Speedtest already running, exiting."
    exit 1
fi
touch "$LOCK_FILE"

cleanup() {
    rm -f "$LOCK_FILE"
}
trap cleanup EXIT

# Load config
BACKEND="auto"
if [ -f "$CONFIG_FILE" ]; then
    BACKEND=$(python3 -c "import json; d=json.load(open('$CONFIG_FILE')); print(d.get('backend','auto'))" 2>/dev/null || echo "auto")
fi

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EPOCH=$(date +%s)

# Check connectivity first
if ! ping -c 1 -W 3 8.8.8.8 > /dev/null 2>&1; then
    # Log outage
    OUTAGE_ENTRY="{\"timestamp\":\"$TIMESTAMP\",\"epoch\":$EPOCH,\"type\":\"outage\",\"download\":0,\"upload\":0,\"ping\":0,\"server\":\"N/A\",\"isp\":\"N/A\",\"error\":\"No connectivity\"}"
    
    if [ ! -f "$LOG_FILE" ]; then
        echo "[$OUTAGE_ENTRY]" > "$LOG_FILE"
    else
        python3 -c "
import json, sys
entry = $OUTAGE_ENTRY
with open('$LOG_FILE', 'r') as f:
    data = json.load(f)
data.append(entry)
with open('$LOG_FILE', 'w') as f:
    json.dump(data, f)
"
    fi
    echo "OUTAGE logged at $TIMESTAMP"
    exit 0
fi

# Determine which backend to use
USE_BACKEND=""
if [ "$BACKEND" = "speedtest-cli" ] || [ "$BACKEND" = "auto" ]; then
    if command -v speedtest-cli &> /dev/null; then
        USE_BACKEND="speedtest-cli"
    fi
fi
if [ -z "$USE_BACKEND" ] && { [ "$BACKEND" = "librespeed-cli" ] || [ "$BACKEND" = "auto" ]; }; then
    if command -v librespeed-cli &> /dev/null; then
        USE_BACKEND="librespeed-cli"
    fi
fi

if [ -z "$USE_BACKEND" ]; then
    echo "ERROR: No speedtest backend found. Please run the installer."
    exit 1
fi

# Run the speedtest
DOWNLOAD=0
UPLOAD=0
PING=0
SERVER="Unknown"
ISP="Unknown"
ERROR=""

if [ "$USE_BACKEND" = "speedtest-cli" ]; then
    RESULT=$(speedtest-cli --json 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$RESULT" ]; then
        DOWNLOAD=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(round(d['download']/1_000_000,2))")
        UPLOAD=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(round(d['upload']/1_000_000,2))")
        PING=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(round(d['ping'],2))")
        SERVER=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['server']['name']+', '+d['server']['country'])" 2>/dev/null || echo "Unknown")
        ISP=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('client',{}).get('isp','Unknown'))" 2>/dev/null || echo "Unknown")
    else
        ERROR="speedtest-cli failed"
    fi

elif [ "$USE_BACKEND" = "librespeed-cli" ]; then
    RESULT=$(librespeed-cli --json 2>/dev/null)
    if [ $? -eq 0 ] && [ -n "$RESULT" ]; then
        DOWNLOAD=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(round(float(d[0]['download']),2))" 2>/dev/null || echo "0")
        UPLOAD=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(round(float(d[0]['upload']),2))" 2>/dev/null || echo "0")
        PING=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(round(float(d[0]['ping']),2))" 2>/dev/null || echo "0")
        SERVER=$(echo "$RESULT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0].get('server','Unknown'))" 2>/dev/null || echo "Unknown")
        ISP="Unknown"
    else
        ERROR="librespeed-cli failed"
    fi
fi

# Build JSON entry
ENTRY="{\"timestamp\":\"$TIMESTAMP\",\"epoch\":$EPOCH,\"type\":\"result\",\"download\":$DOWNLOAD,\"upload\":$UPLOAD,\"ping\":$PING,\"server\":\"$SERVER\",\"isp\":\"$ISP\",\"backend\":\"$USE_BACKEND\",\"error\":\"$ERROR\"}"

# Append to log file
if [ ! -f "$LOG_FILE" ]; then
    echo "[$ENTRY]" > "$LOG_FILE"
else
    python3 -c "
import json
entry = $ENTRY
with open('$LOG_FILE', 'r') as f:
    data = json.load(f)
data.append(entry)
# Keep last 10000 entries
if len(data) > 10000:
    data = data[-10000:]
with open('$LOG_FILE', 'w') as f:
    json.dump(data, f)
"
fi

echo "Speedtest complete: Down=${DOWNLOAD}Mbps Up=${UPLOAD}Mbps Ping=${PING}ms"
