import pandas as pd
import logging


# Конфигурация логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



def create_df(user_data:dict)->pd.DataFrame:
    # Создание DataFrame для модели
    person_df = pd.DataFrame({k: [v] for k, v in user_data.items()})
    person_df.fillna(0, inplace=True)
    return person_df
