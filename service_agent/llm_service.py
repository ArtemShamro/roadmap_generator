import requests
import json
import time
import logging
import os
from fastapi import HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self, api_key: str, api_url: str = "https://api.groq.com/openai/v1/chat/completions"):
        self.api_key = api_key
        self.api_url = api_url
        if not api_key:
            raise ValueError("GROQ_API_KEY must be provided.")

    def _call_groq_api(self, prompt: str, max_retries: int = 3, retry_delay: float = 2.0) -> dict:
        """Internal method to call Groq API with retries."""
        for attempt in range(max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "llama3-70b-8192",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that generates structured JSON output."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.8
                }
                response = requests.post(
                    self.api_url, headers=headers, json=data)
                response.raise_for_status()

                response_data = response.json()
                logger.info("Groq API response: %s", response_data)

                if "choices" not in response_data or not response_data["choices"]:
                    raise HTTPException(
                        status_code=500, detail=f"Invalid response from Groq API: {response_data}")

                content = response_data["choices"][0]["message"]["content"]
                return json.loads(content)

            except requests.exceptions.HTTPError as e:
                status_code = response.status_code
                error_detail = response.json().get("error", {}).get("message", str(e))
                if status_code == 400:
                    raise HTTPException(
                        status_code=400, detail=f"Bad request to Groq API: {error_detail}")
                if status_code == 429:
                    if attempt < max_retries - 1:
                        logger.warning(
                            "Rate limit exceeded, retrying in %s seconds...", retry_delay)
                        time.sleep(retry_delay)
                        continue
                    raise HTTPException(
                        status_code=429, detail=f"Rate limit exceeded: {error_detail}")
                elif status_code == 401:
                    raise HTTPException(
                        status_code=401, detail=f"Invalid API key: {error_detail}")
                else:
                    raise HTTPException(
                        status_code=status_code, detail=f"Groq API error: {error_detail}")
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=500, detail="Failed to parse JSON response from Groq API.")
            except KeyError as e:
                raise HTTPException(
                    status_code=500, detail=f"Unexpected response structure from Groq API: missing {str(e)}")
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Unexpected error: {str(e)}")

        raise HTTPException(
            status_code=500, detail="Max retries exceeded for Groq API request.")

    def generate_roadmap(self, description: str) -> dict:
        """Generate a new roadmap based on description."""
        prompt = f"""
        Сгенерируй дорожную карту в формате JSON на основе описания: '{description}'.
        Дорожная карта состоит из шагов - steps (от 5 до 15), каждый шаг состоит из составляющих - substeps (от 2 до 15).
        Дорожная карта должна содержать заголовок - 'title' (строка) и массив 'steps', где каждый шаг - 'step' имеет имя - 'name' (строка),
        и массив элементов - 'steps', каждый элемент которого имеет одно поле - 'name'
        Убедитесь, что вывод является допустимым JSON и не содержит дополнительного текста, маркировок или кода.
        Пример:
        {{
            "title": "Дорожная карта разработчика бэкенда",
            "steps": [
                {{
                    "name": "Изучить основы интернета и операционных систем",
                    "steps": [
                        {{"name": "Как работает интернет"}},
                        {{"name": "Что такое HTTP"}},
                        {{"name": "Браузеры и их работа"}},
                        {{"name": "DNS и как он работает"}},
                        {{"name": "Что такое доменное имя"}},
                        {{"name": "Что такое хостинг"}},
                        {{"name": "Основы POSIX"}},
                        {{"name": "Управление памятью"}},
                        {{"name": "Межпроцессное взаимодействие"}},
                        {{"name": "Основы сетевых технологий"}}
                    ]
                }},
                {{
                    "name": "Выбрать язык программирования",
                    "steps": [
                        {{"name": "Go"}},
                        {{"name": "Java"}},
                        {{"name": "Rust"}},
                        {{"name": "C#"}},
                        {{"name": "PHP"}},
                        {{"name": "JavaScript"}},
                        {{"name": "Python"}},
                        {{"name": "Ruby"}}
                    ]
                }},
                {{
                    "name": "Изучить системы контроля версий",
                    "steps": [
                        {{"name": "Git"}},
                        {{"name": "GitHub"}},
                        {{"name": "Bitbucket"}},
                        {{"name": "GitLab"}}
                    ]
                }},
                {{
                    "name": "Работа с терминалами",
                    "steps": [
                        {{"name": "Основные команды терминала"}},
                        {{"name": "grep, awk, sed, lsof"}},
                        {{"name": "curl, wget, tail, head"}},
                        {{"name": "less, find, ssh, kill, dig"}}
                    ]
                }},
                {{
                    "name": "Изучить базы данных",
                    "steps": [
                        {{"name": "Реляционные базы данных"}},
                        {{"name": "PostgreSQL"}},
                        {{"name": "MySQL"}},
                        {{"name": "MariaDB"}},
                        {{"name": "MS SQL"}},
                        {{"name": "Oracle"}},
                        {{"name": "NoSQL базы данных"}},
                        {{"name": "MongoDB"}},
                        {{"name": "Cassandra"}},
                        {{"name": "Redis"}},
                        {{"name": "DynamoDB"}},
                        {{"name": "Neo4j"}}
                    ]
                }},
                {{
                    "name": "Изучить API и веб-технологии",
                    "steps": [
                        {{"name": "REST"}},
                        {{"name": "GraphQL"}},
                        {{"name": "gRPC"}},
                        {{"name": "JSON APIs"}},
                        {{"name": "SOAP"}},
                        {{"name": "WebSockets"}},
                        {{"name": "Server Sent Events"}}
                    ]
                }},
                {{
                    "name": "Изучить веб-серверы и контейнеризацию",
                    "steps": [
                        {{"name": "Nginx"}},
                        {{"name": "Apache"}},
                        {{"name": "Caddy"}},
                        {{"name": "MS IIS"}},
                        {{"name": "Docker"}},
                        {{"name": "LXC"}},
                        {{"name": "Kubernetes"}}
                    ]
                }},
                {{
                    "name": "Изучить кэширование и поисковые системы",
                    "steps": [
                        {{"name": "Redis"}},
                        {{"name": "Memcached"}},
                        {{"name": "Server Side Caching"}},
                        {{"name": "Client Side Caching"}},
                        {{"name": "CDN"}},
                        {{"name": "Elasticsearch"}},
                        {{"name": "Solr"}}
                    ]
                }},
                {{
                    "name": "Изучить архитектурные паттерны и масштабирование",
                    "steps": [
                        {{"name": "Монолитные приложения"}},
                        {{"name": "Микросервисы"}},
                        {{"name": "SOA"}},
                        {{"name": "CQRS"}},
                        {{"name": "Event Sourcing"}},
                        {{"name": "Twelve Factor Apps"}},
                        {{"name": "Стратегии масштабирования баз данных"}},
                        {{"name": "Типы масштабирования"}}
                    ]
                }},
                {{
                    "name": "Изучить тестирование и безопасность",
                    "steps": [
                        {{"name": "Интеграционное тестирование"}},
                        {{"name": "Модульное тестирование"}},
                        {{"name": "Функциональное тестирование"}},
                        {{"name": "OAuth"}},
                        {{"name": "Basic Auth"}},
                        {{"name": "Token Auth"}},
                        {{"name": "JWT"}},
                        {{"name": "OpenID"}},
                        {{"name": "SAML"}},
                        {{"name": "HTTPS"}},
                        {{"name": "CORS"}},
                        {{"name": "Content Security Policy"}},
                        {{"name": "OWASP Risks"}}
                    ]
                }},
                {{
                    "name": "Изучить observability и DevOps",
                    "steps": [
                        {{"name": "Логирование метрик"}},
                        {{"name": "Отладка и решение проблем"}},
                        {{"name": "Мониторинг"}},
                        {{"name": "Телеметрия"}},
                        {{"name": "CI/CD"}},
                        {{"name": "Service Mesh"}},
                        {{"name": "Профилирование производительности"}}
                    ]
                }}
            ]
        }}
        """
        return self._call_groq_api(prompt)

    def update_roadmap(self, current_roadmap: dict, command: str) -> dict:
        """Update an existing roadmap based on a command."""
        logger.info("Updating roadmap with command: %s", command)
        prompt = f"""
        Обновите следующую карту маршрутов на основе команды: '{command}'.
        Текущая карта маршрутов: {json.dumps(current_roadmap)}.
        Верните обновленную карту маршрутов в формате JSON с теми же структурами (заголовок и шаги).
        Убедитесь, что вывод является допустимым JSON и не содержит дополнительного текста, маркировок или кода.
        """
        return self._call_groq_api(prompt)
