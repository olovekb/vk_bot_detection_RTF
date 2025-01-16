from .config import HOST, PORT

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn


app = FastAPI()


class UserInfo(BaseModel):
    user_url : str

@app.post("/check_user")
def create_item(user: UserInfo):
    user_url = user.user_url
    data = <вызов нужной функции>(user_url)
    return {'user_url':user_url, 'user_data':data}


if __name__ == "__main__":
    if HOST is None:
        uvicorn.run(app, host="127.0.0.1", port=8000)