import re
import markdown
from sentence_transformers import SentenceTransformer
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    def __init__(self, model_name: str = "distiluse-base-multilingual-cased-v1"):
        """
        Инициализация генератора эмбеддингов.

        Args:
            model_name (str): Название модели SentenceTransformer.
        """
        self.model = SentenceTransformer(model_name)
        logger.info(f"Initialized SentenceTransformer model: {model_name}")

    def preprocess_markdown(self, text: str) -> str:
        """
        Предобработка текста Markdown для удаления форматирования и выделения информативного контента.

        Args:
            text (str): Входной текст в формате Markdown.

        Returns:
            str: Очищенный текст, готовый для генерации эмбеддинга.
        """
        try:
            # Конвертация Markdown в текст
            html = markdown.markdown(text)

            # Удаление HTML-тегов
            clean_text = re.sub(r'<[^>]+>', '', html)

            # Удаление остатков Markdown-форматирования
            clean_text = re.sub(r'\[([^\]]*)\]\([^\)]*\)',
                                r'\1', clean_text)  # Ссылки
            clean_text = re.sub(r'```.*?```', '', clean_text,
                                flags=re.DOTALL)  # Кодовые блоки
            clean_text = re.sub(r'`.*?`', '', clean_text)  # Инлайн-код
            clean_text = re.sub(r'#+ ', '', clean_text)  # Заголовки
            clean_text = re.sub(r'[-*+]\s', '', clean_text)  # Списки

            # Удаление специальных символов, оставляем буквы, цифры и пробелы
            clean_text = re.sub(r'[^\w\s]', '', clean_text)

            # Нормализация пробелов
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()

            logger.debug(f"Processed Markdown text: {clean_text[:100]}...")

            # Если текст пустой, возвращаем пробел
            return clean_text if clean_text else " "
        except Exception as e:
            logger.error(f"Error preprocessing Markdown: {e}")
            return " "

    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Генерация эмбеддинга для текста с предобработкой.

        Args:
            text (str): Входной текст (Markdown).

        Returns:
            numpy.ndarray: Эмбеддинг текста.
        """
        try:
            # Предобработка текста
            processed_text = self.preprocess_markdown(text)
            # Генерация эмбеддинга
            embedding = self.model.encode(
                processed_text, convert_to_numpy=True)
            logger.info(
                f"Generated embedding for text, shape: {embedding.shape}")
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return np.zeros(self.model.get_sentence_embedding_dimension())
