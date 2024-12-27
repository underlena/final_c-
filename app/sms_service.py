import pika
from config import RABBITMQ_URL

def sms_callback(ch, method, properties, body):
    recipient, message = body.decode().split('|')
    print(f"Sending SMS to {recipient}: {message}")
    # Здесь можно добавить логику отправки SMS
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_sms_service():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='sms')
    channel.basic_consume(queue='sms', on_message_callback=sms_callback)
    print("SMS service is running...")
    channel.start_consuming()

if __name__ == '__main__':
    start_sms_service()