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
parser = argparse.ArgumentParser(description="RabbitMQ Consumer for specific or all user activities")
parser.add_argument(
    "--user_id", 
    type=str, 
    default="all",
    help="Specify the user ID to consume messages for. Defaults to all users."
)
args = parser.parse_args()
user_id = args.user_id

# Встановлення підключення до RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials(rabbitmq_user, rabbitmq_pass))
)
channel = connection.channel()

# Назва обмінника та його оголошення
exchange_name = 'social_media_exchange'
channel.exchange_declare(exchange=exchange_name, exchange_type='topic')

# Визначення черги та шаблону ключа маршрутизації залежно від вказаного користувача
if user_id == "all":
    queue_name = "all_users_activity_queue"
    routing_key = "post.*.*"  # Всі дії для всіх користувачів
else:
    queue_name = f"{user_id}_activity_queue"
    routing_key = f"post.{user_id}.*"  # Всі дії для конкретного користувача

# Оголошення черги та прив'язка до обмінника з відповідним ключем маршрутизації
channel.queue_declare(queue=queue_name)
channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

# Функція для обробки отриманих повідомлень
def callback(ch, method, properties, body):
    routing_parts = method.routing_key.split('.')
    target_user = routing_parts[1]  # Ідентифікатор користувача
    action = routing_parts[2]       # Дія (create, update, delete)
    print(f"Received {action} action for {target_user}: {body.decode()}")

# Налаштування споживача для черги
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

# Повідомлення про те, який тип повідомлень буде отримувати консьюмер
if user_id == "all":
    print("Waiting for messages for all users. To exit, press CTRL+C")
else:
    print(f"Waiting for messages for user {user_id}. To exit, press CTRL+C")

# Запуск отримання повідомлень
channel.start_consuming()

