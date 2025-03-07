# StockSight

A sophisticated FastAPI-based platform for biotech stock market analysis and IPO insights.

## 🧬 Overview

StockSight is a specialized platform designed for biotech investors and analysts, providing comprehensive market data analysis, competitor tracking, and IPO insights. Our platform combines real-time market data with advanced analytics to deliver actionable insights for the biotech sector.

## ⚡ Key Features

### Market Analysis
- Real-time biotech stock price tracking
- Advanced technical analysis with ML-powered predictions
- Historical price analysis with customizable timeframes
- Market sentiment analysis with news integration

### IPO Insights
- Comprehensive IPO tracking and analysis
- Success rate predictions based on historical data
- Pricing trends analysis
- Post-IPO performance tracking

### Competitor Analysis
- Detailed competitor profiling
- Patent portfolio tracking
- Pipeline development monitoring
- Market share analysis
- Financial metrics comparison

### News & Sentiment
- Real-time news aggregation
- Sentiment analysis for biotech news
- Impact analysis on stock performance
- Topic trend analysis

## 🚀 Getting Started

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/stocksight.git
cd stocksight

# Install dependencies
pip install -e .
```

### Configuration

1. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your MarketStack API key and database credentials
```

2. Initialize the database:
```bash
alembic upgrade head
```

### Running the Application

```bash
uvicorn backend.main:app --reload
```

## 📚 API Documentation

Once running, access the interactive API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 Technical Stack

- **Backend**: FastAPI, Python 3.12+
- **Database**: PostgreSQL with SQLAlchemy
- **Cache**: Redis for performance optimization
- **APIs**: MarketStack integration
- **Analysis**: 
  - pandas for data manipulation
  - scikit-learn for ML predictions
  - statsmodels for time series analysis

## 💾 Caching System

The application uses Redis for caching frequently accessed data. The caching system provides both synchronous and asynchronous interfaces:

1. **Cache Service** (`CacheService`):
   - Provides both sync and async methods for caching operations
   - Configurable expiration times
   - Automatic serialization/deserialization
   - Function result caching decorator

Example usage:

```python
from services.cache import CacheService, cache_result

# Initialize cache
cache = CacheService()

# Using sync methods
cache.set("key", "value", expire=3600)  # Cache for 1 hour
value = cache.get("key")

# Using async methods
await cache.aset("key", "value", expire=3600)
value = await cache.aget("key")

# Using the decorator
@cache_result(prefix="my_data", expire=3600)
async def get_data():
    return await fetch_expensive_data()
```

## 🧬 Biotech Features

### Data Model

The platform includes specialized tables for biotech industry analysis:

1. **Therapeutic Areas**:
   - Categorization of drug development focus
   - Hierarchical organization of disease areas
   - Relationship mapping between companies and therapeutic areas

2. **Clinical Trials**:
   - Comprehensive trial tracking across phases
   - Integration with company profiles
   - Status monitoring and updates
   - Therapeutic area associations

3. **IPO Updates**:
   - Real-time tracking of IPO status changes
   - Historical valuation data
   - Market response metrics
   - Competitor impact analysis

### Competitor Analysis

Enhanced competitor tracking with:

1. **Scoring Metrics**:
   - Market volatility assessment
   - IPO performance tracking
   - Patent portfolio strength
   - Pipeline development score

2. **Market Position**:
   - Relative market cap analysis
   - Therapeutic area market share
   - Clinical trial success rates
   - Patent position strength

### Visualization Features

Interactive charts and analytics:

1. **Market Cap Distribution**:
   - Sector-wide distribution analysis
   - Peer group comparisons
   - Historical trends

2. **Clinical Pipeline**:
   - Phase distribution charts
   - Success rate visualization
   - Timeline projections

3. **Therapeutic Focus**:
   - Area concentration analysis
   - Market opportunity mapping
   - Competitor positioning

## 📊 Analysis & Algorithms

### Company Analysis Pipeline

1. **Market Data Collection**:
   - SEC data integration for market cap and financial metrics
   - FDA data integration for drug approvals and clinical trials
   - Real-time stock price tracking
   - Patent portfolio analysis

2. **Therapeutic Area Classification**:
   ```python
   @cache_result("browse:therapeutic", SEARCH_RESULTS_EXPIRY)
   async def get_therapeutic_areas():
       # Fetches and categorizes therapeutic areas from FDA data
       # Uses product classifications and trial categories
       # Returns sorted, deduplicated list of areas
   ```

3. **Company Filtering & Scoring**:
   - Market Cap Analysis:
     - Filters companies by market capitalization range
     - Converts raw values to billions for standardization
     - Supports min/max range filtering
   
   - Clinical Pipeline Evaluation:
     ```python
     # Example filtering criteria
     {
         "therapeutic_areas": ["Oncology", "Immunology"],
         "clinical_trials": {
             "phase1": [...],
             "phase2": [...],
             "phase3": [...],
             "phase4": [...]
         }
     }
     ```

### Competitor Analysis Algorithm

1. **Data Collection Layer**:
   - SEC Integration:
     - Company tickers and CIK numbers
     - Market capitalization data
     - Financial statements
   - FDA Integration:
     - Drug approvals
     - Clinical trial statuses
     - Therapeutic area classifications

2. **Filtering & Matching**:
   ```python
   # Pseudo-code for competitor matching
   def match_competitors(company):
       return {
           "direct_competitors": # Same therapeutic areas & market cap range
           "pipeline_competitors": # Similar clinical trial phases
           "market_competitors": # Similar market cap & business model
       }
   ```

3. **Scoring Metrics**:
   - Market Position Score:
     - Market cap relative to peer group
     - Revenue growth trajectory
     - Market share in therapeutic areas
   
   - Pipeline Strength Score:
     - Number of trials by phase
     - Historical trial success rates
     - Diversity of therapeutic areas
   
   - Innovation Score:
     - Patent portfolio strength
     - R&D investment ratio
     - Novel therapeutic approaches

4. **Real-time Updates**:
   - Continuous monitoring of:
     - Stock price movements
     - Clinical trial updates
     - Patent filings
     - FDA approvals
   - Automatic score recalculation
   - Trend analysis and alerts

### Data Integration Architecture

```
[SEC API] → Market Data → Competitor Service
    ↓
[FDA API] → Clinical Data  →     ↓
    ↓                    Analysis Engine
[Patent DB] → IP Data   →     ↓
    ↓                    Scoring System
[News API] → Sentiment →      ↓
                        Results Cache
```

### Performance Optimizations

1. **Caching Strategy**:
   - Therapeutic area cache: 1 hour expiry
   - Company data cache: 24 hour expiry
   - Market cap cache: 1 hour expiry
   - Search results cache: Configurable expiry

2. **Query Optimization**:
   - Batched SEC data requests
   - Parallel FDA data fetching
   - Incremental updates
   - Connection pooling

3. **Response Time Targets**:
   - Browse endpoint: < 200ms
   - Company detail: < 100ms
   - Competitor analysis: < 500ms
   - Market data: Real-time

### Example API Usage

```python
# Get competitors in therapeutic area
response = await browse_service.browse_companies(
    therapeutic_area="Oncology",
    market_cap_min=1.0,  # $1B minimum
    market_cap_max=10.0, # $10B maximum
    has_approved_drugs=True,
    phase="3"  # Phase 3 trials
)

# Analyze competitor positioning
competitors = response["results"]
for competitor in competitors:
    print(f"Company: {competitor['name']}")
    print(f"Market Cap: ${competitor['market_cap']}B")
    print(f"Therapeutic Areas: {competitor['therapeutic_areas']}")
    print(f"Approved Drugs: {len(competitor['approved_drugs'])}")
    print(f"Clinical Trials: {competitor['clinical_trials']}")
```

## 📊 Example Usage

### Fetch Stock Analysis
```python
import requests

# Get stock prediction
response = requests.get(
    "http://localhost:8000/stocks/MRNA/predict",
    params={"days_ahead": 30}
)
prediction = response.json()

# Get competitor analysis
response = requests.get(
    "http://localhost:8000/competitors/analysis/market-share",
    params={"therapeutic_area": "mRNA vaccines"}
)
market_share = response.json()
```

### Track IPO Performance
```python
# Get upcoming IPOs in biotech
response = requests.get(
    "http://localhost:8000/ipos/upcoming",
    params={"therapeutic_area": "gene therapy"}
)
upcoming_ipos = response.json()
```

## 🔄 Recent Updates

- Enhanced biotech schema with therapeutic areas and clinical trials tracking
- Improved competitor analysis with advanced scoring metrics
- Added interactive visualizations for market analysis
- Upgraded Redis caching system with async support
- Implemented comprehensive error handling and logging
- Added detailed documentation and usage examples
- Optimized database queries and cache performance
- Enhanced IPO tracking with real-time updates

## 📈 Performance

- Real-time data updates every 5 minutes
- Sub-second response times for most endpoints
- Cached responses for expensive computations
- Scalable architecture for high concurrency

## 🛠 Contributing

We welcome contributions! Please check our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
