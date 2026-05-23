import time
from datetime import datetime, timedelta
from collections import defaultdict
from flask import Flask, render_template, send_from_directory, request, jsonify
import os

app = Flask(__name__)

# ---------- Хранилище в памяти ----------
total_visits = 0
daily_visits = defaultdict(int)  # ключ: 'YYYY-MM-DD'
active_sessions = {}

def update_online(ip):
    now = time.time()
    active_sessions[ip] = now
    cutoff = now - 300
    for stored_ip in list(active_sessions.keys()):
        if active_sessions[stored_ip] < cutoff:
            del active_sessions[stored_ip]

def record_visit(ip):
    global total_visits
    total_visits += 1
    today = datetime.now().strftime('%Y-%m-%d')
    daily_visits[today] += 1

@app.route('/')
def home():
    ip = request.remote_addr
    update_online(ip)
    record_visit(ip)
    return render_template('index.html')

@app.route('/robots.txt')
def robots():
    try:
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'robots.txt')
        with open(file_path, 'r') as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        # если файл не найден или не читается, отдаём стандартное содержимое
        print(f"Ошибка чтения robots.txt: {e}")
        content = "User-agent: *\nAllow: /\nSitemap: https://yourdomain.com/sitemap.xml"
        return content, 200, {'Content-Type': 'text/plain'}

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'sitemap.xml')

@app.route('/api/online')
def online():
    now = time.time()
    cutoff = now - 300
    active = sum(1 for t in active_sessions.values() if t >= cutoff)
    return jsonify({'online': active})

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/api/stats')
def api_stats():
    days_labels = []
    counts = []
    for i in range(6, -1, -1):
        date = datetime.now() - timedelta(days=i)
        day_str = date.strftime('%Y-%m-%d')
        days_labels.append(date.strftime('%d.%m'))
        counts.append(daily_visits.get(day_str, 0))

    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    return jsonify({
        'total': total_visits,
        'today': daily_visits.get(today, 0),
        'yesterday': daily_visits.get(yesterday, 0),
        'days': days_labels,
        'counts': counts
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
