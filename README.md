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

### Redis Configuration

StockSight uses Redis for high-performance caching with both synchronous and asynchronous clients. Configure Redis through environment variables:

```bash
REDIS_HOST=localhost      # Redis server host
REDIS_PORT=6379          # Redis server port
REDIS_DB=0              # Redis database number
REDIS_PASSWORD=         # Optional Redis password
```

### Cache Implementation

The caching system provides two implementations:

1. **Synchronous Cache** (`RedisCache`):
   - General-purpose caching for API responses and computed data
   - Automatic JSON serialization/deserialization
   - Configurable TTL (Time-To-Live) for cache entries
   - Built-in error handling and logging

```python
from services.cache import RedisCache, cache_result

# Direct cache usage
cache = RedisCache()
cache.set("my_key", {"data": "value"}, expire=3600)
data = cache.get("my_key")

# Decorator usage
@cache_result(prefix="market", expire=300)
async def get_market_data():
    # ... fetch market data ...
```

2. **Asynchronous Cache** (MarketStack Client):
   - Specialized for MarketStack API responses
   - Rate limiting and automatic retries
   - Async/await support
   - Request deduplication

### Cache Keys and Expiration

Predefined cache prefixes and TTLs for different data types:

- Market Data: 5 minutes TTL
- SEC Data: 24 hours TTL
- FDA Data: 24 hours TTL
- Search Results: 1 hour TTL

### Best Practices

1. **Key Generation**:
   - Use the `_generate_key()` method for consistent key creation
   - Include relevant parameters in cache keys
   - Avoid overly long or complex keys

2. **Error Handling**:
   - Cache failures are logged but don't break the application
   - Fallback to direct API calls when cache is unavailable
   - Automatic retry mechanism for failed cache operations

3. **Performance Optimization**:
   - Use appropriate TTLs based on data volatility
   - Implement batch operations where possible
   - Monitor cache hit/miss ratios

4. **Memory Management**:
   - Set reasonable expiration times
   - Use compression for large values
   - Implement cache eviction policies

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
