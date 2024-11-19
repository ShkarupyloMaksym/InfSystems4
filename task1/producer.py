import pika
import time
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

# Custom message content
message_text = "do u play chess?"

# Send messages with a different interval
for i in range(15):
    message = f"{message_text} {i+1}"
    channel.basic_publish(exchange='', routing_key=queue_name, body=message)
    print(f"Sent: {message}")
    time.sleep(2)  # New interval in seconds

connection.close()

