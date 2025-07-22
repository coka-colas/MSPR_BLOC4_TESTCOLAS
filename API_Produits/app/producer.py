import pika
import json
import os
import yaml

# Charger la config YAML
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.yaml')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

rabbitmq_config = config['message_broker']
RABBITMQ_HOST = rabbitmq_config['host']
RABBITMQ_PORT = rabbitmq_config.get('port', 5672)
QUEUE_NAME = rabbitmq_config['queue_name']

class RabbitMQProducer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, port=RABBITMQ_PORT)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=QUEUE_NAME, durable=True)

    def publish_event(self, event_type: str, data: dict):
        """Publie un événement dans RabbitMQ"""
        message = {
            "event": event_type,
            "data": data
        }
        self.channel.basic_publish(
            exchange='',
            routing_key=QUEUE_NAME,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f"Publié dans {QUEUE_NAME} : {message}")

    def close(self):
        self.connection.close()

# Global producer instance
producer = RabbitMQProducer()

def envoyer_message(routing_key: str, body: str):
    """Function to send messages - for compatibility with existing code"""
    try:
        data = json.loads(body) if isinstance(body, str) else body
        producer.publish_event(routing_key, data)
    except Exception as e:
        print(f"Error sending message: {e}")