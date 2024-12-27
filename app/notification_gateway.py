import pika
from flask import Flask, request, jsonify
from db.models import init_db, Notification
from config import DB_URL, RABBITMQ_URL

app = Flask(__name__)
session = init_db(DB_URL)

def send_to_queue(channel, recipient, message):
    connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
    channel_mq = connection.channel()
    channel_mq.queue_declare(queue=channel)
    channel_mq.basic_publish(
        exchange='',
        routing_key=channel,
        body=f"{recipient}|{message}"
    )
    connection.close()

@app.route('/send', methods=['POST'])
def send_notification():
    data = request.json
    channel = data.get('channel')
    recipient = data.get('recipient')
    message = data.get('message')

    if not channel or not recipient or not message:
        return jsonify({"error": "Invalid request"}), 400

    # Сохранение уведомления в базе данных
    notification = Notification(channel=channel, recipient=recipient, message=message)
    session.add(notification)
    session.commit()

    # Отправка в очередь RabbitMQ
    send_to_queue(channel, recipient, message)

    return jsonify({"status": "Notification sent", "id": notification.id}), 200

if __name__ == '__main__':
    app.run(port=5000)