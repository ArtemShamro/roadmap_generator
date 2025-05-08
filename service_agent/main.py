
from llm_service import LLMService
import redis
import json
import uuid
import os
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import logging
import time
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


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

# Redis setup
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_TTL = int(os.getenv("REDIS_TTL", 3600))
API_URL = "https://api.groq.com/openai/v1/chat/completions"
API_KEY = os.environ.get("GROQ_API_KEY")

redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

llm_service = LLMService(api_key=os.getenv("GROQ_API_KEY"))


class RoadmapCreate(BaseModel):
    description: str


class RoadmapUpdate(BaseModel):
    roadmap_id: str
    command: str


class RoadmapResponse(BaseModel):
    id: str
    title: str
    structure: dict


@app.post("/generate", response_model=RoadmapResponse)
async def generate_roadmap(roadmap: RoadmapCreate):
    logger.info(roadmap)
    result = llm_service.generate_roadmap(roadmap.description)
    print(result)
    logger.info(result)
    roadmap_id = str(uuid.uuid4())

    redis_client.setex(roadmap_id, REDIS_TTL, json.dumps(result))

    return RoadmapResponse(id=roadmap_id, title=result["title"], structure=result)


@app.put("/update", response_model=RoadmapResponse)
async def update_roadmap(update: RoadmapUpdate):
    roadmap_id = update.roadmap_id
    logger.info("Update: %s", update)
    roadmap_json = redis_client.get(roadmap_id)
    if not roadmap_json:
        raise HTTPException(status_code=404, detail="Roadmap not found")

    current_roadmap = json.loads(roadmap_json)

    result = llm_service.update_roadmap(current_roadmap, update.command)

    redis_client.setex(roadmap_id, REDIS_TTL, json.dumps(result))

    return RoadmapResponse(id=roadmap_id, title=result["title"], structure=result)
