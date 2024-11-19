import pika
import os
import random
from dotenv import load_dotenv

# Завантаження змінних середовища з .env файлу
load_dotenv()

# Отримання користувача та пароля з .env файлу
rabbitmq_user = os.getenv("RABBITMQ_USER")
rabbitmq_pass = os.getenv("RABBITMQ_PASS")

# Встановлення підключення до RabbitMQ
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials(rabbitmq_user, rabbitmq_pass))
)
channel = connection.channel()

# Оголошення обмінника типу topic
exchange_name = 'social_media_exchange'
channel.exchange_declare(exchange=exchange_name, exchange_type='topic')

# Список користувачів та дій
user_ids = ['user1', 'user2', 'user3']
actions = ['create', 'update', 'delete']

# Відправлення повідомлень для кожного користувача з випадковою дією
for _ in range(15):  # Надсилаємо 15 повідомлень
    user_id = random.choice(user_ids)
    action = random.choice(actions)
    routing_key = f"post.{user_id}.{action}"
    message = f"Action {action} performed by {user_id}"
    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message)
    print(f"Sent to {routing_key}: {message}")

connection.close()

