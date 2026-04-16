import streamlit as st
import requests
import pandas as pd

if 'page_number' not in st.session_state:
    st.session_state.page_number = 0

def next_page():
    st.session_state.page_number += 1

def prev_page():
    if st.session_state.page_number > 0:
        st.session_state.page_number -= 1

def reset_page():
    st.session_state.page_number = 0

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


selected_city = st.selectbox('Выберите город:', cities, on_change=reset_page)

limit = 10
offset = st.session_state.page_number * limit

if st.button('Показать вакансии'):

    if selected_city == 'Все города':
        url = f'{BASE_URL}/jobs?limit={limit}&offset={offset}'
    else:
        url = f'{BASE_URL}/jobs?city={selected_city}&limit={limit}&offset={offset}'
    
    res = requests.get(url)

    if res.status_code == 200:
        df = pd.DataFrame(res.json())

        if not df.empty:
            st.write(f'Показаны вакансии {offset +1} - {offset + len(df)}')
            st.dataframe(df, use_container_width=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.button('Назад', on_click=prev_page, disabled=(st.session_state.page_number == 0))
            with col2:
                st.write(f'Страница {st.session_state.page_number + 1}')
            with col3:
                st.button('Вперед', on_click=next_page, disabled=(len(df) < limit))
        else:
            st.warning('На этой странице больше нет вакансий.')
            if st.button('Вернуться на первую страницу'):
                reset_page()
                st.rerun()

    else:
        st.error('Не удалось получить данные')

