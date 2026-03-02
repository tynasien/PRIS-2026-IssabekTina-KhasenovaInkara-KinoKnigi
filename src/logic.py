import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_PATH = os.path.join(BASE_DIR, 'data', 'raw', 'rules.json')

def load_rules():
    if not os.path.exists(RULES_PATH):
        return {
            "scenario_name": "Default",
            "thresholds": {"min_rating": 1.0, "max_rating": 10.0},
            "lists": {"blacklist": []}
        }
    with open(RULES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_rules(movie_dict):
    """Проверяет один фильм на соответствие правилам"""
    rules = load_rules()
    
    rating = movie_dict.get('imdb_score', 0)
    if rating < rules['thresholds']['min_rating']:
        return f"Рейтинг ({rating}) ниже допустимого"
    
    movie_genres = movie_dict.get('genres', [])
    for genre in movie_genres:
        if genre in rules['lists']['blacklist']:
            return f"Жанр '{genre}' запрещен правилами"
    
    return "Соответствует"

def process_text_message(text, graph, movies_list):
    """Анализирует запрос пользователя и ищет ответ"""
    query = text.lower().strip()
    
    if query in ["привет", "старт", "hi", "hello"]:
        return ("Салем! Я твой киносоветчик. 🎬\n\n"
                "Ты можешь:\n"
                "Написать жанр (например: 'Drama')\n"
                "Написать год (например: '1995')\n"
                "Написать слово из сюжета (например: 'adventure')")

    for node in graph.nodes:
        if query == node.lower():
            neighbors = list(graph.neighbors(node))
            return f"В базе знаний '{node}' найден в фильмах: {', '.join(neighbors[:7])}"

    found_titles = []
    for m in movies_list:
        if query in m['description'].lower() or query in m['title'].lower():
            found_titles.append(m['title'])
    
    if found_titles:
        return f"По вашему описанию подобрал: {', '.join(found_titles[:5])}"

    return "Не совсем понял. Попробуй ввести жанр, год или ключевое слово (например, 'Animation')."
def apply_production_model(movie):
    """
    Реализация продукционной модели (Rule-Based System).
    Набор правил IF-THEN для классификации контента.
    """
    score = movie.get('imdb_score', 0)
    genres = movie.get('genres', [])
    year = int(movie.get('year', 0))
    
    if score >= 8.0 and year < 2005:
        return "🏆Это культовая классика, проверенная временем."
    
    if score >= 8.0 and year >= 2015:
        return "🔥Современный блокбастер с высочайшим одобрением зрителей."
    
    if "Animation" in genres and score >= 8.0:
        return "🎨Эталонная анимация, рекомендованная всем возрастам."
    
    if "Drama" in genres and score >= 7.8:
        return "🎭Серьезная психологическая работа для вдумчивого просмотра."
    
    return "✅Качественный контент, прошедший фильтрацию по рейтингу 7.5+."