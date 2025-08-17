#!/usr/bin/env python3
"""
Build Chroma vector index for AgriSage RAG system
"""
import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path
import json

def load_data_from_db():
    """Load data from SQLite database for indexing"""
    db_path = Path("data/agri.db")
    if not db_path.exists():
        raise FileNotFoundError("Database not found. Run ETL first: python services/ingestion/etl_imd.py")
    
    conn = sqlite3.connect(db_path)
    documents = []
    metadatas = []
    ids = []
    
    # Weather forecast data
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, district, forecast_date, precip_prob, max_temp, min_temp 
        FROM weather_forecast
    """)
    for row in cursor.fetchall():
        doc_id, district, date, precip, max_temp, min_temp = row
        text = f"Weather forecast for {district} on {date}: {precip}% chance of precipitation, max temp {max_temp}°C, min temp {min_temp}°C"
        documents.append(text)
        metadatas.append({
            "source": "weather_forecast",
            "row_id": str(doc_id),
            "district": district,
            "date": date,
            "type": "weather"
        })
        ids.append(f"weather_{doc_id}")
    
    # Soil health data
    cursor.execute("""
        SELECT id, farmer_id, village, district, pH, N, P, K, organic_carbon, soil_moisture 
        FROM soil_card
    """)
    for row in cursor.fetchall():
        doc_id, farmer_id, village, district, ph, n, p, k, oc, moisture = row
        text = f"Soil analysis for {village}, {district}: pH {ph}, Nitrogen {n}, Phosphorus {p}, Potassium {k}, Organic Carbon {oc}%, Soil Moisture {moisture}%"
        documents.append(text)
        metadatas.append({
            "source": "soil_card",
            "row_id": str(doc_id),
            "district": district,
            "village": village,
            "type": "soil"
        })
        ids.append(f"soil_{doc_id}")
    
    # Market prices data
    cursor.execute("""
        SELECT id, date, commodity, mandi, price 
        FROM market_prices
    """)
    for row in cursor.fetchall():
        doc_id, date, commodity, mandi, price = row
        text = f"Market price for {commodity} at {mandi} on {date}: ₹{price} per unit"
        documents.append(text)
        metadatas.append({
            "source": "market_prices",
            "row_id": str(doc_id),
            "commodity": commodity,
            "mandi": mandi,
            "date": date,
            "type": "market"
        })
        ids.append(f"market_{doc_id}")
    
    # eNAM trade data (if available)
    cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name='enam_trades';
    """)
    if cursor.fetchone():
        cursor.execute("""
            SELECT rowid, date, commodity, mandi, trade_volume, price 
            FROM enam_trades
        """)
        for row in cursor.fetchall():
            doc_id, date, commodity, mandi, volume, price = row
            text = f"eNAM trade for {commodity} at {mandi} on {date}: {volume} units traded at ₹{price}"
            documents.append(text)
            metadatas.append({
                "source": "enam_trades",
                "row_id": str(doc_id),
                "commodity": commodity,
                "mandi": mandi,
                "date": date,
                "type": "trade"
            })
            ids.append(f"enam_{doc_id}")
    
    conn.close()
    return documents, metadatas, ids

def build_chroma_index():
    """Build Chroma vector database index"""
    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Loading data from database...")
    documents, metadatas, ids = load_data_from_db()
    
    if not documents:
        raise ValueError("No documents found in database. Run ETL first.")
    
    print(f"Found {len(documents)} documents to index")
    
    # Initialize Chroma client
    chroma_path = Path("services/rag/chroma_db")
    chroma_path.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(path=str(chroma_path))
    
    # Delete existing collection if it exists
    try:
        client.delete_collection("agri")
    except:
        pass
    
    # Create new collection
    collection = client.create_collection(
        name="agri",
        metadata={"description": "AgriSage agricultural knowledge base"}
    )
    
    print("Generating embeddings and building index...")
    
    # Add documents in batches to avoid memory issues
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_metas = metadatas[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]
        
        # Generate embeddings
        embeddings = model.encode(batch_docs).tolist()
        
        # Add to collection
        collection.add(
            embeddings=embeddings,
            documents=batch_docs,
            metadatas=batch_metas,
            ids=batch_ids
        )
        
        print(f"Processed batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
    
    print(f"Index built successfully with {len(documents)} documents")
    return collection

def test_index():
    """Test the built index with sample queries"""
    print("\nTesting index with sample queries...")
    
    chroma_path = Path("services/rag/chroma_db")
    client = chromadb.PersistentClient(path=str(chroma_path))
    collection = client.get_collection("agri")
    
    test_queries = [
        "When should I irrigate wheat in Roorkee?",
        "What is the soil pH in my area?",
        "Current market price for rice",
        "Weather forecast for tomorrow"
    ]
    
    for query in test_queries:
        results = collection.query(
            query_texts=[query],
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )
        
        print(f"\nQuery: {query}")
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0], 
            results['metadatas'][0], 
            results['distances'][0]
        )):
            print(f"  {i+1}. [{meta['source']}] {doc[:100]}... (distance: {dist:.3f})")

def main():
    """Main function to build and test index"""
    try:
        collection = build_chroma_index()
        test_index()
        print("\n✅ Vector index built successfully!")
        print("Next step: Start the API server with 'uvicorn services.api.app:app --reload'")
        
    except Exception as e:
        print(f"❌ Error building index: {e}")
        print("Make sure to run ETL first: python services/ingestion/etl_imd.py")

if __name__ == "__main__":
    main()
