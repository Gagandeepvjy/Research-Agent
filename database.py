import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY,
                    query TEXT,
                    summary TEXT,
                    key_points TEXT,
                    links TEXT,
                    created_at TEXT
                )''')
    conn.commit()
    conn.close()

def save_report(query, summary, key_points, links):
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    created_at = datetime.now().isoformat()
    c.execute('INSERT INTO reports (query, summary, key_points, links, created_at) VALUES (?, ?, ?, ?, ?)',
              (query, summary, key_points, links, created_at))
    conn.commit()
    conn.close()

def get_all_reports():
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute('SELECT id, query, created_at FROM reports ORDER BY created_at DESC')
    reports = c.fetchall()
    conn.close()
    return reports

def get_report_by_id(report_id):
    conn = sqlite3.connect('reports.db')
    c = conn.cursor()
    c.execute('SELECT * FROM reports WHERE id = ?', (report_id,))
    report = c.fetchone()
    conn.close()
    return report
