# AgriSage Setup Guide

## Complete Local Setup Instructions

### 1. Environment Setup
```bash
# Clone repository
git clone <your-repo-url>
cd AgriSage2

# Create Python virtual environment (recommended)
python -m venv agrisage_env
agrisage_env\Scripts\activate  # Windows
# source agrisage_env/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. API Keys Configuration
```bash
# Copy environment template
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env file with your API keys
notepad .env  # Windows
# nano .env  # Linux/Mac
```

Required API keys:
- **OpenWeatherMap:** Free tier available at https://openweathermap.org/api
- **DataGovIn:** Register at https://data.gov.in for market data access
- **Gemini:** Get API key from https://makersuite.google.com

### 3. Data Initialization
```bash
# Fetch live data from all APIs
python -m services.ingestion.reliable_api_fetcher

# Build vector search index
python -m services.rag.build_index
```

Expected output:
- Weather records: 120
- Soil records: 36
- Agricultural records: 9
- Market records: 2000
- Vector index: 6169 documents

### 4. Start Application
```bash
# Option A: One-click startup (recommended)
python scripts/start_demo.py

# Option B: Manual startup
# Terminal 1:
uvicorn services.api.app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2:
streamlit run frontend/streamlit_app.py --server.port 8501
```

### 5. Verify Setup
- Open http://localhost:8501
- Try query: "What is the current market price for rice?"
- Check that sources show "DataGovIn_API" (not fallback)
- Verify confidence scores are 85%+

## Troubleshooting

### Import Errors
```bash
# Always use module format for scripts
python -m services.ingestion.reliable_api_fetcher
python -m services.rag.build_index
```

### API Failures
- Check .env file exists and has valid keys
- Test individual APIs:
  - OpenWeatherMap: Check quota limits
  - DataGovIn: Verify API key registration
  - Gemini: Check billing/quota status

### Fallback Data Issues
If seeing "FALLBACK_MARKET_API_FAILED" instead of "DataGovIn_API":
```bash
# Clean old data and rebuild
python -c "import sqlite3; conn = sqlite3.connect('data/agrisage.db'); conn.execute('DELETE FROM real_mandi_prices WHERE source LIKE \"%FALLBACK%\"'); conn.commit(); conn.close()"
python -m services.rag.build_index
```

### Vector Index Corruption
```bash
# Delete and rebuild index
rmdir /s services\rag\chroma_db  # Windows
# rm -rf services/rag/chroma_db  # Linux/Mac
python -m services.rag.build_index
```

## Development Workflow

### Adding New Data Sources
1. Add fetcher method in `services/ingestion/reliable_api_fetcher.py`
2. Update database schema if needed
3. Modify `services/rag/build_index.py` to include new data
4. Rebuild vector index

### Extending Geographic Coverage
1. Add new districts to location list in `reliable_api_fetcher.py`
2. Update fallback logic in `datagovin_api_fetcher.py`
3. Re-run data ingestion

### Testing Changes
```bash
# Test data ingestion
python -m services.ingestion.reliable_api_fetcher

# Test vector search
python -m services.rag.build_index

# Test API
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d '{"user_id":"test","question":"rice price today","location":"Roorkee"}'
```
