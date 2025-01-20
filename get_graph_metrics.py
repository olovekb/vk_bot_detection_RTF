# -*- coding: utf-8 -*-
import json
import pandas as pd
import networkx as nx
import csv
from statistics import *
import networkx as nx
import json
import pandas as pd
from threading import Thread

import requests
from time import time, sleep

BASIC_LINK = 'https://api.vk.com/method/'
#токен курва
ACCESS_TOKEN = ''

def get_friends_ids(user_id, uid2friends):
    """Addition of friends ids to dictionary uid2friends"""

    method = 'friends.get?user_id={user_id}&count={count}&offset={offset}&access_token={access_token}&v={api_version}'
    payload = {
        'user_id': user_id,
        'count': 500,
        'offset': 1,
        'order': 'random',
        'v': '5.199',
        'access_token': ACCESS_TOKEN
    }
    response = requests.get(BASIC_LINK + method, params=payload).json()
    #Check for any errors occuring
    if 'response' in response:
        uid2friends[user_id] = response['response']['items']
    else:
        #print(response['error']['error_msg'])
        uid2friends[user_id] = []

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

def get_graph_features(graph_1, user_id):
    avg_cl = nx.average_clustering(graph_1)
    trans = nx.transitivity(graph_1)
    average_neighbor_degree = mean(nx.average_neighbor_degree(graph_1))
    average_degree_connectivity = mean(nx.average_degree_connectivity(graph_1).values())
    degree_centrality = mean(nx.degree_centrality(graph_1).values())
    closeness_centrality = mean(nx.closeness_centrality(graph_1).values())
    betweenness_centrality = mean(nx.betweenness_centrality(graph_1).values())
    diameter = nx.diameter(graph_1)
    features = [avg_cl, trans, average_neighbor_degree, average_degree_connectivity,
           degree_centrality, closeness_centrality, betweenness_centrality,  diameter]
    list_of_features = []
    for feature in features:
        if type(feature) == int or type(feature) == float:
            list_of_features.append(feature)
        else:
            pass
    return list_of_features

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

    list_of_features = get_graph_features(graph, uid)
    return list_of_features

if __name__ == "__main__":
    user_id = 1#интовый idшник
    print(get_metrics_for_users(user_id))