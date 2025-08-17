#!/bin/bash
# AgriSage Demo Runner Script

echo "=== AgriSage MVP Demo Runner ==="
echo "This script will set up and run the complete AgriSage system"
echo

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.11+"
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Please install pip"
    exit 1
fi

echo "✅ Python and pip found"

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from .env.example"
    cp .env.example .env
    echo "📝 Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY=your_openai_key_here"
    echo "   - GEMINI_API_KEY=your_gemini_key_here (optional)"
    echo
    read -p "Press Enter after you've added your API keys to .env file..."
fi

# Run ETL
echo "🔄 Running ETL pipeline..."
python services/ingestion/etl_imd.py

if [ $? -ne 0 ]; then
    echo "❌ ETL failed. Check your data files in data/sample/"
    exit 1
fi

# Build vector index
echo "🧠 Building vector index..."
python services/rag/build_index.py

if [ $? -ne 0 ]; then
    echo "❌ Vector index build failed"
    exit 1
fi

# Test fallback rules
echo "🛡️  Testing fallback rules..."
python -c "
from services.rules_engine.fallback import irrigation_rule
print('Irrigation rule test:', irrigation_rule(20, 10))
print('✅ Fallback rules working')
"

# Start API server in background
echo "🚀 Starting API server..."
uvicorn services.api.app:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait for server to start
sleep 3

# Test API endpoint
echo "🧪 Testing API endpoint..."
curl -s -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo","question":"When should I irrigate wheat in Roorkee?","location":"Roorkee"}' \
  | python -m json.tool

if [ $? -eq 0 ]; then
    echo "✅ API test successful"
else
    echo "❌ API test failed"
    kill $API_PID
    exit 1
fi

echo
echo "🎉 AgriSage is now running!"
echo "📱 Open frontend/pwa/index.html in your browser"
echo "🌐 API available at: http://localhost:8000"
echo "📚 API docs at: http://localhost:8000/docs"
echo
echo "Press Ctrl+C to stop the server"

# Keep script running
wait $API_PID
