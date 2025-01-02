import aio_pika
import asyncio
import json
import logging
from firebase_admin import messaging, credentials, initialize_app

# Initialize Firebase
cred = credentials.Certificate("firebase-config.json")
initialize_app(cred)

class PushNotificationService:
    MAX_RETRIES = 3
    
    @staticmethod
    async def send_push(token: str, title: str, body: str):
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token,
        )
        return messaging.send(message)

async def process_push(message, retry_count=0):
    try:
        data = json.loads(message.body.decode())
        await PushNotificationService.send_push(
            data['recipient'],
            data.get('title', 'Notification'),
            data['message']
        )
        logging.info(f"Push notification sent to {data['recipient']}")
    except Exception as e:
        logging.error(f"Error sending push: {str(e)}")
        if retry_count < PushNotificationService.MAX_RETRIES:
            await asyncio.sleep(2 ** retry_count)
            await process_push(message, retry_count + 1)
        else:
            logging.error("Max retries reached for push notification")

async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()
    queue = await channel.declare_queue("push_notifications")
    
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                await process_push(message)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
