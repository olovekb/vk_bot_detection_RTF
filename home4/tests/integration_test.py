import joblib
import pytest
from fastapi.testclient import TestClient
from api import app  # Импортируйте ваше FastAPI приложение

# Создаем тестовый клиент для API
client = TestClient(app)

# Загружаем модель для тестирования
model = joblib.load("model.pkl")


def test_model_loading():
    """Тестируем загрузку модели"""
    assert model is not None, "Модель не загружена"


def test_prediction_api_valid_user():
    """Тестируем API предсказания для валидного пользователя"""
    test_uid = (
        "https://vk.com/id123456"  # Замените на валидный ID или ссылку на пользователя
    )
    response = client.post("/predict/", json={"uid": test_uid})
    assert response.status_code == 200, "Ошибка в API предсказания"

    prediction = response.json()
    assert "uid" in prediction, "Отсутствует 'uid' в ответе"
    assert "message" in prediction, "Отсутствует 'message' в ответе"
    assert "prediction" in prediction, "Отсутствует 'prediction' в ответе"
    assert "probability" in prediction, "Отсутствует 'probability' в ответе"

    assert isinstance(
        prediction["prediction"], int
    ), "Предсказание должно быть целым числом"
    assert isinstance(
        prediction["probability"], float
    ), "Вероятность должна быть числом с плавающей точкой"


def test_prediction_api_invalid_user():
    """Тестируем API предсказания для невалидного пользователя"""
    test_uid = "invalid_user_id"
    response = client.post("/predict/", json={"uid": test_uid})
    assert (
        response.status_code == 404
    ), "Ожидался статус 404 для невалидного пользователя"


# Запуск тестов
if __name__ == "__main__":
    pytest.main()
