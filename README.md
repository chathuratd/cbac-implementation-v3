# CBIE MVP - Core Behavior Identification Engine

## Overview

The Core Behavior Identification Engine (CBIE) is an MVP system that identifies a user's behavioral patterns by clustering observed interactions, computing behavior strengths, and producing a profile (primary/core and secondary/supporting behaviors). The system computes behavior weights, groups semantically-similar behaviors, assigns canonical labels, and classifies clusters by tier.

## What changed (recent updates)

- Frontend added: a React + Vite UI (Tailwind CSS) for profile inspection and interaction.
- UI terminology uses user-friendly labels: **Core** (PRIMARY) and **Supporting** (SECONDARY) behaviors. The backend still refers to tiers as PRIMARY/SECONDARY/NOISE internally.
- Tests and utility scripts moved into the `tests/` folder for better organization.
- Detailed documentation added under `docs/`, including `BEHAVIORS_CLUSTERS_ARCHETYPES.md` which explains behaviors → clusters → archetypes.

## Features

- Behavior Weight Calculation: credibility, clarity, and extraction confidence
- Adjusted Behavior Weight: accounts for reinforcement and temporal decay
- Semantic Clustering: HDBSCAN-based clustering using vector embeddings
- Tier Classification: clusters labelled (PRIMARY / SECONDARY / NOISE) — presented in the UI as Core / Supporting
- Temporal Analysis: tracks behavior persistence and recency
- Archetype Generation: optional LLM-based archetype labeling
- REST API: endpoints to analyze, retrieve and update profiles

## Tech Stack

- Backend: FastAPI (Python)
- Frontend: React + Vite, Tailwind CSS
- Databases: MongoDB (documents) and Qdrant (vector embeddings)
- Embeddings & LLM: Azure OpenAI (configurable models)
- Clustering: HDBSCAN (cosine metric)

## Project Structure

```
implemantation-v3/
├── frontend/                  # React + Vite frontend (Tailwind)
├── src/                       # Backend implementation (FastAPI)
│   ├── models/
│   ├── database/              # mongodb_service.py, qdrant_service.py
│   ├── services/              # clustering_engine, embedding_service, calculation_engine, etc.
│   └── api/                   # routes
├── docs/                      # System documentation (incl. BEHAVIORS_CLUSTERS_ARCHETYPES.md)
├── test-data/                 # Sample data for testing
├── tests/                     # Unit & integration tests
├── main.py                    # Backend entry point
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.9+
- Node.js (for frontend) and npm/yarn
- MongoDB (localhost:27017)
- Qdrant (localhost:6333)
- Azure OpenAI credentials (if using embeddings/LLM)

## Installation

1. Backend dependencies:

```powershell
pip install -r requirements.txt
```

2. Frontend dependencies (from project root):

```powershell
cd frontend
npm install
```

3. Configure environment in `.env` (see sample entries below).

## Running the system

Start MongoDB and Qdrant (if needed). Example using Docker:

```powershell
# MongoDB
docker run -d -p 27017:27017 --name mongodb -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=admin123 mongo:latest

# Qdrant
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant:latest
```

Start the backend API (from repo root):

```powershell
python main.py
# or
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Start the frontend (from `frontend`):

```powershell
cd frontend
npm run dev
```

The frontend runs by default on `http://localhost:5173` and the backend on `http://localhost:8000`.

## API Highlights

- `POST /api/v1/analyze-behaviors-from-storage?user_id=<id>` : Run analysis using stored data
- `POST /api/v1/analyze-behaviors` : Import + analyze behaviors (testing/bulk)
- `GET /api/v1/get-user-profile/{user_id}` : Retrieve computed profile
- `GET /api/v1/list-core-behaviors/{user_id}` : List canonical behaviors
- `POST /api/v1/update-behavior` : Update behavior metadata

See `src/api/routes.py` for full details.

## UI / Frontend notes

- The frontend displays clusters grouped into **Core** and **Supporting** sections. Both sections are collapsible and the UI emphasizes a compact card layout that matches the design system (rounded-2xl, slate palette, shadow-xl).
- Example demo user id used in UI: `user_665390` (used throughout tests and screenshots).

## Formulas & Parameters (summary)

Note: the project now uses a cluster-centric pipeline. The README below highlights the formulas actually used for scoring and tiering. Legacy BW/ABW/CBI formulas exist in code for per-observation metrics but are not the primary mechanism for tier assignment.

1) Cluster strength (used for tiering)

	- Raw strength:

		raw_strength = log(cluster_size + 1) × mean_abw × recency_factor

	- Normalized strength (final score in 0–1):

		cluster_strength = raw_strength / (1 + raw_strength)

	- Recency factor:

		recency_factor = average( exp(-decay_rate × days_since_observation) )

		(decay_rate defaults to 0.01 in code)

	- Implementation notes:
		- `mean_abw` is computed from per-observation ABW values (see legacy formulas below).
		- The normalization uses x/(1+x) to bound scores and produce sensible thresholds.

2) Cluster confidence (consistency + reinforcement)

	- Consistency score = 1 / (1 + mean_intra_cluster_distance)
	- Reinforcement score = min(1.0, log10(cluster_size + 1))
	- Clarity trend is computed for reporting (difference between later and earlier clarity averages)
	- Final confidence = consistency_score × reinforcement_score (with a small bonus if clarity trend > 0)

3) Tier thresholds (cluster-centric)

	- PRIMARY (Core): cluster_strength ≥ 0.80
	- SECONDARY (Supporting): 0.40 ≤ cluster_strength < 0.80
	- NOISE: cluster_strength < 0.40

	These thresholds are applied after normalization and are intentionally different from legacy CBI thresholds because `cluster_strength` includes log-size scaling and recency.

4) Legacy per-observation formulas (kept for metrics / historical reference)

	- Behavior Weight (BW):

		BW = credibility^α × clarity_score^β × extraction_confidence^γ

		(α=0.35, β=0.40, γ=0.25 — implemented in `src/services/calculation_engine.py`)

	- Adjusted Behavior Weight (ABW):

		ABW = BW × (1 + reinforcement_count × r) × e^(-decay_rate × days_since_last_seen)

		(r ≈ 0.01 by default)

	- Cluster CBI (legacy):

		Cluster_CBI = Σ(ABW_i) / N

	These legacy formulas are used to compute per-observation metrics (BW/ABW) which feed into `mean_abw` for cluster calculations, but the pipeline uses `cluster_strength` + `confidence` for final tiering.

## Testing

Run backend tests:

```powershell
pytest tests/
```

There are also quick scripts in `tests/` for loading sample data and verifying Qdrant/Mongo contents.

## Configuration (`.env`) sample

```env
# Database
MONGODB_URL=mongodb://admin:admin123@localhost:27017/
MONGODB_DATABASE=cbac_system
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION=behavior_embeddings

# OpenAI / Azure
OPENAI_API_KEY=your-api-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_API_TYPE=azure
OPENAI_API_BASE=your-endpoint
OPENAI_API_VERSION=2024-02-01

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## Documentation

Read detailed design and conceptual docs in `docs/`, notably:

- `docs/BEHAVIORS_CLUSTERS_ARCHETYPES.md` — explanation of behaviors vs clusters vs archetypes and UI guidance.

## Development notes

- Frontend and backend are developed separately — run both during full-stack development.
- Design tokens used in frontend: `rounded-2xl`, `shadow-xl`, slate color palette; Tailwind utility classes throughout.

## Support

If you run into issues, check logs (`main.py` / frontend console), confirm MongoDB and Qdrant are reachable, and verify `.env` values.

---

This README was updated to reflect the current frontend, UI terminology, layout changes, and improved developer instructions.
