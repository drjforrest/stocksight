from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Add the parent directory to sys.path if running directly
if __name__ == "__main__":
    sys.path.append(str(Path(__file__).parent.parent))

from api.routes import stock, indices, competitors, ipo, news
from api.routes.endpoints import tracked, rss, companies, browse, news_endpoints

app = FastAPI(
    title="StockSight API",
    description="""
    StockSight API provides comprehensive market data and analysis for biotech stocks.
    
    Key Features:
    - Real-time stock price data
    - Historical price analysis
    - Company information and financials
    - Competitor analysis and comparisons
    - IPO tracking and analysis
    - News sentiment analysis
    - Market indices monitoring
    - Exchange information
    - Company tracking and personalized news feeds
    - RSS feed generation for tracked companies
    - FDA drug application tracking
    - SEC filing analysis
    
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
        },
        {
            "name": "competitors",
            "description": "Biotech competitor analysis, including financials, patents, and market share"
        },
        {
            "name": "ipos",
            "description": "Biotech IPO tracking, including upcoming listings, pricing, and performance analysis"
        },
        {
            "name": "news",
            "description": "News aggregation and sentiment analysis for biotech companies"
        },
        {
            "name": "tracked",
            "description": "Manage tracked companies and personalized news feeds"
        },
        {
            "name": "rss",
            "description": "Generate RSS feeds for tracked companies"
        },
        {
            "name": "companies",
            "description": "Comprehensive company data including market, SEC, and FDA information"
        },
        {
            "name": "browse",
            "description": "Browse companies and their information"
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
app.include_router(competitors.router)
app.include_router(ipo.router)
app.include_router(news.router)
app.include_router(news_endpoints.router, prefix="/api/news/endpoints")
app.include_router(tracked.router, prefix="/api/tracked")
app.include_router(rss.router, prefix="/api/rss")
app.include_router(companies.router, prefix="/api/companies")
app.include_router(browse.router, prefix="/api/browse")

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