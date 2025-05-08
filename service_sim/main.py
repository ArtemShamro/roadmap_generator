from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager
import yaml
import asyncio
from kafka_consumer import KafkaConsumer
from db_operator import PostgresOperator
from vector_store import VectorStore
from models.article import Article
import logging
from pydantic import BaseModel
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SearchRequest(BaseModel):
    query: str
    k: Optional[int] = 5  # Количество возвращаемых статей


class SearchResponse(BaseModel):
    article: Article
    distance: float


with open("config/config_sim.yaml", "r") as f:
    config = yaml.safe_load(f)

postgres_operator = PostgresOperator(config_path="config/config_sim.yaml")
vector_store = VectorStore(model_name="distiluse-base-multilingual-cased-v1")
kafka_consumer = KafkaConsumer(
    config_path="config/config_sim.yaml", vector_store=vector_store)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Kafka Consumer...")
    task = asyncio.create_task(kafka_consumer.consume())
    yield
    logger.info("Stopping Kafka Consumer...")
    kafka_consumer.consumer.close()
    postgres_operator.close()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Kafka consumer task cancelled")

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Python service is running", "config": config}


@app.get("/all")
async def get_article():
    logger.info("Getting all articles...")
    logger.info(vector_store.id_to_index)
    return vector_store.id_to_index


@app.post("/search", response_model=List[SearchResponse])
async def search_articles(request: SearchRequest):
    """Поиск релевантных статей по текстовому запросу."""
    logger.info(
        f"Received search request: query='{request.query}', k={request.k}")
    results = vector_store.search(request.query, k=request.k)
    return [{"article": article, "distance": distance} for article, distance in results]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
