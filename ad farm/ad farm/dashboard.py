#!/usr/bin/env python3
"""
Web Dashboard — Real-Time Farm Monitor
========================================
Flask-based web dashboard showing live farm statistics.
Accessible at http://localhost:5000 (or configured DASHBOARD_PORT).

Pages:
  /           — Main dashboard with live stats
  /api/stats  — JSON API for live data (auto-refresh every 5s)

Usage:
    python dashboard.py           # Standalone
    # Or started by farm.py       # Integrated
"""

import json
import time
import threading
from pathlib import Path
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

# Global state (populated by farm.py)
farm_state = {
    'running': False,
    'uptime': '0h 0m 0s',
    'total_sessions': 0,
    'successful': 0,
    'failed': 0,
    'success_rate': '0%',
    'total_pages': 0,
    'total_ad_hovers': 0,
    'total_ad_clicks': 0,
    'avg_session_time': '0s',
    'sessions_per_hour': 0,
    'concurrent': 0,
    'proxy_working': 0,
    'proxy_total': 0,
    'estimated_revenue': '$0.00',
    'projected_daily': '$0.00',
    'risk_level': 'safe',
    'throttle': 0,
    'vpn_connected': False,
    'network_count': 1,
    'errors': [],
    'recent_sessions': [],
}

state_lock = threading.Lock()


def update_state(**kwargs):
    """Thread-safe state update from farm.py."""
    with state_lock:
        farm_state.update(kwargs)


MAIN_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LOPINUZE Ad Farm V3 — Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0d1117; color: #c9d1d9; padding: 20px; }
        h1 { color: #58a6ff; font-size: 24px; margin-bottom: 5px; }
        .subtitle { color: #8b949e; font-size: 13px; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 15px; }
        .card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 18px; }
        .card h3 { color: #58a6ff; font-size: 14px; margin-bottom: 12px; text-transform: uppercase; letter-spacing: 1px; }
        .stat { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #21262d; font-size: 14px; }
        .stat-label { color: #8b949e; }
        .stat-value { color: #c9d1d9; font-weight: 600; }
        .stat-value.good { color: #3fb950; }
        .stat-value.warn { color: #d29922; }
        .stat-value.bad { color: #f85149; }
        .risk-safe { color: #3fb950; }
        .risk-caution { color: #d29922; }
        .risk-warning { color: #f0883e; }
        .risk-danger { color: #f85149; }
        .risk-critical { color: #ff0000; font-weight: bold; }
        .progress-bar { background: #21262d; border-radius: 4px; height: 8px; margin-top: 5px; overflow: hidden; }
        .progress-fill { background: #3fb950; height: 100%; transition: width 0.5s; }
        .error-log { max-height: 150px; overflow-y: auto; font-size: 12px; color: #f85149; font-family: monospace; }
        .session-table { width: 100%; font-size: 12px; border-collapse: collapse; }
        .session-table th { text-align: left; color: #8b949e; padding: 4px; }
        .session-table td { padding: 4px; border-top: 1px solid #21262d; }
        .refresh { color: #8b949e; font-size: 11px; text-align: right; }
        .btn { padding: 8px 16px; border: 1px solid #30363d; border-radius: 6px; background: #21262d; color: #c9d1d9; cursor: pointer; margin: 4px; font-size: 13px; }
        .btn:hover { background: #30363d; }
        .btn.green { border-color: #3fb950; color: #3fb950; }
        .btn.red { border-color: #f85149; color: #f85149; }
    </style>
</head>
<body>
    <h1>🚜 LOPINUZE Ad Farm V3</h1>
    <p class="subtitle">80 Workers | GPU-Accelerated | Multi-Network | Self-Healing</p>
    <div class="refresh" id="refresh-status">Auto-refresh: 5s</div>

    <div class="grid">
        <!-- Status Card -->
        <div class="card">
            <h3>📊 Farm Status</h3>
            <div class="stat"><span class="stat-label">Status</span><span class="stat-value good" id="running">Stopped</span></div>
            <div class="stat"><span class="stat-label">Uptime</span><span class="stat-value" id="uptime">0h 0m</span></div>
            <div class="stat"><span class="stat-label">Concurrent</span><span class="stat-value" id="concurrent">0</span></div>
            <div class="stat"><span class="stat-label">Sessions/Hour</span><span class="stat-value" id="sph">0</span></div>
            <div class="stat"><span class="stat-label">Risk Level</span><span class="stat-value risk-safe" id="risk">safe</span></div>
            <div class="stat"><span class="stat-label">VPN</span><span class="stat-value" id="vpn">🔴 Off</span></div>
        </div>

        <!-- Sessions Card -->
        <div class="card">
            <h3>📈 Sessions</h3>
            <div class="stat"><span class="stat-label">Total</span><span class="stat-value" id="total">0</span></div>
            <div class="stat"><span class="stat-label">Successful</span><span class="stat-value good" id="success">0</span></div>
            <div class="stat"><span class="stat-label">Failed</span><span class="stat-value bad" id="failed">0</span></div>
            <div class="stat"><span class="stat-label">Success Rate</span><span class="stat-value" id="rate">0%</span></div>
            <div class="stat"><span class="stat-label">Pages Visited</span><span class="stat-value" id="pages">0</span></div>
            <div class="stat"><span class="stat-label">Avg Time</span><span class="stat-value" id="avgtime">0s</span></div>
        </div>

        <!-- Ad Revenue Card -->
        <div class="card">
            <h3>💰 Revenue</h3>
            <div class="stat"><span class="stat-label">Estimated</span><span class="stat-value good" id="revenue">$0.00</span></div>
            <div class="stat"><span class="stat-label">Projected/Day</span><span class="stat-value" id="projected">$0.00</span></div>
            <div class="stat"><span class="stat-label">Ad Hovers</span><span class="stat-value" id="hovers">0</span></div>
            <div class="stat"><span class="stat-label">Ad Clicks</span><span class="stat-value good" id="clicks">0</span></div>
            <div class="stat"><span class="stat-label">Networks</span><span class="stat-value" id="networks">1</span></div>
        </div>

        <!-- Proxy Pool Card -->
        <div class="card">
            <h3>🌐 Proxies</h3>
            <div class="stat"><span class="stat-label">Working</span><span class="stat-value" id="proxy-working">0</span></div>
            <div class="stat"><span class="stat-label">Total Pool</span><span class="stat-value" id="proxy-total">0</span></div>
            <div class="stat"><span class="stat-label">Health</span><span class="stat-value" id="proxy-health">0%</span></div>
            <div class="progress-bar"><div class="progress-fill" id="proxy-bar" style="width:0%"></div></div>
        </div>
    </div>

    <!-- Recent Sessions -->
    <div class="card" style="margin-top:15px;">
        <h3>📋 Recent Sessions</h3>
        <table class="session-table">
            <tr><th>ID</th><th>Section</th><th>Pages</th><th>Hovers</th><th>Clicks</th><th>Time</th><th>Status</th></tr>
            <tbody id="session-rows"><tr><td colspan="7" style="color:#8b949e;">Loading...</td></tr></tbody>
        </table>
    </div>

    <!-- Error Log -->
    <div class="card" style="margin-top:15px;">
        <h3>⚠️ Recent Errors</h3>
        <div class="error-log" id="errors">No errors</div>
    </div>

    <script>
        const RISK_CLASSES = {'safe':'risk-safe','caution':'risk-caution','warning':'risk-warning','danger':'risk-danger','critical':'risk-critical'};
        async function refresh() {
            try {
                const r = await fetch('/api/stats');
                const d = await r.json();
                document.getElementById('running').textContent = d.running ? '✅ Running' : '⏸️ Stopped';
                document.getElementById('running').className = 'stat-value ' + (d.running ? 'good' : 'warn');
                document.getElementById('uptime').textContent = d.uptime;
                document.getElementById('concurrent').textContent = d.concurrent;
                document.getElementById('sph').textContent = d.sessions_per_hour;
                const risk = d.risk_level || 'safe';
                document.getElementById('risk').textContent = risk;
                document.getElementById('risk').className = 'stat-value ' + (RISK_CLASSES[risk] || 'risk-safe');
                document.getElementById('vpn').textContent = d.vpn ? '🟢 On' : '🔴 Off';
                document.getElementById('vpn').className = 'stat-value ' + (d.vpn ? 'good' : 'bad');
                document.getElementById('total').textContent = d.total_sessions;
                document.getElementById('success').textContent = d.successful;
                document.getElementById('failed').textContent = d.failed;
                document.getElementById('rate').textContent = d.success_rate;
                document.getElementById('pages').textContent = d.total_pages;
                document.getElementById('avgtime').textContent = d.avg_session_time;
                document.getElementById('revenue').textContent = d.revenue;
                document.getElementById('projected').textContent = d.projected;
                document.getElementById('hovers').textContent = d.ad_hovers;
                document.getElementById('clicks').textContent = d.ad_clicks;
                document.getElementById('networks').textContent = d.networks;
                document.getElementById('proxy-working').textContent = d.proxy_working;
                document.getElementById('proxy-total').textContent = d.proxy_total;
                const pct = d.proxy_total > 0 ? Math.round(d.proxy_working/d.proxy_total*100) : 0;
                document.getElementById('proxy-health').textContent = pct + '%';
                document.getElementById('proxy-bar').style.width = pct + '%';
                if (d.recent && d.recent.length) {
                    document.getElementById('session-rows').innerHTML = d.recent.map(s =>
                        `<tr><td>${s.id}</td><td>${s.section}</td><td>${s.pages}</td><td>${s.hovers}</td><td>${s.clicks}</td><td>${s.time}s</td><td>${s.ok ? '✅' : '❌'}</td></tr>`
                    ).join('');
                }
                if (d.errors && d.errors.length) {
                    document.getElementById('errors').textContent = d.errors.join('\\n');
                }
            } catch(e) { console.error(e); }
        }
        refresh();
        setInterval(refresh, 5000);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(MAIN_PAGE)


@app.route('/api/stats')
def api_stats():
    with state_lock:
        data = dict(farm_state)
    data['ad_hovers'] = data.get('total_ad_hovers', 0)
    data['ad_clicks'] = data.get('total_ad_clicks', 0)
    data['vpn'] = data.get('vpn_connected', False)
    data['networks'] = data.get('network_count', 1)
    data['recent'] = data.get('recent_sessions', [])
    return jsonify(data)


def start_dashboard(host: str = '127.0.0.1', port: int = 5000):
    """Start dashboard in a background thread."""
    def run():
        app.run(host=host, port=port, debug=False, use_reloader=False)
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    print(f"📊 Dashboard: http://{host}:{port}")
    return thread


if __name__ == '__main__':
    print("LOPINUZE Ad Farm V3 Dashboard")
    print("Starting on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True)