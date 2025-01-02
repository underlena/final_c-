from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from prometheus_client import Counter, Histogram, start_http_server
import time
from models.database import SessionLocal, Notification, NotificationStatus
import aio_pika
import asyncio
import json
from typing import Optional
import logging

app = FastAPI()

# Метрики
notification_counter = Counter('notifications_total', 'Общее количество уведомлений', ['type'])

# Расширенные метрики
notification_latency = Histogram(
    'notification_processing_seconds',
    'Время обработки уведомлений',
    ['type']
)
notification_failures = Counter(
    'notification_failures_total',
    'Общее количество неудачных уведомлений',
    ['type']
)

# Безопасность
API_KEY_NAME = "X-API-Key"
API_KEY = "your-secure-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Could not validate API key"
        )
    return api_key

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class NotificationRequest(BaseModel):
    type: str
    recipient: str
    message: str
    metadata: Optional[dict] = None

async def send_to_queue(notification: dict, queue_name: str):
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()
    await channel.declare_queue(queue_name)
    
    message = aio_pika.Message(body=json.dumps(notification).encode())
    await channel.default_exchange.publish(message, routing_key=queue_name)
    
    await connection.close()

@app.post("/notify")
async def send_notification(
    notification: NotificationRequest,
    db = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    start_time = time.time()
    try:
        # Сохранение в базу данных
        db_notification = Notification(
            type=notification.type,
            recipient=notification.recipient,
            message=notification.message,
            metadata=notification.metadata,
            status=NotificationStatus.PENDING
        )
        db.add(db_notification)
        db.commit()

        # Отправка в очередь
        queue_name = f"{notification.type.lower()}_notifications"
        await send_to_queue(notification.dict(), queue_name)
        
        # Обновление метрик
        notification_counter.labels(type=notification.type).inc()
        notification_latency.labels(type=notification.type).observe(
            time.time() - start_time
        )
        
        return {"status": "успешно", "id": db_notification.id}
    except Exception as e:
        notification_failures.labels(type=notification.type).inc()
        logging.error(f"Ошибка отправки уведомления: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    start_http_server(8000)
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
