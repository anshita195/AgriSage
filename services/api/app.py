#!/usr/bin/env python3
"""
FastAPI server for AgriSage RAG system
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
import requests
import os
from pathlib import Path
import json
from typing import Optional, List, Dict
import sqlite3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import fallback rules
import sys
sys.path.append(str(Path(__file__).parent.parent))
from rules_engine.fallback import get_fallback_response, safety_check
from rag.prompts import PROMPT_TEMPLATE

app = FastAPI(title="AgriSage API", description="Agricultural Advisory RAG System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
chroma_client = None
collection = None
sentence_model = None
gemini_api_key = None

class QueryRequest(BaseModel):
    user_id: str
    question: str
    location: Optional[str] = None
    locale: Optional[str] = "en"

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    provenance: List[Dict]
    escalate: Optional[bool] = False
    fallback_used: Optional[bool] = False

@app.on_event("startup")
async def startup_event():
    """Initialize models and connections on startup"""
    global chroma_client, collection, sentence_model, gemini_api_key
    
    try:
        # Initialize sentence transformer
        print("Loading sentence transformer...")
        sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize Chroma client
        chroma_path = Path("services/rag/chroma_db")
        if not chroma_path.exists():
            raise FileNotFoundError("Chroma database not found. Run: python services/rag/build_index.py")
        
        chroma_client = chromadb.PersistentClient(path=str(chroma_path))
        collection = chroma_client.get_collection("agri")
        print("Chroma database loaded")
        
        # Initialize Gemini API key
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            print("Gemini API key loaded")
        else:
            print("Warning: GEMINI_API_KEY not found in environment")
        
        print("AgriSage API server started successfully!")
        
    except Exception as e:
        print(f"Error during startup: {e}")
        raise

def get_context_from_db(location: str = None) -> Dict:
    """Get additional context from database based on location"""
    context = {}
    
    try:
        db_path = Path("data/agri.db")
        if not db_path.exists():
            return context
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        if location:
            # Get recent weather for location
            cursor.execute("""
                SELECT precip_prob, max_temp, min_temp, soil_moisture 
                FROM weather_forecast w
                LEFT JOIN soil_card s ON w.district = s.district
                WHERE w.district LIKE ? 
                ORDER BY w.forecast_date DESC LIMIT 1
            """, (f"%{location}%",))
            
            result = cursor.fetchone()
            if result:
                context.update({
                    'precip_prob': result[0],
                    'max_temp': result[1], 
                    'min_temp': result[2],
                    'soil_moisture': result[3]
                })
        
        conn.close()
    except Exception as e:
        print(f"Error getting context from DB: {e}")
    
    return context

def retrieve_documents(query: str, k: int = 5) -> tuple:
    """Retrieve relevant documents from vector database"""
    try:
        results = collection.query(
            query_texts=[query],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        documents = results['documents'][0]
        metadatas = results['metadatas'][0] 
        distances = results['distances'][0]
        
        # Calculate retrieval score (lower distance = higher score)
        max_distance = max(distances) if distances else 1.0
        retrieval_scores = [(max_distance - d) / max_distance for d in distances]
        avg_retrieval_score = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0.0
        
        return documents, metadatas, avg_retrieval_score
        
    except Exception as e:
        print(f"Error retrieving documents: {e}")
        return [], [], 0.0

def call_gemini_llm(prompt: str) -> tuple:
    """Call Google Gemini LLM and return response with confidence"""
    try:
        if not gemini_api_key:
            print("Gemini API key not available")
            return None, 0.0
        
        # Gemini API endpoint - using gemini-1.5-flash (current available model)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": f"You are AgriSage, an AI agricultural advisor for Indian farmers. Always end your response with a confidence score between 0.0 and 1.0.\n\n{prompt}"
                }]
            }],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 500,
                "topP": 0.8,
                "topK": 10
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'candidates' in result and len(result['candidates']) > 0:
                answer = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Try to extract confidence from response
                llm_confidence = 0.7  # default
                if "confidence:" in answer.lower():
                    try:
                        conf_part = answer.lower().split("confidence:")[-1].strip()
                        conf_num = float(conf_part.split()[0])
                        if 0.0 <= conf_num <= 1.0:
                            llm_confidence = conf_num
                    except:
                        pass
                
                return answer, llm_confidence
            else:
                print("No candidates in Gemini response")
                return None, 0.0
        else:
            print(f"Gemini API error: {response.status_code} - {response.text}")
            return None, 0.0
        
    except Exception as e:
        print(f"Error calling Gemini LLM: {e}")
        return None, 0.0

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """Main RAG endpoint for agricultural questions"""
    
    # Safety check first
    if safety_check(request.question):
        return QueryResponse(
            answer="This question involves chemicals or dosages that require expert consultation. Please contact your local agricultural extension officer or Krishi Vigyan Kendra for safe recommendations.",
            confidence=1.0,
            provenance=[],
            escalate=True
        )
    
    try:
        # Retrieve relevant documents
        documents, metadatas, retrieval_score = retrieve_documents(request.question)
        
        if not documents:
            # Use fallback rules if no documents found
            context = get_context_from_db(request.location)
            fallback_result = get_fallback_response(request.question, context)
            
            return QueryResponse(
                answer=fallback_result["advice"],
                confidence=fallback_result["confidence"],
                provenance=[],
                escalate=fallback_result.get("escalate", False),
                fallback_used=True
            )
        
        # Build context for LLM
        context_text = "\n\n".join([
            f"Source: {meta['source']} (ID: {meta['row_id']})\nContent: {doc}"
            for doc, meta in zip(documents, metadatas)
        ])
        
        # Create prompt
        prompt = PROMPT_TEMPLATE.format(
            context=context_text,
            question=request.question,
            location=request.location or "Not specified"
        )
        
        # Call Gemini LLM
        llm_response, llm_confidence = call_gemini_llm(prompt)
        
        if not llm_response:
            # Fallback to rules engine
            context = get_context_from_db(request.location)
            fallback_result = get_fallback_response(request.question, context)
            
            return QueryResponse(
                answer=fallback_result["advice"],
                confidence=fallback_result["confidence"],
                provenance=[],
                escalate=fallback_result.get("escalate", False),
                fallback_used=True
            )
        
        # Calculate combined confidence
        combined_confidence = 0.6 * retrieval_score + 0.4 * llm_confidence
        
        # Check if we should escalate
        should_escalate = combined_confidence < 0.4 or "ESCALATE" in llm_response
        
        if should_escalate:
            context = get_context_from_db(request.location)
            fallback_result = get_fallback_response(request.question, context)
            
            return QueryResponse(
                answer=fallback_result["advice"],
                confidence=fallback_result["confidence"],
                provenance=[],
                escalate=True,
                fallback_used=True
            )
        
        # Build provenance
        provenance = [
            {
                "source": meta["source"],
                "row_id": meta["row_id"],
                "content": doc[:200] + "..." if len(doc) > 200 else doc
            }
            for meta, doc in zip(metadatas[:3], documents[:3])  # Top 3 sources
        ]
        
        return QueryResponse(
            answer=llm_response,
            confidence=combined_confidence,
            provenance=provenance,
            escalate=False
        )
        
    except Exception as e:
        print(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "chroma_connected": collection is not None,
        "model_loaded": sentence_model is not None,
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY"))
    }

@app.post("/fallback")
async def fallback_endpoint(request: QueryRequest):
    """Direct access to fallback rules engine"""
    context = get_context_from_db(request.location)
    result = get_fallback_response(request.question, context)
    
    return QueryResponse(
        answer=result["advice"],
        confidence=result["confidence"],
        provenance=[],
        escalate=result.get("escalate", False),
        fallback_used=True
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
