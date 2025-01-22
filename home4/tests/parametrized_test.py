import joblib
import pytest
from fastapi.testclient import TestClient
from api import app  # Импортируйте ваше FastAPI приложение

# Создаем тестовый клиент для API
client = TestClient(app)

# Загружаем модель для тестирования
model = joblib.load("model.pkl")


@pytest.mark.parametrize(
    "uid, expected_status",
    [
        ("https://vk.com/id123456", 200),  # Валидный UID
        ("invalid_user_id", 404),  # Невалидный UID
        ("", 422),  # Пустой UID (ошибка валидации)
        ("https://vk.com/some_nonexistent_user", 404),  # Не существующий пользователь
    ],
)
def test_predict_api(uid, expected_status):
    """Проверяем API предсказания с разными входными данными."""
    response = client.post("/predict/", json={"uid": uid})
    assert (
        response.status_code == expected_status
    ), f"Ожидался статус {expected_status} для UID: {uid}"


@pytest.mark.parametrize(
    "uid",
    [
        ("123456"),  # Числовой UID
        ("abcdef"),  # Текстовый UID
        ("!@#$%^&*()"),  # Специальные символы
    ],
)
def test_predict_api_invalid_data(uid):
    """Проверяем API предсказания с невалидными данными."""
    response = client.post("/predict/", json={"uid": uid})
    assert response.status_code == 404, f"Ожидался статус 404 для UID: {uid}"


# Запуск тестов
if __name__ == "__main__":
    pytest.main()
