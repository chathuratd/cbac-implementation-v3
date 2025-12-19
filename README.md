# CBIE MVP - Core Behavior Identification Engine

## Overview

The Core Behavior Identification Engine (CBIE) is an MVP system designed to identify a user's **core behaviors** from behavior inputs and prompt history. The system calculates behavior strengths, clusters similar behaviors, assigns canonical behaviors to clusters, and labels them as **PRIMARY**, **SECONDARY**, or **NOISE**.

## Features

- **Behavior Weight Calculation**: Uses credibility, clarity, and extraction confidence
- **Adjusted Behavior Weight**: Accounts for reinforcement and temporal decay
- **Semantic Clustering**: HDBSCAN-based clustering using embeddings
- **Tier Classification**: Automatic PRIMARY/SECONDARY/NOISE assignment
- **Temporal Analysis**: Tracks behavior persistence over time
- **Archetype Generation**: Optional LLM-based behavioral archetype labeling
- **REST API**: 5 endpoints for complete behavior analysis workflow

## Tech Stack

- **FastAPI**: Modern Python web framework
- **MongoDB**: Document database for behaviors, prompts, and profiles
- **Qdrant**: Vector database for semantic embeddings
- **Azure OpenAI**: Embeddings (text-embedding-3-large) and LLM (archetype generation)
- **HDBSCAN**: Density-based clustering algorithm
- **Pydantic**: Data validation and settings management

## Project Structure

```
implemantation-v3/
├── src/
│   ├── models/
│   │   └── schemas.py          # Pydantic data models
│   ├── database/
│   │   ├── mongodb_service.py  # MongoDB operations
│   │   └── qdrant_service.py   # Qdrant vector operations
│   ├── services/
│   │   ├── calculation_engine.py    # BW, ABW, CBI calculations
│   │   ├── embedding_service.py     # Azure OpenAI embeddings
│   │   ├── clustering_engine.py     # HDBSCAN clustering
│   │   ├── archetype_service.py     # LLM archetype generation
│   │   └── analysis_pipeline.py     # Main orchestration
│   ├── api/
│   │   └── routes.py           # FastAPI endpoints
│   ├── utils/
│   │   └── helpers.py          # Utility functions
│   └── config.py               # Configuration management
├── test-data/
│   ├── behaviors_user_348_1765993674.json
│   └── prompts_user_348_1765993674.json
├── tests/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env                        # Environment configuration
└── README.md
```

## Setup

### Prerequisites

- Python 3.9+
- MongoDB running on `localhost:27017`
- Qdrant running on `localhost:6333`
- Azure OpenAI API access

### Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure environment** (`.env` file already exists with configuration)

4. **Start MongoDB** (if not running):
   ```powershell
   # Using Docker
   docker run -d -p 27017:27017 --name mongodb -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=admin123 mongo:latest
   ```

5. **Start Qdrant** (if not running):
   ```powershell
   # Using Docker
   docker run -d -p 6333:6333 --name qdrant qdrant/qdrant:latest
   ```

## Running the Application

### Start the API Server

```powershell
python main.py
```

Or using uvicorn directly:

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at: `http://localhost:8000`

API Documentation (Swagger UI): `http://localhost:8000/docs`

## API Endpoints

### 1. POST `/api/v1/analyze-behaviors-from-storage` ⭐ (PRODUCTION)

**Main production endpoint** - Analyzes behaviors from existing storage.

In normal operation:
- **Behaviors** are stored in **Qdrant** (vector database with embeddings)
- **Prompts** are stored in **MongoDB**

This endpoint fetches from storage and runs analysis.

**Request**: Query parameter `user_id`

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/analyze-behaviors-from-storage?user_id=user_348"
```

**Response**: CoreBehaviorProfile with primary/secondary behaviors

---

### 2. POST `/api/v1/analyze-behaviors`

Import and analyze new behaviors (for testing/bulk import).

This endpoint:
- Stores prompts in MongoDB
- Generates embeddings for behaviors
- Stores behaviors with embeddings in Qdrant
- Stores behavior metadata in MongoDB
- Runs complete analysis

**Request Body**:
```json
{
  "user_id": "user_348",
  "behaviors": [...],
  "prompts": [...]
}
```

**Response**: CoreBehaviorProfile with primary/secondary behaviors

### 3. GET `/api/v1/get-user-profile/{user_id}`

Retrieve existing core behavior profile.

**Response**: CoreBehaviorProfile JSON

### 4. GET `/api/v1/list-core-behaviors/{user_id}`

Get canonical core behaviors for downstream usage.

**Response**: List of canonical behaviors with tiers

### 5. POST `/api/v1/update-behavior`

Update behavior metadata (reinforcement, credibility, timestamps).

**Request Body**:
```json
{
  "behavior_id": "beh_3ccbf2b2",
  "updates": {
    "reinforcement_count": 18,
    "last_seen": 1766000000
  }
}
```

### 6. POST `/api/v1/assign-archetype`

Generate behavioral archetype label using LLM.

**Request Body**:
```json
{
  "user_id": "user_348",
  "canonical_behaviors": ["prefers visual learning", "..."]
}
```

---

## Storage Architecture

### Normal Production Scenario

```
┌─────────────────────┐
│   User Behaviors    │
│  (behavior_text)    │
└──────────┬──────────┘
           │
           │ Embedded via Azure OpenAI
           ↓
┌─────────────────────┐
│  Qdrant Vector DB   │  ← Behaviors stored HERE (with embeddings)
│  - behavior_id      │
│  - embedding [3072] │
│  - behavior_text    │
│  - metadata         │
└─────────────────────┘

┌─────────────────────┐
│    MongoDB          │  ← Prompts stored HERE
│  - prompts          │
│  - behavior_metadata│  (optional, for quick access)
│  - core_profiles    │
└─────────────────────┘
```

**Typical Workflow**:
1. New behavior detected → Generate embedding → Store in **Qdrant**
2. User prompt received → Store in **MongoDB**
3. Analysis triggered → Fetch from **Qdrant** + **MongoDB** → Generate profile

## Formulas and Parameters

### Behavior Weight (BW)
```
BW = credibility^0.35 × clarity_score^0.40 × extraction_confidence^0.25
```

### Adjusted Behavior Weight (ABW)
```
ABW = BW × (1 + reinforcement_count × 0.01) × e^(-decay_rate × days_since_last_seen)
```

### Cluster Core Behavior Index (CBI)
```
Cluster_CBI = Σ(ABW_i) / N
```

### Tier Assignment
- **PRIMARY**: CBI ≥ 1.0
- **SECONDARY**: 0.7 ≤ CBI < 1.0
- **NOISE**: CBI < 0.7

### HDBSCAN Parameters
- `min_cluster_size`: 2
- `min_samples`: 1
- `cluster_selection_epsilon`: 0.15
- `metric`: cosine

## Testing with Sample Data

The `test-data/` folder contains sample behaviors and prompts for user_348:

```powershell
# Example: Load and test with sample data
python -c "
import json
from src.models.schemas import BehaviorModel, PromptModel

# Load behaviors
with open('test-data/behaviors_user_348_1765993674.json') as f:
    behaviors_data = json.load(f)
    behaviors = [BehaviorModel(**b) for b in behaviors_data]

# Load prompts
with open('test-data/prompts_user_348_1765993674.json') as f:
    prompts_data = json.load(f)
    prompts = [PromptModel(**p) for p in prompts_data]

print(f'Loaded {len(behaviors)} behaviors and {len(prompts)} prompts')
"
```

## Development

### Run Tests
```powershell
pytest tests/
```

### Code Style
```powershell
# Format code
black src/

# Lint
flake8 src/
```

## Logging

The application uses Python's built-in logging. Logs include:
- Info: Major pipeline steps and results
- Debug: Detailed calculations and intermediate values
- Error: Exceptions and failures

Adjust log level in `main.py` or via environment variable.

## Configuration

All configuration is in `.env`:

```env
# Database
MONGODB_URL=mongodb://admin:admin123@localhost:27017/
MONGODB_DATABASE=cbac_system
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=behavior_embeddings

# OpenAI
OPENAI_API_KEY=your-api-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_API_TYPE=azure
OPENAI_API_BASE=your-endpoint
OPENAI_API_VERSION=2024-02-01

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## Architecture

### Analysis Pipeline Flow

```
Input (behaviors + prompts)
    ↓
Calculate BW & ABW
    ↓
Generate Embeddings (Azure OpenAI)
    ↓
Store in Qdrant
    ↓
HDBSCAN Clustering
    ↓
Calculate Cluster CBI
    ↓
Select Canonical Behaviors
    ↓
Assign Tiers (PRIMARY/SECONDARY/NOISE)
    ↓
Calculate Temporal Metrics
    ↓
Generate Archetype (optional)
    ↓
Store Profile in MongoDB
    ↓
Return CoreBehaviorProfile
```

## Documentation

See the `docs/` folder for detailed documentation:
- **Core Behavior Identification Engine (CBIE) – MVP Documentation.md**: Complete system specification
- **CBIE MVP Documentation – Full Calculation Logic and Parameter Justification.md**: Detailed formula explanations

## License

This is an MVP research project.

## Support

For issues or questions, please check the documentation files or create an issue in the repository.
