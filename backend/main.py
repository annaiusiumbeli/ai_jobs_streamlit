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
def get_jobs(city: str = None, limit: int = 10, offset: int = 0):
    conn = get_db_connection()
    try:
        print('Проверка соединения')
        count_query = 'SELECT COUNT(*) FROM jobs'
        params = []

        if city:
            count_query += ' WHERE city = ?'
            params.append(city)
        
        res = conn.execute(count_query, params).fetchone()
        total_count = res[0] if res else 0

        query = """SELECT j.*,
            ROUND(c.cost_of_living_plus_rent_idx / 100.0 * 5000, 2) as monthly_cost, 
            ROUND((j.annual_salary_usd / 12.0) - (c.cost_of_living_plus_rent_idx / 100.0 * 5000), 2) as monthly_savings
        FROM jobs j
        LEFT JOIN cities_costs c ON j.city = c.city"""

        # тк индексы расчитываются относительно показателей Нью-Йорка, то чтобы рассчитать расходы нужно учесть средние расходы в Нью-Йорке (согласно Numbeo это примерно 5000$)

        final_params = []

        if city:
            query += ' WHERE j.city = ?'
            final_params.append(city)

        query += ' LIMIT ? OFFSET ?'
        final_params.extend([limit, offset])

        jobs = conn.execute(query, final_params).fetchall()

        return {'total': total_count, 'items': [dict(row) for row in jobs]}

    except Exception as e:
        print(f'Ошибка SQL: {e}')
        return {'error': str(e)}

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