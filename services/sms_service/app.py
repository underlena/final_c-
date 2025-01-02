import aio_pika
import asyncio
import json
import logging

async def process_sms(message):
    try:
        data = json.loads(message.body.decode())
        logging.info(f"Отправка SMS для {data['recipient']}: {data['message']}")
    except Exception as e:
        logging.error(f"Ошибка обработки SMS: {str(e)}")

async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()
    queue = await channel.declare_queue("sms_notifications")
    
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                await process_sms(message)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
