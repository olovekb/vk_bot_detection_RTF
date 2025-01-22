from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import requests
from datetime import datetime
from time import sleep
import pandas as pd
import joblib
import networkx as nx
from statistics import mean
from typing import Dict, Any
import re

# Базовый URL для запросов к API VK
BASIC_LINK = 'https://api.vk.com/method/'
ACCESS_TOKEN = '55e9ed5455e9ed5455e9ed545f56ce2ea1555e955e9ed543264e2e106416ce5f8d6b88e'

USER_FIELDS = [
    "has_photo", "sex", "bdate", "city", "country", "has_mobile", "counters"
]

PURE_FIELDS = [
    "has_photo", "sex", "has_mobile", "relation"
]

COUNTER_FIELDS = [
    "albums", "audios", "followers", "friends", "pages", "photos", "subscriptions", "videos", "clips_followers"
]

LIST_OF_FEATURES = [
    'avg_cl', 'trans', 'average_neighbor_degree', 'average_degree_connectivity', 'degree_centrality',
    'closeness_centrality', 'betweenness_centrality', 'diameter'
]

# Инициализация FastAPI
app = FastAPI()

# Модель для запроса через API
class UserRequest(BaseModel):
    uid: str = Field(..., description="ID пользователя или ссылка на профиль VK (например, https://vk.com/id12345 или https://vk.com/username)")

# Функция для получения числового ID из ссылки
def extract_id_from_link(link: str) -> str:
    """Извлечение числового ID пользователя из ссылки на профиль VK."""
    match = re.search(r"vk\.com/(id(\d+)|[a-zA-Z0-9_.]+)", link)
    if match:
        if match.group(2):  # Если это формат idXXXXXX
            return match.group(2)  # Возвращаем только числовую часть
        return match.group(1)  # Если это screen_name, возвращаем его
    return link  # Если это не ссылка, возвращаем оригинальный `uid`

# Функция для получения информации о пользователе VK
def get_user_info(user_id):
    method = 'users.get'
    payload = {
        'user_ids': [user_id],
        'fields': ','.join(USER_FIELDS),
        'v': '5.130',
        'access_token': ACCESS_TOKEN
    }
    response = requests.get(BASIC_LINK + method, params=payload).json()
    print(f"Ответ API для пользователя {user_id}: {response}")  # Лог ответа API
    if 'response' in response and len(response['response']) > 0:
        user_info = response['response'][0]
        print(f"Полученные данные пользователя {user_id}: {user_info}")
        return user_info
    else:
        raise HTTPException(status_code=404, detail="User not found")

# Функция для получения списка друзей пользователя
def get_friends_ids(user_id, uid2friends=None):
    """Получение списка друзей пользователя для построения графа."""
    print(f"Запрос списка друзей для пользователя с ID: {user_id}")
    method = 'friends.get'
    payload = {
        'user_id': user_id,
        'count': 500,
        'offset': 1,
        'order': 'random',
        'v': '5.130',
        'access_token': ACCESS_TOKEN
    }
    response = requests.get(BASIC_LINK + method, params=payload).json()

    # Проверка на ошибки
    if 'response' in response:
        friends = response['response']['items']
        print(f"Найдено {len(friends)} друзей для пользователя {user_id}.")
        # Если передан uid2friends, обновляем его
        if uid2friends is not None:
            uid2friends[user_id] = friends
        return friends, len(friends)  # Возвращаем и список друзей, и их количество
    else:
        error_msg = response.get('error', {}).get('error_msg', 'Unknown error')
        print(f"Ошибка при получении друзей пользователя {user_id}: {error_msg}")
        if uid2friends is not None:
            uid2friends[user_id] = []
        return [], 0  # Если ошибка, возвращаем пустой список и 0

# Функция для вычисления возраста пользователя
def calculate_age(bdate: str):
    bdate_list = bdate.split(".")
    if len(bdate_list) != 3:
        return None
    bday, bmonth, byear = map(int, bdate_list)
    today = datetime.today()
    return today.year - byear - ((today.month, today.day) < (bmonth, bday))

# Преобразование данных о пользователе в нужный формат
def transform_user_info(user_info):
    """Преобразование данных пользователя."""
    transformed_user_info = {}
    # Копирование полей из PURE_FIELDS
    for user_field in PURE_FIELDS:
        transformed_user_info[user_field] = user_info.get(user_field, None)
    # Копирование полей из COUNTER_FIELDS
    for user_field in COUNTER_FIELDS:
        transformed_user_info[user_field] = user_info.get("counters", {}).get(user_field, None)
    # Вычисление возраста
    transformed_user_info["age"] = calculate_age(user_info["bdate"]) if "bdate" in user_info else None
    # ID города пользователя
    transformed_user_info["city"] = user_info.get("city", {}).get("id")
    # ID страны пользователя
    transformed_user_info["country"] = user_info.get("country", {}).get("id")
    return transformed_user_info

# Создание графа друзей пользователя
def make_graph_for_user(user_id, uid2friends):
    graph = nx.Graph()
    graph.add_node(user_id)
    friends_ids = set(uid2friends[user_id])
    for friend_id in friends_ids:
        graph.add_edge(user_id, friend_id)
        friends_ids_2nd_gen = uid2friends.get(friend_id, [])
        for friend_id_2nd_gen in friends_ids_2nd_gen:
            if friend_id_2nd_gen in friends_ids:
                graph.add_edge(friend_id_2nd_gen, friend_id)
    return graph

# Функция для создания графа друзей
def make_graph(user_id, uid2friends):
    """Создание графа друзей с обработкой друзей второго уровня."""
    get_friends_ids(user_id, uid2friends)
    sleep(0.3)  # Пауза для предотвращения блокировки

    friends_ids = set(uid2friends[user_id])
    for uid in friends_ids:
        if uid not in uid2friends:
            get_friends_ids(uid, uid2friends)
            sleep(0.3)

# Извлечение характеристик из графа
def get_graph_features(graph_1):
    avg_cl = nx.average_clustering(graph_1)
    trans = nx.transitivity(graph_1)
    try:
        average_neighbor_degree = mean(nx.average_neighbor_degree(graph_1))
    except:
        average_neighbor_degree = None
    try:
        average_degree_connectivity = mean(nx.average_degree_connectivity(graph_1).values())
    except:
        average_degree_connectivity = None
    degree_centrality = mean(nx.degree_centrality(graph_1).values())
    closeness_centrality = mean(nx.closeness_centrality(graph_1).values())
    betweenness_centrality = mean(nx.betweenness_centrality(graph_1).values())
    diameter = nx.diameter(graph_1) if nx.is_connected(graph_1) else None
    features = [avg_cl, trans, average_neighbor_degree, average_degree_connectivity,
                degree_centrality, closeness_centrality, betweenness_centrality, diameter]
    graph_info = dict()
    for i, feature in enumerate(LIST_OF_FEATURES):
        graph_info[feature] = features[i]
    return graph_info

# Функция для создания DataFrame для пользователя
def create_df_for_person(uid):
    # Извлечение ID из ссылки
    user_id = extract_id_from_link(uid)
    print(f"Извлеченный user_id: {user_id}")

    # Получение информации о пользователе
    info = get_user_info(user_id)
    print(f"Данные пользователя до преобразования: {info}")
    info = transform_user_info(info)
    print(f"Данные пользователя после преобразования: {info}")
    
    # Получение списка друзей и их количества
    friends, friends_count = get_friends_ids(user_id)
    print(f"Количество друзей пользователя {user_id}: {friends_count}")
    info['friends'] = friends_count  # Добавляем количество друзей в информацию о пользователе
    
    # Создание графа друзей
    graph = {user_id: friends}
    make_graph(user_id, graph)
    print(f"Граф друзей для user_id {user_id}: {graph}")
    
    # Расчет характеристик графа
    graph_1 = make_graph_for_user(user_id, graph)
    graph_feat = get_graph_features(graph_1)
    print(f"Характеристики графа для user_id {user_id}: {graph_feat}")
    
    # Объединение информации и характеристик графа
    combined_info = {**info, **graph_feat}
    person_df = pd.DataFrame({str(k): [v] for k, v in combined_info.items()})
    person_df.fillna(value=0, axis=1, inplace=True)
    
    pd.set_option('display.max_columns', None)  # Показывать все столбцы
    pd.set_option('display.max_rows', None)     # Показывать все строки
    pd.set_option('display.expand_frame_repr', False)  # Отключить перенос строк

    # Лог данных, отправляемых в модель
    print(f"Данные, отправляемые в модель для user_id {user_id}:\n{person_df}")
    return person_df

# Загрузка модели
model = joblib.load('model.pkl')

# Предсказание с использованием модели
def make_prediction(person_df):
    print(f"Колонки для модели: {person_df.columns.tolist()}")
    prediction = model.predict(person_df)[0]
    pred_proba = model.predict_proba(person_df)[:, 1][0]
    return prediction, pred_proba

@app.post("/predict/")
def predict(request: UserRequest):
    uid = request.uid
    try:
        person_df = create_df_for_person(uid)
        prediction, probability = make_prediction(person_df)

        # Преобразование numpy-значений в стандартные Python-значения
        prediction = int(prediction)
        probability = float(probability)

        message = f'The user with id {uid} is {"a bot" if prediction else "not a bot"} with probability {probability:.2f}'
        return {"uid": uid, "message": message, "prediction": prediction, "probability": probability}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health/")
def health_check():
    return {"status": "ok"}