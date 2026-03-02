import streamlit as st
import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
import os
import re

from mock_data import movies_data
from knowledge_graph import create_graph
from logic import check_rules, process_text_message, apply_production_model

st.set_page_config(page_title="Movie Management System", layout="wide")

# session state initialization

if 'graph' not in st.session_state:
    st.session_state.graph = create_graph()

if 'movies' not in st.session_state:
    st.session_state.movies = movies_data

if 'messages' not in st.session_state:
    st.session_state.messages = []

# сайдбар

with st.sidebar:
    st.header("📥 Выбор фильма")
    
    movie_titles = [m['title'] for m in st.session_state.movies]
    selected_name = st.selectbox("Выберите из топ 250-фильмов", movie_titles)
    
    current_movie = next(m for m in st.session_state.movies if m['title'] == selected_name)
    
    if st.button("Анализировать фильм"):
        st.subheader(f"🎬 {current_movie['title']}")
        
        if current_movie.get('poster') and current_movie['poster'] != 'nan':
            st.image(current_movie['poster'], use_container_width=True)
            
        st.write(f"**Рейтинг:** {current_movie['imdb_score']} ⭐")
        st.write(f"**Год:** {current_movie['year']}")
        st.write(f"**Жанры:** {', '.join(current_movie['genres'])}")

        st.divider()
        st.subheader("Оценка системы")
        
        verdict = apply_production_model(current_movie)
        st.success(verdict)

    st.divider()

# main interface

st.title("🎬 Movie Advisor System v2.0")

col1, col2 = st.columns([1, 1])

# knowledge Graph

with col1:
    st.subheader("🕸 Граф знаний")

    net = Network(height="400px", width="100%", bgcolor="#f0f2f6", font_color="black")
    net.from_nx(st.session_state.graph)
    
    path = "graph_display.html"
    net.save_graph(path)

    with open(path, 'r', encoding='utf-8') as f:
        html_data = f.read()

    components.html(html_data, height=450)

# чатбот консультант

with col2:
    st.subheader("💬 Чат-бот консультант")
    
    chat_container = st.container(height=380)

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)

    if user_input := st.chat_input("Спроси про жанр или год..."):

        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })

        year_match = re.search(r'(\d{4})', user_input)

        if year_match and int(year_match.group(1)) < 1980:
            answer = "К сожалению, в нашем сервисе только фильмы с 1980 года."
        else:
            answer = process_text_message(
                user_input,
                st.session_state.graph,
                st.session_state.movies
            )

        # поиск рекомендаций

        recommended_movies = []

        for m in st.session_state.movies:
            if m['title'].lower() in answer.lower():
                recommended_movies.append(m)

        recommended_movies = recommended_movies[:3]

        detailed_info_text = "\n🎬 **Топ-3 рекомендации**\n"

        if recommended_movies:

            for idx, movie in enumerate(recommended_movies, 1):

                validation_result = check_rules(movie)

                validation_text = "🟢 Правильно" if validation_result else "🔴 Нарушение правил"

                poster = movie.get("poster")
                poster_html = ""

                if poster and poster != "nan":
                    poster_html = f"""
<br>
<img src="{poster}" width="220">
<br>
"""

                detailed_info_text += f"""
---
🏆 **#{idx}**

📌 **Название:** {movie.get('title', '—')}
⭐ **Рейтинг:** {movie.get('imdb_score', '—')}
📅 **Год:** {movie.get('year', '—')}
🎭 **Жанры:** {', '.join(movie.get('genres', []))}

📝 **Описание:**
{movie.get('description', 'Описание недоступно.')}

Валидация: {validation_text}

{poster_html}
"""

        final_answer = answer + ("\n\n" + detailed_info_text if recommended_movies else "")

        st.session_state.messages.append({
            "role": "assistant",
            "content": final_answer
        })

        st.rerun()

st.caption("Разработано в рамках лабораторной работы PRIS-2026")