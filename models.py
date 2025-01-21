from pydantic import BaseModel
from typing import Optional


class UserInfo(BaseModel):
    user_url : str

# Определение модели входных данных
class InputData(BaseModel):
    has_photo : int                    
    sex : int                          
    has_mobile : float                   
    relation : int                     
    albums : float                        
    audios : float                        
    followers : float                     
    friends : float                       
    pages : float                         
    photos : float                        
    subscriptions : float                 
    videos : float                        
    clips_followers : float               
    age : float                           
    city : float                          
    country : float 