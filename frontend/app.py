import streamlit as st
import requests
import pandas as pd


st.set_page_config(page_title='AI Jobs', layout='wide')


if 'page_number' not in st.session_state:
    st.session_state.page_number = 0

if 'search_clicked' not in st.session_state:
    st.session_state.search_clicked = False



def show_results():
    st.session_state.search_clicked = True
    st.session_state.page_number = 0


def next_page():
    st.session_state.page_number += 1

def prev_page():
    if st.session_state.page_number > 0:
        st.session_state.page_number -= 1

def reset_page():
    st.session_state.page_number = 0



st.title('Моноторинг рынка вакансий в сфере ИИ')

BASE_URL = 'http://127.0.0.1:8000'

st.subheader('Обзор рынка')

try:
    analytics_res = requests.get(f'{BASE_URL}/jobs?limit=2000')
    if analytics_res.status_code == 200:
        df_all = pd.DataFrame(analytics_res.json()['items'])

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.write('Топ 10 городов по количеству вакансий')
            city_counts = df_all['city'].value_counts().head(10).sort_values(ascending=False)
            st.bar_chart(city_counts)

        with col_g2:
            st.write('Средняя зарплата (USD) по категориям')
            avg_salary = df_all.groupby('job_category')['annual_salary_usd'].mean().sort_values(ascending=False)
            st.bar_chart(avg_salary)
        
        st.divider()

    else:
        st.info('Данные для аналитики не найдены')

except Exception as e:
    st.error(f'Ошибка загрузки аналитики: {e}')        





try:
    response = requests.get(f'{BASE_URL}/cities')
    if response.status_code == 200:
        cities = ['Все города'] + response.json()
    else:
        cities = ['Все города']
except:
    cities = ['Все города']


selected_city = st.selectbox('Выберите город:', cities, on_change=reset_page)



st.button('Показать вакансии', on_click=show_results)

if st.session_state.search_clicked:
    limit = 10
    offset = st.session_state.page_number * limit


    if selected_city == 'Все города':
        url = f'{BASE_URL}/jobs?limit={limit}&offset={offset}'
    else:
        url = f'{BASE_URL}/jobs?city={selected_city}&limit={limit}&offset={offset}'
    
    res = requests.get(url)

    if res.status_code == 200:
        result = res.json()
        total_jobs = result['total']
        df = pd.DataFrame(result['items'])
        df.index = df.index + offset + 1

        import math
        total_pages = math.ceil(total_jobs / limit)


        if not df.empty:
            st.write(f'Найдено вакансий: {total_jobs}')
            st.write(f'Показаны вакансии {offset + 1} - {offset + len(df)}')
            st.dataframe(df, use_container_width = True)

            col1, col2, col3 = st.columns([5, 2, 5])

            with col2:
                selected_page = st.number_input(f'Страница из {total_pages}', min_value=1, max_value=total_pages, value=st.session_state.page_number + 1)
                
                if selected_page != st.session_state.page_number + 1:
                    st.session_state.page_number = selected_page - 1
                    st.rerun()
    
        else:
            st.warning('По вашему запросу ничего не найдено.')

    else:
        st.error('Ошибка связи с сервером')

