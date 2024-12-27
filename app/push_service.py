import pika
from config import RABBITMQ_URL

def push_callback(ch, method, properties, body):
    recipient, message = body.decode().split('|')
    print(f"Sending push notification to {recipient}: {message}")
    # Здесь можно добавить логику отправки push-уведомлений
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_push_service():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='push')
    channel.basic_consume(queue='push', on_message_callback=push_callback)
    print("Push service is running...")
    channel.start_consuming()

if __name__ == '__main__':
    start_push_service()