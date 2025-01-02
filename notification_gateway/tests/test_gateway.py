import pytest
import aio_pika
import asyncio
from typing import AsyncGenerator
import json

@pytest.fixture
async def rabbitmq_connection() -> AsyncGenerator[aio_pika.Connection, None]:
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    yield connection
    await connection.close()

@pytest.fixture
async def rabbitmq_channel(rabbitmq_connection) -> AsyncGenerator[aio_pika.Channel, None]:
    channel = await rabbitmq_connection.channel()
    
    # Удаляем очередь, если она существует
    try:
        await channel.queue_delete("email_notifications")
    except Exception:
        pass  # Игнорируем ошибку, если очередь не существует
        
    yield channel
    
    # Очистка после теста
    try:
        await channel.queue_delete("email_notifications")
    except Exception:
        pass
        
    await channel.close()

@pytest.mark.asyncio
async def test_notification_flow(rabbitmq_channel):
    # Создаем новую очередь с нужными параметрами
    queue = await rabbitmq_channel.declare_queue(
        "email_notifications",
        durable=False,        # Очередь не сохраняется после перезапуска
        auto_delete=True,     # Удаляется когда последний подписчик отключается
        exclusive=False       # Не эксклюзивная
    )
    
    # Подготавливаем тестовое сообщение
    test_message = {
        "type": "email",
        "recipient": "test@example.com",
        "message": "Test notification"
    }

    # Отправляем сообщение
    await rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(test_message).encode(),
            delivery_mode=aio_pika.DeliveryMode.NOT_PERSISTENT
        ),
        routing_key="email_notifications"
    )

    # Добавляем небольшую задержку
    await asyncio.sleep(0.1)

    # Проверяем получение сообщения
    message = await queue.get(timeout=1)
    assert message is not None
    
    # Подтверждаем получение сообщения
    await message.ack()
    
    # Проверяем содержимое сообщения
    received_data = json.loads(message.body.decode())
    assert received_data["type"] == "email"
    assert received_data["recipient"] == "test@example.com"

@pytest.mark.asyncio
async def test_sms_notification_flow(rabbitmq_channel):
    queue = await rabbitmq_channel.declare_queue(
        "sms_notifications",
        durable=False,
        auto_delete=True
    )
    
    test_message = {
        "type": "sms",
        "recipient": "+1234567890",
        "message": "Test SMS"
    }

    await rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(test_message).encode(),
            delivery_mode=aio_pika.DeliveryMode.NOT_PERSISTENT
        ),
        routing_key="sms_notifications"
    )

    await asyncio.sleep(0.1)
    message = await queue.get(timeout=1)
    assert message is not None
    await message.ack()
    
    received_data = json.loads(message.body.decode())
    assert received_data["type"] == "sms"
    assert received_data["recipient"] == "+1234567890"

@pytest.mark.asyncio
async def test_push_notification_flow(rabbitmq_channel):
    queue = await rabbitmq_channel.declare_queue(
        "push_notifications",
        durable=False,
        auto_delete=True
    )
    
    test_message = {
        "type": "push",
        "recipient": "device_token_123",
        "message": "Test Push",
        "title": "Test Title"
    }

    await rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps(test_message).encode(),
            delivery_mode=aio_pika.DeliveryMode.NOT_PERSISTENT
        ),
        routing_key="push_notifications"
    )

    await asyncio.sleep(0.1)
    message = await queue.get(timeout=1)
    assert message is not None
    await message.ack()
    
    received_data = json.loads(message.body.decode())
    assert received_data["type"] == "push"
    assert received_data["title"] == "Test Title"

@pytest.mark.asyncio
async def test_invalid_message_format(rabbitmq_channel):
    queue = await rabbitmq_channel.declare_queue(
        "email_notifications",
        durable=False,
        auto_delete=True
    )
    
    # Отправляем некорректное сообщение
    await rabbitmq_channel.default_exchange.publish(
        aio_pika.Message(
            body=b"invalid json",
            delivery_mode=aio_pika.DeliveryMode.NOT_PERSISTENT
        ),
        routing_key="email_notifications"
    )

    await asyncio.sleep(0.1)
    message = await queue.get(timeout=1)
    assert message is not None
    # Проверяем что сообщение не обработано успешно
    with pytest.raises(json.JSONDecodeError):
        json.loads(message.body.decode())