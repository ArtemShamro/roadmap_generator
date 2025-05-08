import faiss
import logging
import os
import json
from typing import List, Tuple
from models.article import Article
from embeddings import EmbeddingGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, model_name: str = "distiluse-base-multilingual-cased-v1", index_path: str = "/app/faiss_data/faiss_index.bin", metadata_path: str = "/app/faiss_data/metadata.json"):
        """Инициализация векторного хранилища FAISS и генератора эмбеддингов."""
        self.embedding_generator = EmbeddingGenerator(model_name)
        self.dimension = self.embedding_generator.model.get_sentence_embedding_dimension()
        logger.info(
            f"Initialized EmbeddingGenerator with model: {model_name}, dimension: {self.dimension}")

        self.index = faiss.IndexFlatL2(self.dimension)
        logger.info("Initialized FAISS IndexFlatL2")

        self.id_to_index = {}
        self.index_to_id = {}
        self.index_path = index_path
        self.metadata_path = metadata_path

        # Создать директорию, если не существует
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)

        # Загрузка индекса и метаданных, если они существуют
        if os.path.exists(self.index_path):
            self.load(self.index_path)
            logger.info(f"Loaded existing FAISS index from {self.index_path}")
        if os.path.exists(self.metadata_path):
            self.load_metadata(self.metadata_path)
            logger.info(f"Loaded metadata from {self.metadata_path}")

    def add_article(self, article: Article):
        """Создание эмбеддинга статьи и добавление в FAISS."""
        try:
            embedding = self.embedding_generator.generate_embedding(
                article.text)
            embedding = embedding.reshape(1, -1)
            logger.info(
                f"Generated embedding for article {article.id}, shape: {embedding.shape}")

            index = self.index.ntotal
            self.index.add(embedding)
            logger.info(f"Added embedding to FAISS at index {index}")

            self.id_to_index[article.id] = index
            self.index_to_id[index] = article.id
            logger.info(
                f"Stored metadata for article {article.id} at FAISS index {index}")
            logger.info(f"id_to_index: {self.id_to_index}")

            # Сохраняем индекс и метаданные
            self.save(self.index_path)
            self.save_metadata(self.metadata_path)

        except Exception as e:
            logger.error(f"Error adding article {article.id} to FAISS: {e}")

    def search(self, query: str, k: int = 5) -> List[Tuple[Article, float]]:
        try:
            query_embedding = self.embedding_generator.generate_embedding(
                query)
            query_embedding = query_embedding.reshape(1, -1)
            logger.info(
                f"Generated query embedding, shape: {query_embedding.shape}")

            distances, indices = self.index.search(query_embedding, k)
            logger.info(f"Found {len(indices[0])} nearest neighbors for query")

            from db_operator import PostgresOperator
            db = PostgresOperator("config/config_sim.yaml")
            results = []
            for idx, distance in zip(indices[0], distances[0]):
                article_id = self.index_to_id.get(idx)
                if article_id is not None:
                    article = db.get_article_by_id(article_id)
                    if article:
                        results.append((article, distance))
                        logger.info(
                            f"Found relevant article {article_id} with distance {distance}")
                else:
                    logger.warning(
                        f"No article ID found for FAISS index {idx}")
            db.close()
            return results  # Исправлено: возвращать results, а не indices

        except Exception as e:
            logger.error(f"Error searching for query '{query}': {e}")
            return []

    def save(self, path: str = None):
        """Сохранение FAISS индекса на диск."""
        try:
            if path is None:
                path = self.index_path
            faiss.write_index(self.index, path)
            logger.info(f"Saved FAISS index to {path}")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")

    def load(self, path: str = None):
        """Загрузка FAISS индекса с диска."""
        try:
            if path is None:
                path = self.index_path
            self.index = faiss.read_index(path)
            logger.info(f"Loaded FAISS index from {path}")
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")

    def save_metadata(self, path: str = None):
        """Сохранение метаданных (id_to_index и index_to_id) в JSON."""
        try:
            if path is None:
                path = self.metadata_path
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                json.dump({
                    'id_to_index': {str(k): v for k, v in self.id_to_index.items()},
                    'index_to_id': {str(k): str(v) for k, v in self.index_to_id.items()}
                }, f)
            logger.info(f"Saved metadata to {path}")
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")

    def load_metadata(self, path: str = None):
        """Загрузка метаданных из JSON."""
        try:
            if path is None:
                path = self.metadata_path
            with open(path, 'r') as f:
                data = json.load(f)
                self.id_to_index = {k: v for k,
                                    v in data['id_to_index'].items()}
                self.index_to_id = {
                    int(k): v for k, v in data['index_to_id'].items()}
            logger.info(f"Loaded metadata from {path}")
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
