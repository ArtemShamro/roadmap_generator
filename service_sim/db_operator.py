import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import yaml
from typing import Optional
from models.article import Article

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgresOperator:
    def __init__(self, config_path: str):
        """Инициализация оператора PostgreSQL с параметрами из конфигурации."""
        # Загрузка конфигурации
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        db_config = config.get("database", {})
        self.host = db_config.get("host", "pgdb")
        self.port = db_config.get("port", 5432)
        self.dbname = db_config.get("dbname", "scrapping")
        self.user = db_config.get("user", "articles")
        self.password = db_config.get("password", "articles")

        # Инициализация соединения
        self.conn = None
        self.connect()

    def connect(self):
        """Установка соединения с PostgreSQL."""
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                cursor_factory=RealDictCursor
            )
            logger.info("Successfully connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def close(self):
        """Закрытие соединения с PostgreSQL."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("PostgreSQL connection closed")

    def get_article_by_id(self, article_id: int) -> Optional[Article]:
        """
        Получение статьи из таблицы articles по ID.

        Args:
            article_id (int): ID статьи.

        Returns:
            Optional[Article]: Pydantic-модель статьи или None, если статья не найдена.
        """
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, name, text, complexity, reading_time, tags
                    FROM scrapping.articles
                    WHERE id = %s
                    """,
                    (article_id,)
                )
                article_data = cursor.fetchone()
                if article_data:
                    # Преобразуем tags из JSONB в Python-список
                    article_data["tags"] = article_data["tags"] if article_data["tags"] else [
                    ]
                    # Создаём Pydantic-модель
                    article = Article(**article_data)
                    logger.info(f"Retrieved article with ID {article_id}")
                    return article
                logger.info(f"Article with ID {article_id} not found")
                return None
        except Exception as e:
            logger.error(f"Error retrieving article with ID {article_id}: {e}")
            self.conn.rollback()
            return None
