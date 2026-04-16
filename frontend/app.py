import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title='AI Jobs')

st.title('Моноторинг рынка вакансий в сфере ИИ')

API_URL = 'http://127.0.0.1:8000/jobs'

if st.button('Загрузить данные'):
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            jobs_data = response.json()
            df = pd.DataFrame(jobs_data)
            st.success(f'Успешно загружено {len(df)} вакансий.')
            st.dataframe(df)
        else:
            st.error('Бэкенд ответил ошибкой')
    except Exception as e:
        st.error(f'Не удалось подключиться к бэкенду. Ошибка: {e}')