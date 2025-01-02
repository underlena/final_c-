# Notification System

## Компоненты
- Notification Gateway
- Email Service
- SMS Service
- Push Service
- PostgreSQL
- RabbitMQ
- Prometheus
- Grafana

## Требования
- Docker и Docker Compose
- Python 3.8+
- pip

## Docker Registry
```bash
# Сборка образов
docker-compose build
```

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd final_project
```

2. Создайте виртуальное окружение для тестов:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install pytest pytest-asyncio aio_pika fastapi[all] pytest-cov
```

4. Запустите сервисы:
```bash
docker-compose up -d
```

## Запуск тестов

Из корневой директории проекта выполните:

```bash
# Установка всех зависимостей
pip install -r requirements.txt

# Gateway тесты
pytest notification_gateway/tests/test_gateway.py -v
```

## Проверка работоспособности

1. Проверьте доступность RabbitMQ:
   - Откройте http://localhost:15672
   - Логин: guest
   - Пароль: guest

2. Отправьте тестовое уведомление:
```bash
curl -X POST http://localhost:8000/notify \
   -H "X-API-Key: your-secure-api-key" \
   -H "Content-Type: application/json" \
   -d '{
     "type": "email",
     "recipient": "test@example.com",
     "message": "Test notification",
     "metadata": {"priority": "high"}
   }'
```

## Мониторинг

- Метрики Prometheus доступны по адресу: http://localhost:8000/metrics
- Логи можно посмотреть командой: `docker-compose logs -f`
