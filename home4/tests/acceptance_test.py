import joblib
import pytest
from fastapi.testclient import TestClient
from api import app  # Импортируйте ваше FastAPI приложение

# Создаем тестовый клиент для API
client = TestClient(app)


# Загрузка модели для тестирования
def load_model():
    try:
        return joblib.load("model.pkl")
    except Exception as e:
        return None


model = load_model()


def test_api_accepts_valid_uid():
    """Тестируем API с валидным UID"""
    test_uid = "https://vk.com/id123456"  # Замените на валидный ID пользователя
    response = client.post("/predict/", json={"uid": test_uid})

    assert (
        response.status_code == 200
    ), "API должен вернуть статус 200 для валидного UID"
    assert "uid" in response.json(), "Ответ должен содержать 'uid'"
    assert "message" in response.json(), "Ответ должен содержать 'message'"
    assert "prediction" in response.json(), "Ответ должен содержать 'prediction'"
    assert "probability" in response.json(), "Ответ должен содержать 'probability'"


def test_api_rejects_invalid_uid():
    """Тестируем API с невалидным UID"""
    test_uid = "65643234"
    response = client.post("/predict/", json={"uid": test_uid})

    assert (
        response.status_code == 404
    ), "API должен вернуть статус 404 для невалидного UID"
    assert (
        "detail" in response.json()
    ), "Ответ должен содержать 'detail' с описанием ошибки"


def test_model_not_loaded():
    """Тестируем обработку ошибки, если модель не загружена"""
    global model
    original_model = model
    model = None  # Устанавливаем модель в None для теста

    test_uid = "https://vk.com/id123456"  # Замените на валидный ID пользователя
    response = client.post("/predict/", json={"uid": test_uid})

    assert (
        response.status_code == 500
    ), "API должен вернуть статус 500, если модель не загружена"
    assert (
        "detail" in response.json()
    ), "Ответ должен содержать 'detail' с описанием ошибки"

    model = original_model  # Восстанавливаем оригинальную модель


def test_health_check():
    """Тестируем проверку состояния API"""
    response = client.get("/health/")
    assert (
        response.status_code == 200
    ), "API должен вернуть статус 200 для проверки состояния"
    assert response.json() == {
        "status": "ok"
    }, "Ответ должен содержать {'status': 'ok'}"


# Запуск тестов
if __name__ == "__main__":
    pytest.main()
