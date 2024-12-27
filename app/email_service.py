import pika
from config import RABBITMQ_URL

def email_callback(ch, method, properties, body):
    recipient, message = body.decode().split('|')
    print(f"Sending email to {recipient}: {message}")
    # Здесь можно добавить логику отправки email
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_email_service():
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel = connection.channel()
    channel.queue_declare(queue='email')
    channel.basic_consume(queue='email', on_message_callback=email_callback)
    print("Email service is running...")
    channel.start_consuming()

if __name__ == '__main__':
    start_email_service()