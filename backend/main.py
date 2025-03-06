from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import stock, indices

app = FastAPI(
    title="StockSight API",
    description="""
    StockSight API provides comprehensive market data and analysis for biotech stocks.
    
    Features:
    - Real-time stock price data
    - Historical price analysis
    - Company information
    - Dividend history
    - Stock splits tracking
    - Market indices monitoring
    - Exchange information
    
    All endpoints are documented with examples and detailed parameter descriptions.
    Rate limits and data freshness are handled automatically.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "stocks",
            "description": "Operations with stock data, including prices, company info, dividends, and splits"
        },
        {
            "name": "indices",
            "description": "Market index data and analysis"
        }
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stock.router)
app.include_router(indices.router)

@app.get("/")
async def root():
    """
    Root endpoint returning API information and documentation links.
    
    Returns:
    - Welcome message
    - Links to API documentation:
        - Swagger UI (/docs)
        - ReDoc (/redoc)
    
    Examples:
    ```json
    {
        "message": "Welcome to StockSight API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
    ```
    """
    return {
        "message": "Welcome to StockSight API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
