# Ссылка для получения ключа: https://dev.vk.com/ru/api/access-token/getting-started
# 
# Ссылка для создания приложения для получения токена: https://dev.vk.com/ru
# 
# Статья о том как токен получать: https://smmplanner.com/blog/gaid-po-api-vk-kak-podkliuchit-i-ispolzovat/

import os
import json

import requests
import pandas as pd
from dotenv import load_dotenv
load_dotenv()


# Params
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

required_fileds = [
    'has_photo',
    'sex',
    'has_mobile',
    'mobile_phone',
    'home_phone',
    'relatives',
    'relation',
    'personal',
    'activities',
    'music',
    'movies',
    'tv',
    'books',
    'about', 
    'quotes',
    'albums', #included
    'audios', #included
    'followers', #included
    'friends', #included
    'pages', #included
    'photos', #included
    'subscriptions', #included
    'videos', #included
    'city',
    'country'
]
# age - такого параметра нет

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


# Parser Core
# Получение даты регистрации аккаунта (спорный метод)
def get_registration_date(id):
    url = f'https://vk.com/foaf.php?id={id}'

    response = requests.get(url)
    if response.status_code == 200:
        for line in response.text.split('\n'):
            if 'ya:created' in line:
                return line.split('=')[1].split('T')[0].replace('"','')
    return None

# Проверка на наличие папки для сохранения данных
def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Directory '{directory_path}' created.")
    else:
        print(f"Directory '{directory_path}' already exists.")

    return directory_path
    

# сохранение данных в json
def save_dict_to_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4,ensure_ascii=False)
        print(f"Dictionary saved to '{filepath}'.")

    return filepath


# функция отправки запрсоа
def send_request(method, params):
    url = "https://api.vk.com/method/" + method

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    return None

# функция получения информации о пользователе
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

# функция получения подписчиков пользователя
def get_user_followers(user_id, access_token, result='amount', **followers_data):
    """
    Fetches the followers of a user from an API.

    Args:
        user_id (str): The ID or screen name of the user whose followers are to be fetched.
        access_token (str): The access token for API authentication.
        result (str, optional): Specifies the type of result to return. 
                                Can be 'amount' to return the number of followers 
                                or 'data' to return the full response data. 
                                Defaults to 'amount'.
        **followers_data: Additional parameters for fetching followers information.
                          - get_followers_info (bool): If True, fetch additional follower info.
                          - followers_params (str): Comma-separated list of fields to retrieve.
                          - get_all_followers (bool): If True, fetch all followers.

    Returns:
        int or dict: 
            - If result is 'amount', returns the number of followers as an integer.
            - If result is 'data', returns the full response data as a dictionary.

    Raises:
        ValueError: If an invalid result type is specified.
    """
    
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
    """
    Fetches the subscription data for a user from an external API.

    This function retrieves the number of followers (subscriptions) for a specified user
    using the provided user ID and access token. It can return either the total count of 
    followers or detailed subscription data based on the parameters provided.

    Parameters:
    - user_id (str or int): The unique identifier of the user whose subscriptions are to be fetched.
    - access_token (str): The access token required for authentication with the API.
    - result (str, optional): Specifies the type of result to return. 
      - 'amount' (default): Returns the count of followers.
      - 'data': Returns detailed subscription data.
    - **subscriptions_data (dict, optional): Additional parameters for fetching subscription data.
      - 'extended' (bool): If set to True, requests extended information about the subscriptions.
      - 'amount_type' (str, optional): Specifies whether to return the count of 'users' or 'groups'.

    Returns:
    - int: If result is 'amount', returns the count of followers based on the specified amount_type.
    - dict: If result is 'data', returns the complete response containing subscription details.
    """
    
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

# функция получения данных
def parse_data(user_name,save = False):
    token = os.getenv('VK_OAUTH_TOKEN')
    access_token = token  
    user_info = get_user_info(user_name, access_token,user_params)
    if 'error' in user_info.keys():
        print('Error')
        print('Data:',user_info)
    else:
        user_id = user_info['id']
        if save:
            filepath = ensure_directory_exists(f"Data/{user_id}")
            save_dict_to_json(user_info, f'{filepath}/userinfo.json')
    return user_info


# Create Table Module
# Функция проверки значния
def is_not_empty(value):
    return value not in ["", [], {}] and value is not None


# функция создания датафрейма
def create_dataframe(user_info):
    result = {}
    for param in required_fileds:
        if param in user_info.keys():
            result[param] = is_not_empty(user_info[param])
        elif param in included_params and param in user_info['counters']:
            result[param] = user_info['counters'][param]
        else:
            result[param] = None
    df = pd.DataFrame([result])
    creating_date = get_registration_date(user_info['id'])
    df['creating_date'] = creating_date #добавляем дату создания аккаунта

    return df


if __name__ == "__main__":
    user_name = input('Enter user url').split('/')[-1] 
    if type(user_params) == list:
        user_params = ', '.join(user_params)
    print(user_params)
    user_info = parse_data(user_name)
    print(user_info)
    df = create_dataframe(user_info=user_info,)
    # df.to_excel('test.xlsx')