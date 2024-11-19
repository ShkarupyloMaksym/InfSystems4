import pika
import os
import unittest
import time
from dotenv import load_dotenv

# Завантаження змінних середовища з .env файлу
load_dotenv()

# Отримання користувача та пароля з .env файлу
rabbitmq_user = os.getenv("RABBITMQ_USER")
rabbitmq_pass = os.getenv("RABBITMQ_PASS")

# Параметри RabbitMQ
exchange_name = 'social_media_exchange'
user_ids = ['user1', 'user2', 'user3']
actions = ['create', 'update', 'delete']
received_messages = {user_id: [] for user_id in user_ids}

class RabbitMQSetupTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Встановлення підключення до RabbitMQ
        cls.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials(rabbitmq_user, rabbitmq_pass))
        )
        cls.channel = cls.connection.channel()
        
        # Оголошення обмінника
        cls.channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
        
        # Оголошення черг та прив'язка до обмінника для кожного користувача
        for user_id in user_ids:
            queue_name = f"{user_id}_activity_queue"
            cls.channel.queue_declare(queue=queue_name)
            cls.channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=f"post.{user_id}.*")

    @classmethod
    def tearDownClass(cls):
        # Видалення обмінника та черг
        cls.channel.exchange_delete(exchange=exchange_name)
        for user_id in user_ids:
            queue_name = f"{user_id}_activity_queue"
            cls.channel.queue_delete(queue=queue_name)
        cls.connection.close()

    def test_message_routing(self):
        # Надсилання тестових повідомлень для кожного користувача та дії
        for user_id in user_ids:
            for action in actions:
                routing_key = f"post.{user_id}.{action}"
                test_message = f"Test message for {user_id} action {action}"
                self.channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=test_message)
        
        # Запуск споживачів з обмеженням на кількість повідомлень
        self.start_consumers(expected_messages=len(user_ids) * len(actions))

        # Перевірка, що кожна черга отримала відповідні повідомлення
        for user_id in user_ids:
            with self.subTest(user_id=user_id):
                self.assertTrue(len(received_messages[user_id]) >= 1)

    def start_consumers(self, expected_messages):
        # Встановлення нового підключення для споживачів
        consumer_connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials(rabbitmq_user, rabbitmq_pass))
        )
        consumer_channel = consumer_connection.channel()

        # Лічильник отриманих повідомлень
        total_received = 0

        # Функція для обробки отриманих повідомлень
        def callback(ch, method, properties, body):
            nonlocal total_received
            user_id = method.routing_key.split('.')[1]
            received_messages[user_id].append(body.decode())
            total_received += 1
            # Перевірка, чи всі очікувані повідомлення отримано
            if total_received >= expected_messages:
                consumer_channel.stop_consuming()

        # Оголошення споживачів для кожного користувача
        for user_id in user_ids:
            queue_name = f"{user_id}_activity_queue"
            consumer_channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        
        # Початок отримання повідомлень з тайм-аутом
        try:
            consumer_channel.start_consuming()
        except KeyboardInterrupt:
            pass  # Дозволяє зупинити цикл вручну, якщо необхідно

        # Закриття споживача після завершення отримання повідомлень
        consumer_connection.close()

if __name__ == '__main__':
    unittest.main()

