from fastapi import FastAPI
import sqlite3
import os

app = FastAPI()

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'jobs_project.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@app.get('/')
def home():
    return {'status': 'Сервер работает. Подключение к базе данных установлено.'}


@app.get('/jobs')
def get_jobs(city: str = None):
    conn = get_db_connection()
    try:
        if city:
            query = 'SELECT * FROM jobs WHERE city = ?'
            jobs = conn.execute(query, (city,)).fetchall()
        else:
            jobs = conn.execute('SELECT * FROM jobs LIMIT 10').fetchall()

        return [dict(row) for row in jobs]
    finally:
        conn.close()

@app.get('/cities')
def get_cities():
    conn = get_db_connection()
    try:
        cursor = conn.execute('SELECT DISTINCT city from jobs ORDER BY city')
        return [row['city'] for row in cursor.fetchall()]
    finally:
        conn.close()