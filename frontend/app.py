import streamlit as st
import requests
import pandas as pd
import plotly.express as px


st.set_page_config(page_title='AI Jobs', layout='wide')

BASE_URL = 'http://127.0.0.1:8000'


@st.cache_data(ttl=600)
def load_all_jobs(url):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return pd.DataFrame(res.json()['items'])
    except:
        pass
    return pd.DataFrame()



@st.cache_data(ttl=600)
def load_stats(url):
    try:
        res = requests.get(url)
        if res.status_code == 200:
            return res.json()
    except:
        pass
    return None


@st.cache_data(ttl=600)
def load_cities(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return ['Все города'] + response.json()
    except:
        pass
    return ['Все города']



@st.cache_data(ttl=600)
def load_categories(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return ['Все категории'] + response.json()
    except:
        pass
    return ['Все категории']




df_all = load_all_jobs(f'{BASE_URL}/jobs?limit=2000')
db_stats = load_stats(f'{BASE_URL}/stats')
cities = load_cities(f'{BASE_URL}/cities')
categories = load_categories(f'{BASE_URL}/categories')



if db_stats:
    max_salary_limit = int(db_stats.get('max_salary', 500000))
else:
    max_salary_limit = 500000








if 'page_number' not in st.session_state:
    st.session_state.page_number = 0

if 'search_clicked' not in st.session_state:
    st.session_state.search_clicked = False



if 'year_key' not in st.session_state:
    st.session_state.year_key = 'Все'


if 'search_city_key' not in st.session_state:
    st.session_state.search_city_key = 'Все категории'

if 'search_salary_key' not in st.session_state:
    st.session_state.search_salary_key = 0


if 'search_years_key' not in st.session_state:
    st.session_state.search_years_key = []





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

    if not df_all.empty:

        available_years = sorted(df_all['posting_year'].unique().tolist())
        
        radio_options = ['Все'] + available_years


        try:
            curr_index = radio_options.index(st.session_state.get('year_key', 'Все'))

        except:
            curr_index = 0
        

        st.session_state.year_key = st.radio('Год:', options=radio_options, horizontal=True, index=curr_index)


        if st.session_state.year_key == 'Все':
            df_filtered = df_all
        
        else:
            df_filtered = df_all[df_all['posting_year'] == st.session_state.year_key]



        col_1_top, col_2_top = st.columns([2, 3])

        with col_1_top:

            total_cnt = len(df_filtered)
            avg_sal = int(df_filtered['annual_salary_usd'].mean()) if total_cnt > 0 else 0
            max_sal = int(df_filtered['annual_salary_usd'].max()) if total_cnt > 0 else 0


            st.metric('Всего вакансий', f'{total_cnt:,}')
            st.write('')
            st.write('')
            st.write('')
            st.metric('Средняя зарплата за год', f'${avg_sal:,}')
            st.write('')
            st.write('')
            st.write('')
            st.metric('Maкс. предложение', f'${max_sal:,}')
            
        with col_2_top:
            st.write('Доля вакансий по категориям')
            df_category = df_filtered['job_category'].value_counts().reset_index()
            df_category.columns = ['Категория', 'Количество']

            category_pie = px.pie(df_category, values='Количество', names='Категория', hole=0.5)
            category_pie.update_layout(margin=dict(t=20, b=20, l=0, r=0), height=350)
            st.plotly_chart(category_pie)

        st.divider()

        col_g1, col_g2 = st.columns(2)

        with col_g1:
            st.write('Топ 10 городов по количеству вакансий')
            city_counts = df_filtered['city'].value_counts().head(10).reset_index()
            city_counts.columns=['city', 'count']
            fig_city = px.bar(city_counts, x='city', y='count',
                            labels={'city': 'Город', 'count': 'Вакансии'})
            fig_city.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(l=20, r=20, t=30, b=20), height=400)
            st.plotly_chart(fig_city, use_container_width=True)

        with col_g2:
            st.write('Средняя годовая зарплата (USD) по категориям')
            avg_salary = df_filtered.groupby('job_category')['annual_salary_usd'].mean().sort_values(ascending=False).reset_index()
            avg_salary.columns = ['job_category', 'salary']
            fig_salary = px.bar(avg_salary, x='job_category', y='salary', labels={'job_category': 'Категория', 'salary': 'Средняя зарплата'})
            fig_salary.update_layout(xaxis_title=None, yaxis_title=None, margin=dict(l=20, r=20, t=30, b=20), height=400)
            st.plotly_chart(fig_salary, use_container_width=True)
        
        st.divider()


    else:
        st.error(f'Данные о вакансиях не найдены. Проверьте подключение к базе данных.')









elif page == 'Поиск вакансий':
    st.title('Поиск вакансий в сфере ИИ')

    years = sorted(df_all['posting_year'].unique().tolist())


    filter_1, filter_2, filter_3, filter_4, button, col5 = st.columns([2, 2, 2, 2.5, 2, 2])


    with filter_1:

        try:
            city_index = cities.index(st.session_state.get('search_city_key', 'Все города'))
        except:
            city_index = 0
    
        st.session_state.search_city_key = st.selectbox('Город:', cities, on_change=reset_page, index=city_index)

        selected_city = st.session_state.search_city_key



    with filter_2:

        try:
            category_index = categories.index(st.session_state.get('search_category_key', 'Все категории'))
        except:
            category_index = 0
        
        st.session_state.search_category_key = st.selectbox('Категория:', categories, on_change=reset_page, index=category_index)

        selected_category = st.session_state.search_category_key



    with filter_3:

        st.session_state.search_salary_key = st.slider('Мин. зп в год ($):', min_value=0, max_value=max_salary_limit, value=st.session_state.get('search_salary_key'), step=5000)

        min_salary = st.session_state.search_salary_key



    with filter_4:

        st.session_state.search_years_key = st.multiselect('Годы:', years, default=st.session_state.get('search_years_key', years))

        selected_years = st.session_state.search_years_key



    with button:
        st.write('')
        st.button('Показать вакансии', on_click=show_results)



    with col5:
        pass





    if st.session_state.search_clicked:
        limit = 10
        offset = st.session_state.page_number * limit

        url = f'{BASE_URL}/jobs?limit={limit}&offset={offset}&min_salary={min_salary}'

        if selected_city != 'Все города':
            url += f'&city={selected_city}'

        if selected_category != 'Все категории':
            url += f'&category={selected_category}'

        if selected_years:
            for y in selected_years:
                url += f'&years={y}'


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
                
                display_cols = ['job_title', 'job_category', 'posting_year', 'city', 'country', 'annual_salary_usd', 'monthly_cost', 'monthly_savings']
                
                rename_cols = {'job_title': 'Job Title', 'job_category': 'Category', 'posting_year': 'Year', 'city': 'City', 'country': 'Country', 'annual_salary_usd': 'Annual salary ($)', 'monthly_cost': 'Monthly Living + Rent Cost ($)', 'monthly_savings': 'Monthly Savings ($)'}
                
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

