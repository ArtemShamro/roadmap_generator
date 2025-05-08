from confluent_kafka import Consumer, KafkaError
import logging
import yaml
import asyncio
import json
from db_operator import PostgresOperator
from models.article import Article
from vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KafkaConsumer:
    def __init__(self, config_path: str, vector_store: VectorStore):
        # Загрузка конфигурации
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        self.topic = config["kafka"]["topic"]
        self.brokers = config["kafka"]["brokers"]
        self.group_id = config["kafka"]["group_id"]

        # Настройки Kafka Consumer
        self.consumer_config = {
            "bootstrap.servers": self.brokers,
            "group.id": self.group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
        }
        self.consumer = Consumer(self.consumer_config)
        self.consumer.subscribe([self.topic])

        # Инициализация оператора PostgreSQL
        self.db = PostgresOperator(config_path)

        # Инициализация VectorStore
        self.vector_store = vector_store
        logger.info("Initialized KafkaConsumer with VectorStore")

    async def consume(self):
        try:
            while True:
                msg = self.consumer.poll(timeout=1.0)
                if msg is None:
                    await asyncio.sleep(0.1)
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        logger.info(
                            f"Reached end of partition: {msg.partition()}")
                    else:
                        logger.error(f"Kafka error: {msg.error()}")
                    continue

                value = msg.value().decode("utf-8") if msg.value() else None
                logger.info(f"Received message: value={value}")

                try:
                    data = json.loads(value)  # {"id": 123}
                    article_id = data["id"]
                    # Получаем статью из PostgreSQL
                    article = self.db.get_article_by_id(article_id)
                    if article:
                        logger.info(
                            f"Processing article: id={article_id}, title={article.name}")
                        self.process_article(article)
                    else:
                        logger.warning(
                            f"Article {article_id} not found in database")
                except Exception as e:
                    logger.error(f"Error processing message {value}: {e}")

        except Exception as e:
            logger.error(f"Error in consumer: {e}")
        finally:
            self.db.close()
            self.consumer.close()

    def process_article(self, article: Article):
        """Обработка статьи: генерация эмбеддинга и добавление в VectorStore."""
        try:
            logger.info(
                f"Processing article {article.id}: {article.text[:100]}...")
            # Добавляем статью в VectorStore (эмбеддинг генерируется с предобработкой Markdown)
            self.vector_store.add_article(article)
            logger.info(
                f"Successfully added article {article.id} to VectorStore")
        except Exception as e:
            logger.error(f"Error processing article {article.id}: {e}")

    def start(self):
        asyncio.run(self.consume())
