#!/usr/bin/env python3
"""
PiSpeed Monitor - Web Server
Serves the dashboard and provides API endpoints.
"""

import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import csv
import io

CONFIG_FILE = "/etc/pispeed/config.json"
LOG_FILE = "/var/lib/pispeed/results.json"
SPEEDTEST_SCRIPT = "/usr/local/bin/pispeed-run"
WEB_DIR = "/usr/share/pispeed/web"

DEFAULT_CONFIG = {
    "port": 8080,
    "interval_minutes": 60,
    "backend": "auto",
    "isp_download": 100,
    "isp_upload": 20,
    "threshold_percent": 80,
    "display_name": "PiSpeed Monitor"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
            # Merge with defaults for any missing keys
            for k, v in DEFAULT_CONFIG.items():
                if k not in cfg:
                    cfg[k] = v
            return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(cfg, f, indent=2)

def load_results():
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE) as f:
            return json.load(f)
    except Exception:
        return []

def get_violations(results, config):
    threshold_down = config['isp_download'] * (config['threshold_percent'] / 100)
    threshold_up = config['isp_upload'] * (config['threshold_percent'] / 100)
    violations = []
    for r in results:
        if r.get('type') == 'outage':
            violations.append({**r, 'violation_type': 'outage'})
        elif r.get('type') == 'result' and not r.get('error'):
            reasons = []
            if r['download'] < threshold_down:
                reasons.append(f"Download {r['download']} Mbps < threshold {threshold_down:.1f} Mbps")
            if r['upload'] < threshold_up:
                reasons.append(f"Upload {r['upload']} Mbps < threshold {threshold_up:.1f} Mbps")
            if reasons:
                violations.append({**r, 'violation_type': 'below_threshold', 'reasons': reasons})
    return violations

def results_to_csv(results):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        'timestamp','epoch','type','download','upload','ping','server','isp','backend','error'
    ])
    writer.writeheader()
    for r in results:
        row = {k: r.get(k, '') for k in writer.fieldnames}
        writer.writerow(row)
    return output.getvalue()

running_test = False
running_test_lock = threading.Lock()

def trigger_speedtest_async():
    global running_test
    with running_test_lock:
        if running_test:
            return False
        running_test = True

    def run():
        global running_test
        try:
            subprocess.run([SPEEDTEST_SCRIPT], timeout=120)
        except Exception as e:
            print(f"Speedtest error: {e}")
        finally:
            with running_test_lock:
                running_test = False

    t = threading.Thread(target=run, daemon=True)
    t.start()
    return True


class PiSpeedHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass  # Suppress default access log

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path, content_type):
        try:
            with open(path, 'rb') as f:
                body = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        # Serve main dashboard
        if path == '/' or path == '/index.html':
            self.send_file(os.path.join(WEB_DIR, 'index.html'), 'text/html; charset=utf-8')
            return

        # Static assets
        if path.startswith('/static/'):
            fname = path[8:]
            fpath = os.path.join(WEB_DIR, 'static', fname)
            ctype = 'text/css' if fname.endswith('.css') else 'application/javascript'
            self.send_file(fpath, ctype)
            return

        # API endpoints
        if path == '/api/results':
            limit = int(qs.get('limit', [500])[0])
            results = load_results()[-limit:]
            self.send_json(results)

        elif path == '/api/config':
            self.send_json(load_config())

        elif path == '/api/status':
            global running_test
            results = load_results()
            latest = None
            for r in reversed(results):
                if r.get('type') == 'result':
                    latest = r
                    break
            self.send_json({
                'running': running_test,
                'latest': latest,
                'total_tests': len([r for r in results if r.get('type') == 'result']),
                'total_outages': len([r for r in results if r.get('type') == 'outage']),
            })

        elif path == '/api/violations':
            config = load_config()
            results = load_results()
            violations = get_violations(results, config)
            self.send_json(violations)

        elif path == '/api/export':
            fmt = qs.get('format', ['json'])[0]
            results = load_results()
            if fmt == 'csv':
                body = results_to_csv(results).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'text/csv')
                self.send_header('Content-Disposition', 'attachment; filename="pispeed_results.csv"')
                self.send_header('Content-Length', len(body))
                self.end_headers()
                self.wfile.write(body)
            else:
                body = json.dumps(results, indent=2).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Disposition', 'attachment; filename="pispeed_results.json"')
                self.send_header('Content-Length', len(body))
                self.end_headers()
                self.wfile.write(body)

        elif path == '/api/trigger':
            started = trigger_speedtest_async()
            if started:
                self.send_json({'status': 'started', 'message': 'Speedtest triggered'})
            else:
                self.send_json({'status': 'busy', 'message': 'Speedtest already running'}, 409)

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == '/api/config':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                new_cfg = json.loads(body)
                cfg = load_config()
                # Only allow known keys
                allowed = set(DEFAULT_CONFIG.keys())
                for k, v in new_cfg.items():
                    if k in allowed:
                        cfg[k] = v
                save_config(cfg)
                # Restart systemd timer if interval changed
                if 'interval_minutes' in new_cfg:
                    try:
                        subprocess.run(['systemctl', 'daemon-reload'], check=False)
                        subprocess.run(['systemctl', 'restart', 'pispeed-timer.timer'], check=False)
                    except Exception:
                        pass
                self.send_json({'status': 'ok', 'config': cfg})
            except Exception as e:
                self.send_json({'status': 'error', 'message': str(e)}, 400)

        elif path == '/api/trigger':
            started = trigger_speedtest_async()
            if started:
                self.send_json({'status': 'started', 'message': 'Speedtest triggered'})
            else:
                self.send_json({'status': 'busy', 'message': 'Speedtest already running'}, 409)

        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


def main():
    config = load_config()
    port = config.get('port', 8080)

    server = HTTPServer(('0.0.0.0', port), PiSpeedHandler)
    print(f"PiSpeed Monitor running on http://0.0.0.0:{port}")
    sys.stdout.flush()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == '__main__':
    main()
