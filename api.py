from models import UserInfo
from fastapi import FastAPI
from pydantic import ValidationError
import uvicorn
from vk_parser import parse_user_data, get_friends_ids
from get_graph_metrics import make_graph_for_user, get_graph_features
import logging
from utils import create_df
from model import predict

app = FastAPI()

# Настроим логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

@app.get("/health")
async def health_check():
    return {"status": "API is running"}

@app.post("/check_user")
async def create_item(user: UserInfo):
    user_url = user.user_url
    user_data,user_id = parse_user_data(user_url)
    print(user_data)
    friends_ids, friends_count = get_friends_ids(user_id)
    if friends_count == 0:
        logger.warning(f"Профиль пользователя {user_url} закрыт или у него нет друзей.")
        return {'user_url': user_url, 'error': 'Профиль пользователя закрыт или у него нет друзей'}
    
    # Строим граф на основе данных о друзьях
    uid2friends = {user_id: friends_ids}
    user_graph = make_graph_for_user(user_id, uid2friends)
    # Расчёт метрик графа
    graph_features = get_graph_features(user_graph)
    combined_info = {**user_data, **graph_features}

    person_df = create_df(combined_info)
    data = predict(person_df)
    return {'user_url': user_url, 'user_data': data}

if __name__ == "__main__":  # Исправлено с "__api__" на "__main__"
    uvicorn.run(app, host="127.0.0.1", port=8000)
# @app.post("/predict")
# def predict(input_data: InputData):
#     # Выполнение предсказания
#     try:
#         data_dict ={
#                 'has_photo':input_data.has_photo ,                    
#                 'sex':input_data.sex ,                          
#                 'has_mobile':input_data.has_mobile ,                   
#                 'relation':input_data.relation ,                     
#                 'albums':input_data.albums ,                        
#                 'audios':input_data.audios ,                        
#                 'followers':input_data.followers ,                     
#                 'friends':input_data.friends ,                       
#                 'pages':input_data.pages ,                         
#                 'photos':input_data.photos ,                        
#                 'subscriptions':input_data.subscriptions ,                 
#                 'videos':input_data.videos ,                        
#                 'clips_followers':input_data.clips_followers ,               
#                 'age':input_data.age ,                           
#                 'city':input_data.city ,                          
#                 'country':input_data.country , 
#         }
#         prediction = <вызов нужной функции>(data_dict)
#         return {
#             "prediction":prediction
#         }  # Возвращаем предсказания в удобном формате
#     except ValidationError as e:
#         raise HTTPException(status_code=422, detail=e.errors())
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

