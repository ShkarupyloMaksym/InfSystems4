import pika
import os
import argparse
from dotenv import load_dotenv

# Завантаження змінних середовища з .env файлу (якщо потрібно)
load_dotenv()

# Отримання користувача та пароля з .env файлу
rabbitmq_user = os.getenv("RABBITMQ_USER", "user")
rabbitmq_pass = os.getenv("RABBITMQ_PASS", "password")

# Парсинг аргументів командного рядка
parser = argparse.ArgumentParser(description="RabbitMQ Consumer for specific day of the week")
parser.add_argument(
    "--day", 
    type=str, 
    default="all", 
    choices=["all", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
    help="Specify the day of the week to consume messages for (default: all days)"
)
args = parser.parse_args()
day_of_week = args.day

# Встановлення підключення до RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials(rabbitmq_user, rabbitmq_pass))
)
channel = connection.channel()

# Назва обмінника та його оголошення
exchange_name = 'day_exchange'
channel.exchange_declare(exchange=exchange_name, exchange_type='direct')

# Функція для обробки отриманих повідомлень
def callback(ch, method, properties, body):
    print(f"Received in {method.routing_key}: {body.decode()}")

# Якщо вказано конкретний день, прив'язка тільки для нього
if day_of_week != "all":
    queue_name = f"{day_of_week}_queue"
    channel.queue_declare(queue=queue_name)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=day_of_week)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print(f"Waiting for messages for {day_of_week}. To exit, press CTRL+C")

# Якщо обрано "all", прив'язка для всіх днів тижня
else:
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days_of_week:
        queue_name = f"{day}_queue"
        channel.queue_declare(queue=queue_name)
        channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=day)
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    print("Waiting for messages for all days. To exit, press CTRL+C")

# Запуск отримання повідомлень
channel.start_consuming()

