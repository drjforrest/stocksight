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

- Added ML-powered stock movement predictions
- Implemented competitor analysis features
- Enhanced IPO tracking capabilities
- Integrated news sentiment analysis
- Added Redis caching for improved performance

## 📈 Performance

- Real-time data updates every 5 minutes
- Sub-second response times for most endpoints
- Cached responses for expensive computations
- Scalable architecture for high concurrency

## 🛠 Contributing

We welcome contributions! Please check our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
