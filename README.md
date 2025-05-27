# Django Backend Service

Тестовое задание для загрузки фотографий c задержкой в 20 секунд.

## Стэк

- Django 5.2
- PostgreSQL 15
- Redis 7
- Celery
- Flower
- Grafana
- Prometheus
- Docker
- Poetry

## Запуск

1. Создайте свой `.env` в корне проекта:

```env
CELERY_BROKER_URL=redis://redis:6379/0

TELEGRAM_CHAT_ID=your_telegram_chat_id (можно узнать у бота @getmyid_bot)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token (создайте своего бота в @BotFather, и вставьте в .env его токен)

POSTGRES_DB=your_database_name
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=your_database_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
```

2. Соберите и запустите контейнеры:

```bash
docker compose up --build
```

3. После запуска сервисы будут доступны по адресам:

* Django API: [http://localhost:8000](http://localhost:8000)
* Flower: [http://localhost:5555](http://localhost:5555)
* Grafana: [http://localhost:3000](http://localhost:3000)
* Prometheus: [http://localhost:9090](http://localhost:9090)

4. Для запуска тестов:

```bash
docker compose exec web pytest
```