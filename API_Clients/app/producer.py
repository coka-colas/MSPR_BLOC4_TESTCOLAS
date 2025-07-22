""""
Module de production de messages pour RabbitMQ
"""

# Standard
import os
import time

# Tiers
import pika
import json
import yaml

# Local
from app.logger import setup_logger

logger = setup_logger("mq-producer")

# Charger la config YAML
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.yaml')
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

rabbitmq_config = config['message_broker']
RABBITMQ_HOST = rabbitmq_config.get('host', 'rabbitmq-shared')
RABBITMQ_PORT = rabbitmq_config.get('port')
QUEUE_NAME = rabbitmq_config['queue_name']
RABBITMQ_USER = rabbitmq_config.get('user', 'guest')
RABBITMQ_PASSWORD = rabbitmq_config.get('password', 'guest')

class RabbitMQProducer:
    def __init__(self, max_retries=3, retry_delay=5):
        """
        Initialise le producteur RabbitMQ avec des tentatives de connexion.
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connected = False

        for attempt in range(max_retries):
            try:
                credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
                self.connection = pika.BlockingConnection(
                    pika.ConnectionParameters(
                        host=RABBITMQ_HOST,
                        port=RABBITMQ_PORT,
                        credentials=credentials
                    )
                )
                self.channel = self.connection.channel()
                self.channel.exchange_declare(
                    exchange='microservices',
                    exchange_type='topic',
                    durable=True
                )
                self.channel.queue_declare(queue=QUEUE_NAME, durable=True)
                self.connected = True
                break
            except pika.exceptions.AMQPConnectionError as e:
                logger.error("Échec de la connexion à RabbitMQ (tentative %d) : %s", attempt + 1, e)
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise


    def publish_event(self, event_type: str, data: dict):
        """
        Publie un événement sur RabbitMQ.
        """
        try:
            message = {
                "event": event_type,
                "data": data
            }
            self.channel.basic_publish(
                exchange='microservices',
                routing_key=event_type,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            logger.info("Message publié : %s", message)
        except pika.exceptions.AMQPError as e:
            logger.error("Échec AMQP : %s", e)
        except json.JSONDecodeError as e:
            logger.error("Échec de sérialisation JSON : %s", e)
            self.close()

    def close(self):
        self.connection.close()