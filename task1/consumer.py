import pika
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve user and password from environment variables
rabbitmq_user = os.getenv("RABBITMQ_USER")
rabbitmq_pass = os.getenv("RABBITMQ_PASS")

# Set up RabbitMQ connection
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials(rabbitmq_user, rabbitmq_pass))
)
channel = connection.channel()

# Define the queue name
queue_name = 'custom_queue'
channel.queue_declare(queue=queue_name)

# Counter for messages
message_count = 0

def callback(ch, method, properties, body):
    global message_count
    message_count += 1
    print(f"Received ({message_count}): {body.decode()}")

# Set up consumer
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

print("Waiting for messages. To exit, press CTRL+C")
channel.start_consuming()

