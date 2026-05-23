import os
import time
import pymysql
from datetime import datetime, timedelta
from flask import Flask, render_template, send_from_directory, request, jsonify, g

app = Flask(__name__)

# ---------- Конфигурация MySQL ----------
DB_CONFIG = {
    'host': '78.108.80.125',
    'user': 'u245369_umXh',
    'password': os.environ.get('DB_PASSWORD', 'QtBdOGPU'),  # ← пароль в переменную окружения или прямо в коде
    'database': 'b245369_YBCo',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# ---------- работа с БД ----------
def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(**DB_CONFIG)
    return g.db

def init_db():
    with app.app_context():
        db = get_db()
        with db.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS visits (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ip VARCHAR(45) NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
        db.commit()

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ---------- отслеживание активных сессий ----------
active_sessions = {}  # {ip: последнее время активности}

def update_active_session(ip):
    now = time.time()
    active_sessions[ip] = now
    cutoff = now - 300
    for ip_addr in list(active_sessions.keys()):
        if active_sessions[ip_addr] < cutoff:
            del active_sessions[ip_addr]

def record_visit(ip):
    db = get_db()
    with db.cursor() as cur:
        cur.execute('INSERT INTO visits (ip) VALUES (%s)', (ip,))
    db.commit()

# ---------- маршруты ----------
@app.route('/')
def home():
    ip = request.remote_addr
    update_active_session(ip)
    record_visit(ip)
    return render_template('index.html')

@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'robots.txt')

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
    db = get_db()
    with db.cursor() as cur:
        # общее количество посещений
        cur.execute('SELECT COUNT(*) AS total FROM visits')
        total = cur.fetchone()['total']

        # сегодня и вчера
        today = datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        cur.execute('SELECT COUNT(*) AS cnt FROM visits WHERE DATE(timestamp) = %s', (today,))
        today_count = cur.fetchone()['cnt']
        cur.execute('SELECT COUNT(*) AS cnt FROM visits WHERE DATE(timestamp) = %s', (yesterday,))
        yesterday_count = cur.fetchone()['cnt']

        # посещения по дням за последние 7 дней
        days = []
        counts = []
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            day_str = date.strftime('%Y-%m-%d')
            cur.execute('SELECT COUNT(*) AS cnt FROM visits WHERE DATE(timestamp) = %s', (day_str,))
            cnt = cur.fetchone()['cnt']
            days.append(date.strftime('%d.%m'))
            counts.append(cnt)

    return jsonify({
        'total': total,
        'today': today_count,
        'yesterday': yesterday_count,
        'days': days,
        'counts': counts
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=False, host='0.0.0.0', port=5000)
