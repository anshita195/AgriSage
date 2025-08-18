# AgriSage: AI-Powered Agricultural Advisory System

A production-ready agricultural advisory system that provides farmers with real-time, data-driven insights using a Retrieval-Augmented Generation (RAG) pipeline. Combines live data from authoritative sources with large language model synthesis for safe, accurate agricultural guidance.

## 🏗️ Architecture

**Core Pipeline:** Data Ingestion → Vector Indexing → Query Processing
- **Backend:** FastAPI + Gemini LLM
- **Frontend:** Streamlit chat interface
- **Database:** SQLite + ChromaDB vector store
- **Data Sources:** 4 live APIs (Weather, Soil, Agricultural, Markets)

## 📊 Live Data Sources

| Source | API | Records | Coverage |
|--------|-----|---------|----------|
| Weather | OpenWeatherMap | 120 | 3 districts, 5-day forecasts |
| Soil | SoilGrids ISRIC | 36 | Global pH, nutrients, composition |
| Agricultural | NASA POWER | 9 | Temperature, precipitation, solar |
| Markets | DataGovIn | 2000 | Live mandi prices with multi-state fallback |

**Geographic Coverage:** Uttarakhand (Dehradun, Roorkee, Haridwar) with fallback to UP/Haryana/Punjab  
**Commodities:** Rice, Wheat, Mustard, Maize, Sugarcane, Soybean, Cotton, Onion, Potato, Tomato

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- API keys for OpenWeatherMap, DataGovIn, Gemini

### Installation
```bash
# Clone and navigate
git clone <repo-url>
cd AgriSage2

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys:
# OPENWEATHER_API_KEY=your_key
# DATA_GOV_IN_API_KEY=your_key  
# GEMINI_API_KEY=your_key
```

### Data Setup
```bash
# Fetch live data from APIs
python -m services.ingestion.reliable_api_fetcher

# Build vector index
python -m services.rag.build_index
```

### Run Application
```bash
# Option 1: One-click startup (recommended)
python scripts/start_demo.py

# Option 2: Manual startup
# Terminal 1: Backend API
uvicorn services.api.app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend UI
streamlit run frontend/streamlit_app.py --server.port 8501
```

### Access URLs
- **Main UI:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

## 📁 Directory Structure

```
AgriSage2/
├── services/
│   ├── api/app.py                    # FastAPI backend with RAG
│   ├── rag/build_index.py           # Vector indexing
│   └── ingestion/
│       ├── reliable_api_fetcher.py  # Data orchestrator
│       └── datagovin_api_fetcher.py # Market API with fallback
├── frontend/
│   └── streamlit_app.py             # Main chat interface
├── scripts/
│   └── start_demo.py                # One-click startup
├── data/
│   ├── agrisage.db                  # SQLite database
│   └── sample/                      # Fallback CSV data
├── requirements.txt                 # Python dependencies
└── .env                            # API keys (create from .env.example)
```

## 🔧 Core Features

### Working Capabilities
- ✅ Multi-modal agricultural queries (weather + soil + market + agro)
- ✅ Vector similarity search (6169 documents)
- ✅ Confidence scoring & provenance tracking
- ✅ Safety gates preventing hallucinations
- ✅ Geographic fallback logic for data availability

### Query Examples
- "When should I irrigate wheat in Roorkee?"
- "What is the current market price for rice?"
- "What's the soil pH in my area?"
- "Weather forecast for next 3 days"

## 🔄 Data Refresh Workflow

```bash
# 1. Fetch fresh data from APIs
python -m services.ingestion.reliable_api_fetcher

# 2. Rebuild vector index
python -m services.rag.build_index

# 3. Restart services (or use start_demo.py)
```

## 🎯 Performance Metrics

- **Vector Index:** 6169 documents
- **Response Time:** <2 seconds
- **Data Freshness:** Live APIs updated daily
- **Confidence Scores:** 85-98% for live data queries

## 🔒 Production Features

- Error handling and logging
- API rate limiting and timeouts
- Database connection pooling
- Environment variable management
- Docker containerization support

## 📋 API Keys Required

Create `.env` file with:
```
OPENWEATHER_API_KEY=your_key
DATA_GOV_IN_API_KEY=your_key  
GEMINI_API_KEY=your_key
```

### Getting API Keys
1. **OpenWeatherMap:** https://openweathermap.org/api
2. **DataGovIn:** https://data.gov.in
3. **Gemini:** https://makersuite.google.com

## 🐛 Troubleshooting

### Common Issues
```bash
# Import errors when running scripts
python -m services.ingestion.reliable_api_fetcher  # Use module format

# Vector index errors
python -m services.rag.build_index  # Rebuild if corrupted

# API failures
# Check .env file and API key validity
```

### Data Refresh
If seeing fallback data instead of live data:
1. Run data ingestion script
2. Rebuild vector index
3. Restart application

## 🏆 Hackathon Highlights

- **Multi-modal RAG:** Combines weather, soil, agricultural, and market data
- **Safety-First:** Prevents hallucinations with confidence scoring
- **Geographic Intelligence:** Multi-state fallback for data availability
- **Production-Ready:** Robust error handling and monitoring
- **Real APIs:** Live data from authoritative government/scientific sources

## License

MIT License
