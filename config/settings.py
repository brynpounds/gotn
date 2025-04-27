import os
import platform
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Platform-specific Docker host handling
if platform.system() == "Darwin":  # macOS
    os.environ["OLLAMA_URL"] = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434")
    os.environ["REDIS_HOST"] = os.getenv("REDIS_HOST", "host.docker.internal")
    os.environ["INFLUX_URL"] = os.getenv("INFLUX_URL", "http://host.docker.internal:8086")

# Shared config
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "my-secret-token")
INFLUX_ORG = os.getenv("INFLUX_ORG", "troubleshooters")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "metrics")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.35"))
UNSTRUCTURED_SIMILARITY_THRESHOLD = float(os.getenv("UNSTRUCTURED_SIMILARITY_THRESHOLD", "0.51"))

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")  # Default to mistral if not set

