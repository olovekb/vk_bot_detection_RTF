from unittest.mock import patch
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_health_check():
    """Тест для эндпоинта /health."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "API is running"}

@patch('vk_parser.parse_user_data')
@patch('vk_parser.get_friends_ids')
@patch('get_graph_metrics.make_graph_for_user')
@patch('get_graph_metrics.get_graph_features')
@patch('model.predict')
def test_check_user(mock_predict, mock_get_graph_features, mock_make_graph_for_user, mock_get_friends_ids, mock_parse_user_data):
    """Тест для эндпоинта /check_user с мокированием внешних API."""
    
    # Мокаем возвращаемые значения функций
    mock_parse_user_data.return_value = ({"name": "Test User", "age": 25}, 12345)
    mock_get_friends_ids.return_value = ([67890, 54321], 2)
    mock_make_graph_for_user.return_value = "MockGraph"
    mock_get_graph_features.return_value = {
        "avg_cl": 0.5,
        "trans": 0.2,
        "average_neighbor_degree": 1.5,
        "average_degree_connectivity": 1.2,
        "degree_centrality": 0.8,
        "closeness_centrality": 0.7,
        "betweenness_centrality": 0.6,
        "diameter": 4,
    }
    mock_predict.return_value = {
        "prediction": 1,
        "probability": 0.85,
    }

    # Тестовые данные для запроса
    request_data = {"user_url": "https://vk.com/durov"}

    # Выполняем запрос к API
    response = client.post("/check_user", json=request_data)

    # Проверяем ответ
    assert response.status_code == 200
    assert response.json() == {
        "user_url": "https://vk.com/durov",
        "user_data": {
            "prediction": 1,
            "probability": 0.85,
        },
    }

    # Проверяем, что мокированные функции были вызваны
    mock_parse_user_data.assert_called_once_with("https://vk.com/durov")
    mock_get_friends_ids.assert_called_once_with(12345)
    mock_make_graph_for_user.assert_called_once()
    mock_get_graph_features.assert_called_once()
    mock_predict.assert_called_once()