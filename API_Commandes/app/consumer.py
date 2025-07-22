# app/consumer.py

import os
import pika
import json
import time
import yaml
from app.database import SessionLocal
from app.logger import setup_logger
from app.model import Customer, Product

logger = setup_logger("worker-consumer")

def get_rabbitmq_config():
    """
    Récupère la configuration RabbitMQ depuis variables d'environnement ou fichier YAML
    Les variables d'environnement ont la priorité (pour Docker)
    """
    # Priorité aux variables d'environnement (Docker)
    rabbitmq_host = os.getenv("RABBITMQ_HOST")
    if rabbitmq_host:
        return {
            "host": rabbitmq_host,
            "port": int(os.getenv("RABBITMQ_PORT", 5672)),
            "user": os.getenv("RABBITMQ_USER", "guest"),
            "password": os.getenv("RABBITMQ_PASSWORD", "guest")
        }
    
    # Fallback sur config YAML (développement local)
    try:
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.yaml')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        rabbitmq_config = config.get("rabbitmq", {})
        return {
            "host": rabbitmq_config.get("host", "localhost"),
            "port": rabbitmq_config.get("port", 5672),
            "user": rabbitmq_config.get("user", "guest"),
            "password": rabbitmq_config.get("password", "guest")
        }
    except FileNotFoundError:
        logger.warning("Fichier config.yaml non trouvé, utilisation des valeurs par défaut")
        return {
            "host": "localhost",
            "port": 5672,
            "user": "guest",
            "password": "guest"
        }

def create_rabbitmq_connection():
    """Crée une connexion RabbitMQ avec la configuration appropriée"""
    config = get_rabbitmq_config()
    
    logger.info(f"Connexion à RabbitMQ: {config['host']}:{config['port']}")
    
    credentials = pika.PlainCredentials(config["user"], config["password"])
    parameters = pika.ConnectionParameters(
        host=config["host"],
        port=config["port"],
        credentials=credentials,
        heartbeat=600,
        blocked_connection_timeout=300
    )
    
    return pika.BlockingConnection(parameters)

def demarrer_consumer():
    """Démarrage du consommateur RabbitMQ avec reconnexion automatique"""
    logger.info("Démarrage du consommateur RabbitMQ...")
    
    while True:
        connection = None
        try:
            connection = create_rabbitmq_connection()
            channel = connection.channel()

            # Configuration des exchanges et queues
            channel.exchange_declare(exchange="microservices", exchange_type="topic", durable=True)
            result = channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue

            # Binding des événements
            binding_keys = [
                "client.created", "client.updated", "client.deleted",
                "product.created", "product.updated", "product.deleted"
            ]
            
            for key in binding_keys:
                channel.queue_bind(exchange="microservices", queue=queue_name, routing_key=key)

            logger.info(f"✅ En attente de messages sur les clés : {', '.join(binding_keys)}")
            
            # Configuration du consumer
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=queue_name, on_message_callback=traiter_evenement)

            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"❌ Connexion AMQP perdue: {e}. Reconnexion dans 5s...")
            time.sleep(5)
        except KeyboardInterrupt:
            logger.info("⏹️ Arrêt du consumer demandé")
            if connection and not connection.is_closed:
                connection.close()
            break
        except Exception as e:
            logger.error(f"❌ Erreur inattendue : {e}")
            time.sleep(5)
        finally:
            if connection and not connection.is_closed:
                try:
                    connection.close()
                    logger.info("🔌 Connexion RabbitMQ fermée")
                except:
                    pass

def traiter_evenement(ch, method, properties, body):
    """Traite les événements reçus de RabbitMQ"""
    db = None
    try:
        # Décoder l'événement
        event_data = json.loads(body.decode())
        routing_key = method.routing_key
        
        logger.info(f"📨 [MQ] Événement reçu : {routing_key} - Données : {event_data}")
        
        # Créer une nouvelle session DB
        db = SessionLocal()
        
        # Router selon le type d'événement
        if routing_key.startswith("client."):
            traiter_evenement_client(db, routing_key, event_data)
        elif routing_key.startswith("product."):
            traiter_evenement_produit(db, routing_key, event_data)
        else:
            logger.warning(f"❓ Événement inconnu : {routing_key}")
        
        # Confirmer le traitement
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.debug(f"✅ Événement {routing_key} traité avec succès")

    except json.JSONDecodeError as e:
        logger.error(f"❌ Erreur décodage JSON : {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    except Exception as e:
        logger.error(f"❌ Erreur lors du traitement de {routing_key}: {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    finally:
        if db:
            db.close()

def traiter_evenement_client(db, routing_key, event_data):
    """Traite les événements liés aux clients"""
    # ✅ CORRECTION 1: Extraction correcte des données
    data = event_data.get('data', event_data)  # Fallback si pas de structure 'data'
    
    if routing_key == "client.created":
        logger.info(f"👤 ✅ Nouveau client créé")
        
        # ✅ CORRECTION 2: Utilisation de 'data' au lieu de 'event_data'
        nouveau_client = Customer(
            username=data.get("username"),
            name=data.get("name"),
            first_name=data.get("first_name"),  # ✅ snake_case
            last_name=data.get("last_name"),    # ✅ snake_case
            postal_code=data.get("postal_code"),
            city=data.get("city"),
            profile_first_name=data.get("profile_first_name"),
            profile_last_name=data.get("profile_last_name"),
            company_name=data.get("company_name"),
            phone=data.get("phone"),
            actif=data.get("actif", True),  # ✅ True par défaut
            email=data.get("email"),
            # ✅ CORRECTION 3: Ne pas inclure password_hash si non fourni
            password_hash=data.get("password_hash") if data.get("password_hash") else None
        )
        db.add(nouveau_client)
        db.commit()
        db.refresh(nouveau_client)  # ✅ Pour récupérer l'ID généré
        logger.info(f"✅ Client ajouté à la base de données avec l'ID: {nouveau_client.id}")
        
    elif routing_key == "client.updated":
        # ✅ CORRECTION 4: Récupération de l'ID client
        client_id = data.get("id")
        if not client_id:
            logger.error("❌ ID client manquant pour la mise à jour")
            return
            
        logger.info(f"👤 🔄 Client mis à jour : {client_id}")
        client = db.query(Customer).filter_by(id=client_id).first()
        if client:
            # ✅ CORRECTION 5: Utilisation de 'data' et des bons noms de champs
            client.username = data.get("username", client.username)
            client.name = data.get("name", client.name)
            client.first_name = data.get("first_name", client.first_name)
            client.last_name = data.get("last_name", client.last_name)
            client.postal_code = data.get("postal_code", client.postal_code)
            client.city = data.get("city", client.city)
            client.profile_first_name = data.get("profile_first_name", client.profile_first_name)
            client.profile_last_name = data.get("profile_last_name", client.profile_last_name)
            client.company_name = data.get("company_name", client.company_name)
            client.phone = data.get("phone", client.phone)
            client.actif = data.get("actif", client.actif)
            client.email = data.get("email", client.email)
            if data.get("password_hash"):
                client.password_hash = data.get("password_hash")
            
            db.commit()
            logger.info(f"✅ Client mis à jour en base : {client_id}")
        else:
            logger.warning(f"⚠️ Client {client_id} non trouvé pour mise à jour")
            
    elif routing_key == "client.deleted":
        # ✅ CORRECTION 6: Récupération de l'ID depuis les données
        client_id = data.get("client_id") or data.get("id")
        if not client_id:
            logger.error("❌ ID client manquant pour la suppression")
            return
            
        logger.info(f"👤 🗑️ Client supprimé : {client_id}")
        client = db.query(Customer).filter_by(id=client_id).first()
        if client:
            db.delete(client)
            db.commit()
            logger.info(f"✅ Client supprimé de la base : {client_id}")
        else:
            logger.warning(f"⚠️ Client {client_id} non trouvé pour suppression")

def traiter_evenement_produit(db, routing_key, event_data):
    """Traite les événements liés aux produits"""
    # ✅ CORRECTION 7: Même logique pour les produits
    data = event_data.get('data', event_data)
    product_id = data.get('product_id') or data.get('id')
    
    if routing_key == "product.created":
        logger.info(f"📦 ✅ Nouveau produit créé : {product_id}")
        nouveau_produit = Product(
            id=product_id,
            name=data.get("name"),
            stock=data.get("stock"),
            price=data.get("price"),
            description=data.get("description"),
            color=data.get("color", ""),
        )
        db.add(nouveau_produit)
        db.commit()
        logger.info(f"✅ Produit ajouté à la base de données : {product_id}")
        
    elif routing_key == "product.updated":
        if not product_id:
            logger.error("❌ ID produit manquant pour la mise à jour")
            return
            
        logger.info(f"📦 🔄 Produit mis à jour : {product_id}")
        produit = db.query(Product).filter_by(id=product_id).first()
        if produit:
            produit.name = data.get("name", produit.name)
            produit.stock = data.get("stock", produit.stock)
            produit.price = data.get("price", produit.price)
            produit.description = data.get("description", produit.description)
            produit.color = data.get("color", produit.color)
            db.commit()
            logger.info(f"✅ Produit mis à jour en base : {product_id}")
        else:
            logger.warning(f"⚠️ Produit {product_id} non trouvé pour mise à jour")
            
    elif routing_key == "product.deleted":
        if not product_id:
            logger.error("❌ ID produit manquant pour la suppression")
            return
            
        logger.info(f"📦 🗑️ Produit supprimé : {product_id}")
        produit = db.query(Product).filter_by(id=product_id).first()
        if produit:
            db.delete(produit)
            db.commit()
            logger.info(f"✅ Produit supprimé de la base : {product_id}")
        else:
            logger.warning(f"⚠️ Produit {product_id} non trouvé pour suppression")

if __name__ == "__main__":
    demarrer_consumer()
