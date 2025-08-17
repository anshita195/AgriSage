# AgriSage MVP

Agricultural advisory system combining public datasets, RAG (Retrieval Augmented Generation), and safety fallbacks.

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment: Copy `.env.example` to `.env` and add your API keys
3. Run ETL: `python services/ingestion/etl_imd.py`
4. Build vector index: `python services/rag/build_index.py`
5. Start API: `uvicorn services.api.app:app --host 0.0.0.0 --port 8000`
6. Open PWA: `frontend/pwa/index.html`

## Data Sources

- **IMD** - India Meteorological Department (district forecasts)
- **Soil Health Card** - soilhealth.dac.gov.in
- **AGMARKNET** - Market prices via data.gov.in
- **eNAM** - Trade data from enam.gov.in

## Architecture

- **ETL Pipeline** - Processes CSV data into SQLite
- **Vector Index** - Chroma DB with sentence-transformers
- **RAG API** - FastAPI with OpenAI/Gemini LLM
- **Safety Rules** - Fallback engine for critical decisions
- **PWA Frontend** - Progressive Web App with offline support

## API Usage

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"u1","question":"When should I irrigate wheat in Roorkee?","location":"Roorkee"}'
```

## License

Uses public datasets under their respective licenses.
