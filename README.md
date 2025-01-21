# vk_bot_detection_RTF

## FastApi app vk_bot_detection_RTF

## Описание

Web приложение на FastApi предназначенное для прогнозирования вероятности того, что пользователь является ботом

## API Endpoints

На данный момент реализован один endpoint `check_user`, который принимает следующие параметры:

```python
{'user_url':<ссылка на пользователя ВК>}
```


## Запуск

Для работы необходимо:

1. Создать виртуальное окружение

    Для Windows:

    ```bash
    python -m venv venv
    ```

    Для Linux/MacOS:

    ```bash
    python3 -m venv venv
    ```

2. Активация окружения

    Для Windows:

    ```bash
    .venv\Script\activate
    ```

    Для Linux/MacOS:

    ```bash
    .venv\Script\activate
    ```

3. Установка необходимых библиотек (команды необходимо выполнять в виртуальном окружении)

    ```bash
    pip install -r /path/to/requirements.txt
    ```

4. Необходимо создать файл .env и сохранить в него токен для обращения к API VK:

    ```env
    VK_OAUTH_TOKEN = ''
    ```

5. Для запуска модуля по парсингу данных необходимо запустить vk_parser.

    Для Windows:

    ```bash
    uvicorn api:app --reload
    ```

    Для Linux/MacOS:

    ```bash
    uvicorn api:app --reload
    ```