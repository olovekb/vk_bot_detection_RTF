import json
import joblib
import pytest
from fastapi.testclient import TestClient
from api import app  # Импортируйте ваше FastAPI приложение

# Создаем тестовый клиент для API
client = TestClient(app)

# Загружаем модель для тестирования
model = joblib.load("model.pkl")

# Загрузка тестовых данных
with open("test_data.json") as f:
    test_data = json.load(f)


@pytest.mark.parametrize("data", test_data)
def test_regression(data):
    """Тестируем предсказания модели на заранее определенных данных"""
    uid = data["uid"]
    expected_prediction = data["expected_prediction"]
    expected_probability = data["expected_probability"]

    response = client.post("/predict/", json={"uid": uid})
    assert response.status_code == 200, "Ошибка в API предсказания"

    prediction = response.json()
    assert (
        prediction["prediction"] == expected_prediction
    ), f"Ожидалось {expected_prediction}, но получено {prediction['prediction']}"
    assert (
        abs(prediction["probability"] - expected_probability) < 0.01
    ), f"Ожидалась вероятность {expected_probability}, но получена {prediction['probability']}"


# Запуск тестов
if __name__ == "__main__":
    pytest.main()
