# KAI — Open-Source AI Layer Engine & Services

KARIGAR is an AI-powered digital assistant designed for marginalized artisans. This repository contains the complete **AI Layer**, exposing clean FastAPI microservices and action contracts for the FastAPI backend to execute.

---

## Architecture Overview

```
VOICE / TEXT / PHOTO INPUT
       │
       ▼
 ┌───────────┐      ┌─────────────┐      ┌──────────────┐
 │  Speech   │ ───► │ Translation │ ───► │    Intent    │
 │ (Whisper) │      │  (Indic/en) │      │ Understanding│
 └───────────┘      └─────────────┘      └──────┬───────┘
                                                │
       ┌────────────────────────────────────────┴────────────────────────────────────────┐
       ▼                                        ▼                                        ▼
┌──────────────┐                       ┌─────────────────┐                      ┌─────────────────┐
│ E-Commerce   │                       │ Computer Vision │                      │ Fair Pricing &  │
│ Generation   │                       │ Photo Pipeline  │                      │ Tutorial Recom. │
│ (Product/    │                       │ (OpenCV/Pillow/ │                      │ (Complexity/    │
│  Story/Ideas)│                       │  rembg)         │                      │  Tutorials)     │
└──────┬───────┘                       └────────┬────────┘                      └────────┬────────┘
       │                                        │                                        │
       └────────────────────────────────────────┼────────────────────────────────────────┘
                                                ▼
                                   ┌────────────────────────┐
                                   │  Structured JSON       │
                                   │  Action Contract       │
                                   └────────────┬───────────┘
                                                ▼
                                   ┌────────────────────────┐
                                   │ FastAPI Backend        │
                                   │ (Executes DB & Actions)│
                                   └────────────────────────┘
```

---

## Requirements & Prerequisites

- **Python**: 3.9+ (Python 3.10 or 3.11 recommended)
- **CPU / RAM**: Minimum 4-Core CPU, 8GB RAM (16GB RAM recommended for local Ollama models)
- **GPU (Optional)**: NVIDIA GPU with CUDA for accelerated Whisper and Ollama inference
- **Ollama**: Local Ollama service running on `http://localhost:11434`

---

## Quick Start & Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Local LLM (Ollama)

Download and install Ollama from [ollama.com](https://ollama.com). Then pull your preferred local instruct model:

```bash
ollama pull llama3.2
# Or alternative models:
# ollama pull qwen2.5
# ollama pull mistral
```

Ensure Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

### 3. Environment Variables (Optional Configuration)

Create a `.env` file or export environment variables:

```ini
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
WHISPER_MODEL=base
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8
PORT=8001
HOST=0.0.0.0
HIGH_CONFIDENCE_THRESHOLD=0.70
```

---

## Starting the AI Service

Run the standalone FastAPI AI service using Uvicorn:

```bash
python main.py
```

The service will start at `http://localhost:8001`. You can view interactive OpenAPI documentation at `http://localhost:8001/docs`.

---

## API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/ai/health` | Health check & model status |
| `POST` | `/api/ai/transcribe` | Speech-to-text audio transcription (`faster-whisper` / custom audio files) |
| `POST` | `/api/ai/intent` | Voice command intent & entity parameter extraction |
| `POST` | `/api/voice/command` | Complete Voice Pipeline accepting custom audio upload (`.wav`, `.mp3`, `.m4a`, `.ogg`, `.webm`) |
| `POST` | `/api/ai/generate-product` | E-commerce product listing generation (truthful, non-hallucinatory) |
| `POST` | `/api/ai/generate-story` | Authentic artisan craft story transformation |
| `POST` | `/api/ai/generate-ideas` | Raw material to product ideas generator (3-5 ideas) |
| `POST` | `/api/ai/analyze-image` | Computer vision photo quality analyzer (lighting, blur, resolution) |
| `POST` | `/api/ai/enhance-image` | Photo contrast, brightness, sharpening & `rembg` background removal |
| `POST` | `/api/ai/assess-pricing` | Craft complexity rating (1-5) & effort category for backend pricing |
| `POST` | `/api/ai/recommend-tutorials`| Verified craft tutorial matching by material, craft & language |

---

## Example Requests & Responses

### 1. Intent Classification (`POST /api/ai/intent`)

**Request**:
```json
{
  "text": "என்னிடம் ஐந்து கிலோ மூங்கில் இருக்கிறது",
  "language": "ta"
}
```

**Response**:
```json
{
  "intent": "ADD_RAW_MATERIAL",
  "confidence": 0.95,
  "parameters": {
    "name": "Bamboo",
    "quantity": 5,
    "unit": "kg"
  },
  "requires_confirmation": false
}
```

---

### 2. Product Generation (`POST /api/ai/generate-product`)

**Request**:
```json
{
  "transcript": "I want to make a bamboo basket",
  "material": "Bamboo",
  "craftType": "Weaving",
  "language": "en"
}
```

**Response**:
```json
{
  "productName": "Handcrafted Bamboo Storage Basket",
  "category": "Home Decor & Storage",
  "material": "Bamboo",
  "craftType": "Weaving",
  "description": "Artisanal hand-woven bamboo basket crafted with care. Ideal for home storage and organization.",
  "keywords": ["bamboo", "handwoven", "basket", "storage", "eco-friendly"]
}
```

---

## Verification & Testing

### Run Unit & Integration Tests

```bash
python -m unittest discover -s tests
```

### Run 6-Step End-to-End Interactive Demo Flow

```bash
python demo_flow.py
```

---

## Backend Integration Contract

1. **DB Safety Boundary**: The AI layer NEVER interacts directly with SQLite or executes database CRUD operations.
2. **Intent Contracts**: The AI layer evaluates user input and returns structured proposals (`intent`, `confidence`, `parameters`, `requires_confirmation`).
3. **Action Execution**: The FastAPI backend receives the proposal, validates user permissions, and executes DB insertions or marketplace publishing.
4. **Fair Pricing Boundary**: The AI layer provides complexity classification ratings (1-5) and effort categories. Final prices are determined deterministically by the backend formula (`Material + Labour + Packaging`).
5. **Fallback Mechanics**: If Ollama or faster-whisper are offline or running on low-resource machines, deterministic template fallbacks automatically engage so no request fails.
