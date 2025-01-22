# -*- coding: utf-8 -*-
#%%
import networkx as nx
from statistics import *
from time import time, sleep
import logging
from vk_parser import get_friends_ids
# Конфигурация логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def make_graph(user_id_1, uid2friends):
    """Dict with list of friends is created."""
    #List of friends is added to dictionary uid2friends.
    if user_id_1 not in uid2friends:
        get_friends_ids(user_id_1, uid2friends)
        sleep(0.3)

    friends_ids = set(uid2friends[user_id_1])
    for uid in friends_ids:
        #Check if list if friends for uid hadn't been received.
        if uid in uid2friends:
            continue
        get_friends_ids(uid, uid2friends)
        sleep(0.3)

def get_graph_features(graph):
    """Рассчитывает метрики графа."""

    LIST_OF_FEATURES = [
    'avg_cl', 'trans', 'average_neighbor_degree', 'average_degree_connectivity',
    'degree_centrality', 'closeness_centrality', 'betweenness_centrality', 'diameter'
    ]
    logger.debug("Рассчитываем метрики графа.")
    
    if len(graph.nodes) == 0:
        return {field: 0 for field in LIST_OF_FEATURES}  # Если граф пустой, все метрики равны 0
    
    features = {
        'avg_cl': nx.average_clustering(graph),
        'trans': nx.transitivity(graph),
        'average_neighbor_degree': mean(nx.average_neighbor_degree(graph).values()) if len(graph.nodes) > 0 else 0,
        'average_degree_connectivity': mean(nx.average_degree_connectivity(graph).values()) if len(graph.nodes) > 0 else 0,
        'degree_centrality': mean(nx.degree_centrality(graph).values()) if len(graph.nodes) > 0 else 0,
        'closeness_centrality': mean(nx.closeness_centrality(graph).values()) if len(graph.nodes) > 0 else 0,
        'betweenness_centrality': mean(nx.betweenness_centrality(graph).values()) if len(graph.nodes) > 0 else 0,
        'diameter': nx.diameter(graph) if nx.is_connected(graph) else None,
    }
    logger.debug(f"Метрики графа успешно рассчитаны: {features}")
    return features

def make_graph_for_user(user_id_1, uid2friends):
    """Создание графа друзей Вконтакте пользователя с user_id."""

    graph = nx.Graph()
    graph.add_node(user_id_1)

    friends_ids = set(uid2friends[user_id_1])

    for friend_id in friends_ids:
        graph.add_edge(user_id_1, friend_id)
        friends_ids_2nd_gen = uid2friends[friend_id]
        for friend_id_2nd_gen in friends_ids_2nd_gen:
            if friend_id_2nd_gen in friends_ids:
                graph.add_edge(friend_id_2nd_gen, friend_id)
    return graph


def get_metrics_for_users(user_id):
    """Получение метрик по user_id."""

    uid2friends = dict()
    uid = user_id
    make_graph(uid, uid2friends)

    #print(uid2friends)

    graph = make_graph_for_user(uid, uid2friends)
    #print(graph)

    dict_of_features = get_graph_features(graph, uid)
    return dict_of_features
    
#%%
if __name__ == "__main__":
    user_id = 194854409#интовый idшник
    print(get_metrics_for_users(user_id))
# %%
