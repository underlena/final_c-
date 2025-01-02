import aio_pika
import asyncio
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import ssl
from config import settings

class EmailSender:
    def __init__(self):
        self.smtp_host = settings.EMAIL_SMTP_HOST
        self.smtp_port = settings.EMAIL_SMTP_PORT
        self.username = settings.EMAIL_USER
        self.password = settings.EMAIL_PASS
        self.max_retries = 3

    async def send_email(self, to_email: str, subject: str, message: str) -> bool:
        for attempt in range(self.max_retries):
            try:
                # Создаем сообщение
                msg = MIMEMultipart()
                msg['From'] = self.username
                msg['To'] = to_email
                msg['Subject'] = subject

                # Добавляем тело сообщения
                msg.attach(MIMEText(message, 'plain'))

                # Создаем защищенное SSL соединение
                context = ssl.create_default_context()
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls(context=context)
                    server.login(self.username, self.password)
                    server.send_message(msg)
                
                logging.info(f"Email успешно отправлен на {to_email}")
                return True
                
            except Exception as e:
                logging.error(f"Попытка {attempt + 1} отправки email не удалась: {str(e)}")
                if attempt == self.max_retries - 1:
                    logging.error(f"Достигнуто максимальное количество попыток для {to_email}")
                    return False
                await asyncio.sleep(2 ** attempt)  # Экспоненциальная задержка

email_sender = EmailSender()

async def process_email(message):
    try:
        data = json.loads(message.body.decode())
        subject = data.get('subject', 'Уведомление')
        success = await email_sender.send_email(
            to_email=data['recipient'],
            subject=subject,
            message=data['message']
        )
        
        if not success:
            raise Exception("Failed to send email after all retries")
            
    except Exception as e:
        logging.error(f"Ошибка обработки email: {str(e)}")
        # Можно добавить логику для сохранения неудачных попыток в базу данных
        raise

async def main():
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq/")
    channel = await connection.channel()
    queue = await channel.declare_queue("email_notifications")
    
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                await process_email(message)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
