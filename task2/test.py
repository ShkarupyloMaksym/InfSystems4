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
exchange_name = 'test_day_exchange'
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
received_messages = {day: [] for day in days_of_week}  # Збереження отриманих повідомлень


class RabbitMQSetupTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Встановлення підключення до RabbitMQ
        cls.connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials(rabbitmq_user, rabbitmq_pass))
        )
        cls.channel = cls.connection.channel()
        
        # Оголошення обмінника
        cls.channel.exchange_declare(exchange=exchange_name, exchange_type='direct')
        
        # Оголошення черг та зв'язування їх з обмінником
        for day in days_of_week:
            cls.channel.queue_declare(queue=day)
            cls.channel.queue_bind(exchange=exchange_name, queue=day, routing_key=day)

    @classmethod
    def tearDownClass(cls):
        # Закриття підключення до RabbitMQ
        cls.channel.exchange_delete(exchange=exchange_name)
        for day in days_of_week:
            cls.channel.queue_delete(queue=day)
        cls.connection.close()

    def test_message_routing(self):
        # Надсилання тестових повідомлень
        for day in days_of_week:
            test_message = f"Test message for {day}"
            self.channel.basic_publish(exchange=exchange_name, routing_key=day, body=test_message)
        
        # Запуск споживачів для кожного дня
        self.start_consumers()

        # Затримка для отримання всіх повідомлень
        time.sleep(2)

        # Перевірка, що кожна черга отримала лише своє повідомлення
        for day in days_of_week:
            with self.subTest(day=day):
                self.assertEqual(len(received_messages[day]), 1)
                self.assertEqual(received_messages[day][0], f"Test message for {day}")

    def start_consumers(self):
        # Встановлення нового підключення для споживачів
        consumer_connection = pika.BlockingConnection(
            pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials(rabbitmq_user, rabbitmq_pass))
        )
        consumer_channel = consumer_connection.channel()

        # Функція для обробки отриманих повідомлень
        def callback(ch, method, properties, body):
            received_messages[method.routing_key].append(body.decode())

        # Оголошення споживачів для кожної черги
        for day in days_of_week:
            consumer_channel.basic_consume(queue=day, on_message_callback=callback, auto_ack=True)

        # Запуск отримання повідомлень
        consumer_channel.start_consuming()


if __name__ == '__main__':
    # Run tests and capture results
    result = unittest.TextTestRunner().run(unittest.makeSuite(RabbitMQSetupTest))
    
    # Display test summary
    if result.wasSuccessful():
        print("\nAll tests passed.")
    else:
        print("\nSome tests failed.")
    
    # Show details of each test case result
    for test, _ in result.failures:
        print(f"{test}: Test Failed")
    for test, _ in result.errors:
        print(f"{test}: Test Encountered an Error")
    for test in result.testsRun - len(result.failures) - len(result.errors):
        print(f"{test}: Test Passed")

