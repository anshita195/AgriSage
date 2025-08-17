#!/usr/bin/env python3
"""
ETL pipeline for AgriSage - processes CSV datasets into SQLite database
"""
import sqlite3
import pandas as pd
import os
from pathlib import Path

def create_database():
    """Create SQLite database and tables"""
    db_path = Path("data/agri.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Weather forecast table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_forecast (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            district TEXT,
            forecast_date TEXT,
            precip_prob REAL,
            max_temp REAL,
            min_temp REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Soil health card table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS soil_card (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            row_id TEXT,
            farmer_id TEXT,
            village TEXT,
            district TEXT,
            pH REAL,
            N REAL,
            P REAL,
            K REAL,
            organic_carbon REAL,
            soil_moisture REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Market prices table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            row_id TEXT,
            date TEXT,
            commodity TEXT,
            mandi TEXT,
            price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # eNAM trade data table (optional)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enam_trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            commodity TEXT,
            mandi TEXT,
            trade_volume REAL,
            price REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    return conn

def load_csv_data(conn):
    """Load CSV data into database tables"""
    data_dir = Path("data/sample")
    
    # Load IMD weather data
    imd_file = data_dir / "imd_sample.csv"
    if imd_file.exists():
        df = pd.read_csv(imd_file)
        df.to_sql('weather_forecast', conn, if_exists='append', index=False)
        print(f"Loaded {len(df)} rows from IMD data")
    else:
        print(f"Warning: {imd_file} not found")
    
    # Load soil health data
    soil_file = data_dir / "soil_sample.csv"
    if soil_file.exists():
        df = pd.read_csv(soil_file)
        df.to_sql('soil_card', conn, if_exists='append', index=False)
        print(f"Loaded {len(df)} rows from Soil Health data")
    else:
        print(f"Warning: {soil_file} not found")
    
    # Load market prices
    market_file = data_dir / "market_sample.csv"
    if market_file.exists():
        df = pd.read_csv(market_file)
        df.to_sql('market_prices', conn, if_exists='append', index=False)
        print(f"Loaded {len(df)} rows from Market data")
    else:
        print(f"Warning: {market_file} not found")
    
    # Load eNAM data (optional)
    enam_file = data_dir / "enam_sample.csv"
    if enam_file.exists():
        df = pd.read_csv(enam_file)
        df.to_sql('enam_trades', conn, if_exists='append', index=False)
        print(f"Loaded {len(df)} rows from eNAM data")
    else:
        print(f"Info: {enam_file} not found (optional)")

def main():
    """Main ETL process"""
    print("Starting AgriSage ETL pipeline...")
    
    # Create database and tables
    conn = create_database()
    print("Database and tables created")
    
    # Load CSV data
    load_csv_data(conn)
    
    # Verify data
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Created tables: {[t[0] for t in tables]}")
    
    # Show row counts
    for table_name in ['weather_forecast', 'soil_card', 'market_prices', 'enam_trades']:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"{table_name}: {count} rows")
    
    conn.close()
    print("ETL pipeline completed successfully!")

if __name__ == "__main__":
    main()
