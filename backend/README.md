# Pata Backend

Backend MVP for Pata — Location Intelligence for Last-Mile Delivery.

## Overview

This backend accepts messy Indian delivery addresses and returns structured address parsing, geocoding, confidence, evidence, corrections, latency metrics, and estimated cost.

## Backend Structure

- `app/main.py`: FastAPI application entrypoint
- `app/config.py`: configuration and environment loading
- `app/api/routes.py`: API endpoints
- `app/models/`: request and response models
- `app/services/`: business logic and scoring
- `app/infrastructure/`: external service clients and cache
- `app/utils/`: normalization, timing, distance, language helpers
- `app/data/pincode/`: pincode CSV reference data
- `app/tests/`: tests with pytest

## Data Residency & Privacy

This backend keeps raw addresses in memory only during request processing. It does not persist raw address strings to logs, cache keys, or external analytics.

The system is designed for local deployment and can be hosted on India-based infrastructure to align with DPDP Act data residency requirements.

## Startup

1. Copy `.env.example` to `.env`
2. Place the pincode CSV at `app/data/pincode/all_india_pincode_2025.csv`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start with Uvicorn:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API

- `POST /api/v1/geocode`
- `GET /health`

## Notes

- The backend uses a deterministic fallback parser if Ollama is unavailable or returns invalid output.
- Overpass requests are capped at 250ms. Failures degrade gracefully.
- Evidence and corrections are included in every response.
