import streamlit as st
import requests
import pandas as pd
import plotly.express as px


st.set_page_config(page_title='AI Jobs', layout='wide')

BASE_URL = 'http://127.0.0.1:8000'



try:
    stats_res = requests.get(f'{BASE_URL}/stats')
    if stats_res.status_code == 200:
        db_stats = stats_res.json()
        max_salary_limit = int(db_stats['max_salary'])
    else:
        max_salary_limit = 500000
except:
    max_salary_limit = 500000





try:
    response = requests.get(f'{BASE_URL}/cities')
    if response.status_code == 200:
        cities = ['Все города'] + response.json()
    else:
        cities = ['Все города']
except:
    cities = ['Все города']





try:
    res_cat = requests.get(f'{BASE_URL}/categories')
    if res_cat.status_code == 200:
        categories = ['Все категории'] + res_cat.json()
    else:
        categories = ['Все категории']
except:
    categories = ['Все категории']





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







with st.sidebar:
    st.title('Меню')
    page = st.radio('', ['Аналитика', 'Поиск вакансий'])




if page == 'Аналитика':
    st.title('Анализ рынка вакансий в сфере ИИ')


    if 'db_stats' in locals() and db_stats:
        m1, m2, m3 = st.columns(3)
        m1.metric('Всего вакансий', f'{db_stats['total_cnt']:,}')
        m2.metric('Средняя зарплата за год', f'${db_stats['avg_salary']:,}')
        m3.metric('Maкс. предложение', f'${db_stats['max_salary']:,}')
        st.divider()


    try:
        analytics_res = requests.get(f'{BASE_URL}/jobs?limit=2000')
        if analytics_res.status_code == 200:
            df_all = pd.DataFrame(analytics_res.json()['items'])

            col_g1, col_g2 = st.columns(2)

            with col_g1:
                st.write('Топ 10 городов по количеству вакансий')
                city_counts = df_all['city'].value_counts().head(10).reset_index()
                city_counts.columns=['city', 'count']
                fig_city = px.bar(city_counts, x='city', y='count',
                                labels={'city': 'Город', 'count': 'Вакансии'})
                fig_city.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(l=20, r=20, t=30, b=20), height=400)
                st.plotly_chart(fig_city, use_container_width=True)

            with col_g2:
                st.write('Средняя годовая зарплата (USD) по категориям')
                avg_salary = df_all.groupby('job_category')['annual_salary_usd'].mean().sort_values(ascending=False).reset_index()
                avg_salary.columns = ['job_category', 'salary']
                fig_salary = px.bar(avg_salary, x='job_category', y='salary', labels={'job_category': 'Категория', 'salary': 'Средняя зарплата'})
                fig_salary.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(l=20, r=20, t=30, b=20), height=400)
                st.plotly_chart(fig_salary, use_container_width=True)
            
            st.divider()


            st.write('Структура рынка по категориям')
            df_category = df_all['job_category'].value_counts().reset_index()
            df_category.columns = ['Категория', 'Количество']

            category_pie = px.pie(df_category, values='Количество', names='Категория', )
            st.plotly_chart(category_pie)


        else:
            st.info('Данные для аналитики не найдены')

    except Exception as e:
        st.error(f'Ошибка загрузки аналитики: {e}')       









elif page == 'Поиск вакансий':
    st.title('Поиск вакансий в сфере ИИ')


    filter_1, filter_2, filter_3, button, col4 = st.columns([2, 2, 2, 2, 4])

    with filter_1:
        selected_city = st.selectbox('Выберите город:', cities, on_change=reset_page)

    with filter_2:
        selected_category = st.selectbox('Категория:', categories, on_change=reset_page)

    with filter_3:
        min_salary = st.slider('Мин. зп в год ($):', min_value=0, max_value=max_salary_limit, value=0, step=5000)

    with button:
        st.button('Показать вакансии', on_click=show_results)

    with col4:
        pass





    if st.session_state.search_clicked:
        limit = 10
        offset = st.session_state.page_number * limit

        url = f'{BASE_URL}/jobs?limit={limit}&offset={offset}&min_salary={min_salary}'

        if selected_city != 'Все города':
            url += f'&city={selected_city}'

        if selected_category != 'Все категории':
            url += f'&category={selected_category}'


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
                
                display_cols = ['job_title', 'job_category', 'city', 'country', 'annual_salary_usd', 'monthly_cost', 'monthly_savings']
                
                rename_cols = {'job_title': 'Job Title', 'job_category': 'Category', 'city': 'City', 'country': 'Country', 'annual_salary_usd': 'Annual salary ($)', 'monthly_cost': 'Monthly Living + Rent Cost ($)', 'monthly_savings': 'Monthly Savings ($)'}
                
                display_df = df[display_cols].rename(columns=rename_cols)
                
                st.dataframe(display_df, use_container_width = True)

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

