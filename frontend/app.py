import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title='AI Jobs')

st.title('Моноторинг рынка вакансий в сфере ИИ')

BASE_URL = 'http://127.0.0.1:8000'

try:
    response = requests.get(f'{BASE_URL}/cities')
    if response.status_code == 200:
        cities = ['Все города'] + response.json()
    else:
        cities = ['Все города']
except:
    cities = ['Все города']


selected_city = st.selectbox('Выберите город:', cities)

if st.button('Показать вакансии'):

    if selected_city == 'Все города':
        url = f'{BASE_URL}/jobs'
    else:
        url = f'{BASE_URL}/jobs?city={selected_city}'
    
    res = requests.get(url)

    if res.status_code == 200:
        st.dataframe(pd.DataFrame(res.json()))
    else:
        st.error('Не удалось получить данные')