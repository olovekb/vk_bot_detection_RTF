import joblib
from utils import create_df


# Загрузка модели
def load_model():
    model = joblib.load('model.pkl')
    return model
        

# Предсказание
def predict(user_data:dict) ->dict:
    # Загружаем модель при старте приложения
    print(user_data)
    model = load_model()
    prediction = model.predict(user_data)[0]
    probability = model.predict_proba(user_data)[0][1]
    return {
            "prediction": int(prediction),
            "probability": float(probability)
        }


if __name__ == '__main__':
    user_data = {}
    predict(user_data)