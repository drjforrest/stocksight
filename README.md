# StockSight

A FastAPI-based API for biotech stock market data and analysis.

## Installation

```bash
pip install -e .
```

## Running the Application

```bash
uvicorn backend.main:app --reload
```

## API Documentation

Once running, visit:
- http://localhost:8000/docs for Swagger UI
- http://localhost:8000/redoc for ReDoc

## Features

- Real-time stock price data
- Historical price analysis
- Company information
- Dividend history
- Stock splits
- Market indices tracking
- Exchange information

# StockSight Project Setup Documentation

## Project Overview

StockSight is an IPO insights application designed to provide real-time stock tracking, IPO performance analysis, and market sentiment insights. The project is structured with a Python FastAPI backend, a React TypeScript frontend (Next.js), and a PostgreSQL database for data storage and analysis.

---

## 1. Initial Project Structure Setup

### Directory Structure Created:

```
stocksight/
├── backend/              # FastAPI backend
│   ├── app/
│   ├── models/
│   ├── services/
│   ├── config/
│   ├── venv/             # Python virtual environment
│   ├── main.py           # FastAPI entry point
├── frontend/             # Next.js frontend
├── database/             # PostgreSQL migrations
│   ├── migrations/
│   │   ├── script.py.mako
│   │   ├── versions/
│   ├── alembic.ini       # Alembic migration config
│   ├── env.py            # Environment variables for database
│   ├── README
```

---

## 2. Backend Setup

### **1. FastAPI Installation & Environment Setup**

```bash
mkdir -p backend/{app,models,services,config}
cd backend
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn psycopg2 requests python-dotenv
```

### **2. FastAPI Entry Point (main.py)**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to StockSight API"}
```

### **3. Running the FastAPI Server**

```bash
uvicorn main:app --reload
```

Expected output:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

To test:

```bash
curl http://127.0.0.1:8000/
```

Expected response:

```json
{"message": "Welcome to StockSight API"}
```

---

## 3. PostgreSQL Setup

### **1. Create Database & User**

```bash
createdb stocksight
psql stocksight
```

Inside PostgreSQL prompt:

```sql
CREATE USER stocksight_user WITH PASSWORD 'stocksight_user1484';
GRANT ALL PRIVILEGES ON DATABASE stocksight TO stocksight_user;
```

### **2. Create Stock Prices Table**

```sql
CREATE TABLE stock_prices (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    timestamp TIMESTAMP DEFAULT NOW()
);
GRANT ALL PRIVILEGES ON TABLE stock_prices TO stocksight_user;
```

### **3. Database Connection in FastAPI**

```python
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
```

To test database connection:

```python
@app.get("/db-test")
def test_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM stock_prices;")
    count = cur.fetchone()[0]
    cur.close()
    conn.close()
    return {"message": f"Database is connected. {count} records in stock_prices table."}
```

Test with:

```bash
curl http://127.0.0.1:8000/db-test
```

---

## 4. Alembic Migrations Fix

### **Issue:**

Alembic migrations were incorrectly nested under `migrations/migrations/`.

### **Fix:**

```bash
mv migrations/migrations/* migrations/
mv migrations/migrations/.* migrations/ 2>/dev/null
rm -r migrations/migrations
```

### **Final Folder Structure After Fix:**

```
.
├── alembic.ini
├── README
├── env.py
└── migrations/
    ├── script.py.mako
    ├── versions/
```

Alembic is now correctly set up. You can run:

```bash
alembic upgrade head
```

To apply migrations.

---

## 5. Next Steps

1. **Integrate MarketStack API** to fetch real-time stock data.
2. **Develop Next.js frontend** with TypeScript & Tailwind CSS.
3. **Build API endpoints** for stock tracking & analysis.

StockSight is now ready for further development! 🚀
