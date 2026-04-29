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
def get_jobs(city: str = None, min_salary: int = 0, limit: int = 10, offset: int = 0):
    conn = get_db_connection()
    try:
        print('Проверка соединения')
        count_query = 'SELECT COUNT(*) FROM jobs WHERE 1=1'
        params = []

        if city:
            count_query += ' AND city = ?'
            params.append(city)

        
        if min_salary > 0:
            count_query += ' AND annual_salary_usd >= ?'
            params.append(min_salary)
        


        res = conn.execute(count_query, params).fetchone()
        total_count = res[0] if res else 0

        query = """SELECT j.*,
            ROUND(c.cost_of_living_plus_rent_idx / 100.0 * 5000, 2) as monthly_cost, 
            ROUND((j.annual_salary_usd / 12.0) - (c.cost_of_living_plus_rent_idx / 100.0 * 5000), 2) as monthly_savings
        FROM jobs j
        LEFT JOIN cities_costs c ON j.city = c.city
        WHERE 1=1
        """

        # тк индексы расчитываются относительно показателей Нью-Йорка, то чтобы рассчитать расходы нужно учесть средние расходы в Нью-Йорке (согласно Numbeo это примерно 5000$)

        final_params = []

        if city:
            query += ' AND j.city = ?'
            final_params.append(city)

        if min_salary > 0:
            query += ' AND j.annual_salary_usd >= ?'
            final_params.append(min_salary)

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



@app.get('/stats')
def get_stats():
    conn = get_db_connection()
    try:
        res = conn.execute('SELECT MAX(annual_salary_usd) as max_salary, COUNT(*) as total_cnt, ROUND(AVG(annual_salary_usd), 0) as avg_salary FROM jobs').fetchone()
        return dict(res)
    finally:
        conn.close()