# Use the official RabbitMQ image from Docker Hub
FROM rabbitmq:3.11-management

# Expose the necessary ports
# 5672 is for RabbitMQ clients, and 15672 is for RabbitMQ Management UI
EXPOSE 5672 15672

# Set environment variables (optional) to define default user and password
ENV RABBITMQ_DEFAULT_USER=user
ENV RABBITMQ_DEFAULT_PASS=password

# Start RabbitMQ server
CMD ["rabbitmq-server"]

