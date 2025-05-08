# Сервис для генерации roadmap

Система генерирует по запросу пользователя roadmap с возможностью его последующей доработки и внесения исправлений. Для каждого понка roadmap подбираются релевантные статьи с habr.

Сервисы системы:

- сервис скрапинга, предоставляющий возможность собирать и хранить в postgress статьи с habr для последующего использования.
- сервис получения эмбеднигов статей habr и организации хранения в вектороной бд (используется модель distiluse-base-multilingual-cased-v1 из библиотеки sentence_transformers, бд - faiss).
- сервис генерации roadmap по запросу пользователя. (используется api Grok с моделью llama3-70b-8192)
- frontend на React для доступа к функционалу сервиса.


## 🛠 Технологии
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)
![asyncio](https://img.shields.io/badge/asyncio-Python_3.11-3776AB?style=flat&logo=python)
![FastAPI](https://img.shields.io/pypi/v/fastapi?color=009688&label=FastAPI&logo=fastapi)
![sentence-transformers](https://img.shields.io/pypi/v/sentence-transformers?color=green&label=sentence--transformers)
![Grok API](https://img.shields.io/badge/Grok_API-xAI-FF4500?style=flat)
![OpenAI](https://img.shields.io/pypi/v/openai?color=412991&label=OpenAI)
![FAISS](https://img.shields.io/badge/FAISS-1.8.0-blue?style=flat)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12.1-336791?style=flat&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-7.2-DC382D?style=flat&logo=redis)
![Kafka](https://img.shields.io/badge/Kafka-3.7.0-231F20?style=flat&logo=apachekafka)
![React](https://img.shields.io/badge/React-18.2.0-61DAFB?style=flat&logo=react)
![Docker](https://img.shields.io/badge/Docker-24.0.7-2496ED?style=flat&logo=docker)

## 🚀 Запуск

Для работы сервиса генерации необходим файл `.env` c API ключем Grok:

```
GROQ_API_KEY=<your_api_key>
```

Чтобы запустить сервис, используйте следующую команду:

`docker compose up -d`

Это создаст и запустит все необходимые контейнеры в фоновом режиме.

После запуска сервис будет доступен по адресу http://localhost:3000/

## 🎯 Демонстрация

https://github.com/user-attachments/assets/a34a8a65-c2ed-4aef-aea8-46c135ccde1c

