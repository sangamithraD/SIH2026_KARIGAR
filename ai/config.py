import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# LLM Configuration (Ollama)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "3.0"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "2"))

# Speech Configuration (faster-whisper)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8" if WHISPER_DEVICE == "cpu" else "float16")

# Translation Configuration
DEFAULT_TARGET_LANGUAGE = os.getenv("DEFAULT_TARGET_LANGUAGE", "en")
SUPPORTED_LANGUAGES = ["ta", "hi", "en"]

# Intent & Action Thresholds
HIGH_CONFIDENCE_THRESHOLD = float(os.getenv("HIGH_CONFIDENCE_THRESHOLD", "0.70"))
DESTRUCTIVE_INTENTS = {"DELETE_PRODUCT", "DELETE_RAW_MATERIAL", "RESET_ACCOUNT"}
CONFIRMATION_REQUIRED_INTENTS = {"PUBLISH_PRODUCT", "PUBLISH_RAW_MATERIAL", "UPDATE_PRICE"}

# Image Processing Configuration
MAX_IMAGE_DIMENSION = int(os.getenv("MAX_IMAGE_DIMENSION", "800"))
DEFAULT_JPEG_QUALITY = 85
BLUR_THRESHOLD = 100.0  # Laplacian variance threshold
UNDEREXPOSED_THRESHOLD = 40.0
OVEREXPOSED_THRESHOLD = 210.0

# Service Port
PORT = int(os.getenv("PORT", "8001"))
HOST = os.getenv("HOST", "0.0.0.0")
