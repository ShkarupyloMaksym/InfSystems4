import pika
import os
import random
from dotenv import load_dotenv

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

# Define the exchange and queues for each day of the week
exchange_name = 'day_exchange'
days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# Declare a direct exchange
channel.exchange_declare(exchange=exchange_name, exchange_type='direct')

# List of messages with associated days
messages = [
    ("Monday", "Monday Opening: Start the week with a King's Gambit!"),
    ("Monday", "Chess Fact: In 1834, La Bourdonnais and McDonnell played a famous match."),
    ("Tuesday", "Tuesday Puzzle: Find the best move for Black in a middlegame position!"),
    ("Tuesday", "Today is perfect for learning the Sicilian Defense!"),
    ("Wednesday", "Midweek Wednesday: Test your endgame skills!"),
    ("Wednesday", "Unique midweek tip: Sacrifice a pawn to launch a king attack!"),
    ("Thursday", "Combination Thursday: Are you ready to find a tactical blow?"),
    ("Thursday", "Fischer said, 'Play chess like math.' Time to think through every move!"),
    ("Friday", "Friday is Defense Day. Master the Caro-Kann Defense!"),
    ("Friday", "Prepare for the weekend: Analyze your lost games."),
    ("Saturday", "Saturday Game: Time for free improvisation on the board!"),
    ("Saturday", "Play with style: Try the Queen's Gambit in your Saturday matches."),
    ("Sunday", "Sunday rest? No! Play a blitz tournament with friends."),
    ("Sunday", "Today is for classics: Review Kasparov's games!"),
    ("Random", "Today is your day: Challenge accepted, you're the grandmaster of your week!"),
    ("Random", "Perfect chess advice: When in doubt, castle short."),
    ("Random", "Are you ready for your next move? Add a bit of drama to the game!")
]

# Send random messages to the appropriate queue
for _ in range(17):  # Send 17 messages
    day, message = random.choice(messages)
    routing_key = day if day != "Random" else random.choice(days_of_week)
    channel.basic_publish(exchange=exchange_name, routing_key=routing_key, body=message)
    print(f"Sent to {routing_key}: {message}")

connection.close()

