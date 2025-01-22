import unittest
from pydantic import BaseModel, ValidationError
import joblib
import pandas as pd
import random


# Определение модели входных данных
class InputData(BaseModel):
    has_photo: int
    sex: int
    has_mobile: float
    relation: int
    albums: float
    audios: float
    followers: float
    friends: float
    pages: float
    photos: float
    subscriptions: float
    videos: float
    clips_followers: float
    age: float
    city: float
    country: float
    avg_cl: float
    trans: float
    average_neighbor_degree: float
    average_degree_connectivity: float
    degree_centrality: float
    closeness_centrality: float
    betweenness_centrality: float
    diameter: float


# Загрузка модели
model = joblib.load("model.pkl")


def predict(input_data: InputData):
    data_dict = input_data.model_dump()
    df = pd.DataFrame([data_dict])
    prediction = model.predict(df)[0]
    probability = model.predict_proba(df)[0][prediction]
    return {"prediction": prediction, "probability": probability}


class TestDataProcessing(unittest.TestCase):

    def setUp(self):
        """Подготовка корректных и некорректных данных для тестирования"""
        # Генерируем валидные данные
        self.valid_data = self.generate_valid_data()

        # Генерируем некорректные данные
        self.invalid_data = self.valid_data.copy()
        self.invalid_data["has_mobile"] = "not_a_float"  # Некорректный тип

    def generate_valid_data(self):
        """Генерация валидных данных, включая все необходимые поля"""
        return {
            "has_photo": random.choice([0, 1]),
            "sex": random.choice([0, 1]),  # 0 - женский, 1 - мужской
            "has_mobile": random.uniform(0, 1),
            "relation": random.randint(0, 6),
            "albums": random.uniform(0, 20),
            "audios": random.uniform(0, 1000),
            "followers": random.uniform(0, 5000),
            "friends": random.uniform(0, 2000),
            "pages": random.uniform(0, 100),
            "photos": random.uniform(0, 500),
            "subscriptions": random.uniform(0, 100),
            "videos": random.uniform(0, 200),
            "clips_followers": random.uniform(0, 100),
            "age": random.randint(0, 100),  # Возраст от 0 до 100
            "city": random.uniform(0, 100),  # Примерный диапазон для города
            "country": random.uniform(0, 100),  # Примерный диапазон для страны
            "avg_cl": random.uniform(0, 1),  # Примерные значения
            "trans": random.uniform(0, 1),
            "average_neighbor_degree": random.uniform(0, 1),
            "average_degree_connectivity": random.uniform(0, 1),
            "degree_centrality": random.uniform(0, 1),
            "closeness_centrality": random.uniform(0, 1),
            "betweenness_centrality": random.uniform(0, 1),
            "diameter": random.uniform(0, 10),
        }

    def test_valid_input_data(self):
        """Тестирование корректного ввода данных"""
        input_data = InputData(**self.valid_data)
        self.assertEqual(input_data.has_photo, self.valid_data["has_photo"])

    def test_invalid_input_data(self):
        """Тестирование некорректного ввода данных"""
        with self.assertRaises(ValidationError):
            InputData(**self.invalid_data)

    def test_predict(self):
        """Тест предсказательной функции"""
        input_data = InputData(**self.valid_data)
        result = predict(input_data)

        # Проверяем структуру результата
        self.assertIsInstance(result, dict)
        self.assertIn("prediction", result)
        self.assertIn("probability", result)

        # Преобразуем np.int64 в int для проверки
        prediction_int = int(result["prediction"])

        # Проверяем типы данных
        self.assertIsInstance(prediction_int, int)
        self.assertIsInstance(result["probability"], float)

        # Проверяем диапазоны значений
        self.assertIn(prediction_int, [0, 1])
        self.assertTrue(0 <= result["probability"] <= 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
