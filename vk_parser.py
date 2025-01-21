# Ссылка для получения ключа: https://dev.vk.com/ru/api/access-token/getting-started

import os
import json

import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import numpy as np
load_dotenv()


def get_friends_ids(user_id):
    """Addition of friends ids to dictionary uid2friends"""
    uid2friends = {}
    method = 'friends.get?user_id={user_id}&count={count}&offset={offset}&access_token={access_token}&v={api_version}'
    payload = {
        'user_id': user_id,
        'count': 500,
        'offset': 1,
        'order': 'random',
        'v': '5.199',
        'access_token': os.getenv('VK_OAUTH_TOKEN')
    }
    response = requests.get('https://api.vk.com/method/' + method, params=payload).json()

    if 'response' in response:
        uid2friends[user_id] = response['response']['items']
    else:
        uid2friends[user_id] = []
    return uid2friends,len(uid2friends.keys())

included_params= [
    'albums', #included
    'audios', #included
    'followers', #included
    'friends', #included
    'pages', #included
    'photos', #included
    'subscriptions', #included
    'videos', #included
]

def get_registration_date(id):
    url = f'https://vk.com/foaf.php?id={id}'

    response = requests.get(url)
    if response.status_code == 200:
        for line in response.text.split('\n'):
            if 'ya:created' in line:
                return line.split('=')[1].split('T')[0].replace('"','')
    return None

def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created.")
    else:
        print(f"Directory '{directory_path}' already exists.")

    return directory_path
    

def save_dict_to_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4,ensure_ascii=False)
        print(f"Dictionary saved to '{filepath}'.")

    return filepath


def send_request(method, params):
    url = "https://api.vk.com/method/" + method

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    return None

def get_user_info(user_id, access_token,user_params):
    method = "users.get"
 
    params = {
        'user_ids': user_id,
        'access_token': access_token,
        'fields': user_params,
        'v': '5.199'
    }
    
    data = send_request(method=method,
                        params=params)
    
    if data:
        if 'response' in data:
            return data['response'][0]  
        else:
            return data  
    else:
        return None
        

def get_user_friends(user_id, access_token):
    method = "friends.get"
 
    params = {
        'user_id': int(user_id),
        'access_token': access_token,
        'v': '5.199'
    }
    
    data = send_request(method=method,
                        params=params)
    if data:
        if 'response' in data:
            return data['response']['count']
        else:
            return data['count']
    else:
        return None

def get_user_followers(user_id, access_token, result='amount', **followers_data):
   
    method = 'users.getFollowers'

    params = {
        'user_id': user_id,  
        'access_token': access_token,
        'v': '5.199'  
    }

    if followers_data.get('get_followers_info', False):
        params['fields'] = followers_data.get('get_followers_info')

    data = send_request(method=method, params=params)

    if followers_data.get('get_all_followers', False):
        amount = data['response']['count']
        params['count'] = amount

    data = send_request(method=method, params=params)
    
    if result == 'amount':
        amount = data['response']['count']
        return amount
    elif result == 'data':
        return data['response']
    else:
        raise ValueError("Invalid result type specified. Use 'amount' or 'data'.")


# Функция получения подписок пользователя
def get_user_subscriptions(user_id, access_token, result='amount', **subscriptions_data):
   
    
    method = 'users.getSubscriptions'

    params = {
        'user_id': user_id,  
        'access_token': access_token,
        'v': '5.199'  
    }

    data = send_request(method=method, params=params)

    if subscriptions_data.get('extended',False):
        params['extended'] = 1
        data = send_request(method=method, params=params)

        
    if result == 'amount':
        amount_type = subscriptions_data.get('amount_type',False)
        if amount_type == 'users':
            amount = data['response']['users']['count']
            return amount
        elif amount_type == 'groups':
            amount = data['response']['groups']['count']
            return amount
        return amount
    elif result == 'data':
        return data['response']

def parse_data(user_name,user_params,save = True):
    token = os.getenv('VK_OAUTH_TOKEN')
    access_token = token  
    user_info = get_user_info(user_name, access_token,user_params)
    print("user_info1",user_info)
    user_info['friends'] = get_user_friends(user_info['id'],access_token)
    print("user_info2",user_info)
    if 'error' in user_info.keys():
        print('Error')
        print('Data:',user_info)
    else:
        user_id = user_info['id']
        if save:
            filepath = ensure_directory_exists(f"Data/{user_id}")
            save_dict_to_json(user_info, f'{filepath}/userinfo.json')
    return user_info

def is_not_empty(value):
    if value not in ["", [], {}] and value is not None:
        return value
    else:
        return 0 

def calculate_age(bdate: str):

    bdate_list = bdate.split(".")
    if len(bdate_list) != 3:
        return None
    bday, bmonth, byear = bdate_list
    today = datetime.today() 
    return today.year - int(byear) - ((today.month, today.day) < (int(bmonth), int(bday)))


def clear_data(user_info):
    result = {}
    required_fileds = [
        'has_photo',                    
        'sex' ,                         
        'has_mobile' ,                  
        'relation' ,                    
        'albums' ,                      
        'audios' ,                      
        'followers' ,                   
        'friends' ,                     
        'pages' ,                       
        'photos' ,                      
        'subscriptions' ,               
        'videos' ,                      
        'clips_followers' ,             
        'age' ,                         
        'city' ,                        
        'country' 
    ]
    age = calculate_age(user_info['bdate'])
    for param in required_fileds:
        if param in user_info.keys():
            result[param] = is_not_empty(user_info[param])
            # result[param] = user_info[param]
        elif param in included_params and param in user_info['counters']:
            result[param] = user_info['counters'][param]
        else:
            result[param] = 0
    result['age'] = age
    if 'city' in result and 'title' in result['city']:
        result['city'] = 1
    else:
        result['city'] = 0
    if 'counters' in user_info and 'clips_followers' in user_info['counters']:
        result['clips_followers'] = user_info['counters']['clips_followers']
    else:
        result['clips_followers'] = 0
    return result


def create_dataframe(user_info):
    result = clear_data(user_info)
    df = pd.DataFrame([result])
    # creating_date = get_registration_date(user_info['id'])
    # df['creating_date'] = creating_date #добавляем дату создания аккаунта
    return df


def parse_user_data(url):
    user_params = [
        'activities',  # 'деятельность'
        'about',  # 'о себе'
        'books',  # 'книги'
        'bdate',  # 'дата рождения'
        'career',  # 'карьера'
        'city',  # 'город'
        'education',  # 'образование'
        'followers_count',  # 'количество подписчиков'
        'has_photo',  # 'есть фото'
        'has_mobile',  # 'есть мобильный'
        'home_town',  # 'родной город'
        'sex',  # 'пол'
        'site',  # 'сайт'
        'schools',  # 'школы'
        'screen_name',  # 'имя на экране'
        'status',  # 'статус'
        'verified',  # 'подтвержденный'
        'games',  # 'игры'
        'interests',  # 'интересы'
        'last_seen',  # 'последний раз в сети'
        'maiden_name',  # 'девичья фамилия'
        'military',  # 'военная служба'
        'movies',  # 'фильмы'
        'music',  # 'музыка'
        'nickname',  # 'псевдоним'
        'occupation',  # 'род деятельности'
        'online',  # 'онлайн'
        'personal',  # 'личное'
        'quotes',  # 'цитаты'
        'relation',  # 'отношение'
        'relatives',  # 'родственники'
        'timezone',  # 'часовой пояс'
        'tv',  # 'телевидение'
        'universities',  # 'университеты'
        'is_verified',  # 'подтвержденный аккаунт'
        'contacts',
        'counters',
        'country'
    ]

    # user_name = url.split('/')[-1] 
    user_name = 194854409
    if type(user_params) == list:
        user_params = ', '.join(user_params)
    print(user_params)
    user_info = parse_data(user_name,user_params)
    user_id = user_info['id']
    print(user_info)
    data = clear_data(user_info=user_info)
    return data,user_id


if __name__ == "__main__":
    user_url = input('Введите url')
    print(parse_user_data(user_url))