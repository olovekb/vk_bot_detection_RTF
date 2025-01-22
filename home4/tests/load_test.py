from locust import HttpUser, TaskSet, task, between
import json


class UserActions(TaskSet):
    @task
    def predict_user(self):
        # Замените на валидный ID пользователя или ссылку
        uid = "https://vk.com/id123456"
        response = self.client.post("/predict/", json={"uid": uid})
        print(
            f"Response status: {response.status_code}, Response body: {response.text}"
        )


class WebsiteUser(HttpUser):
    tasks = [UserActions]
    wait_time = between(1, 2)  # Время ожидания между запросами
