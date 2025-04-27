from dotenv import load_dotenv
load_dotenv()

import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "my-secret-token")
INFLUX_ORG = os.getenv("INFLUX_ORG", "troubleshooters")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "metrics")

# New: Ollama endpoint
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

