# StockSight Backend

FastAPI-based backend for the StockSight application, providing comprehensive biotech stock market data and analysis.

## Installation

```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Running the Application

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Features

- Real-time stock price data
- Historical price analysis
- Company information
- Dividend history
- Stock splits tracking
- Market indices monitoring
- Exchange information

## Development

### Code Style

The project uses:

- Black for code formatting
- isort for import sorting
- mypy for type checking
- flake8 for linting

### Testing

```bash
pytest
```

## Environment Variables

Create a `.env` file in the root directory with:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/stocksight
MARKETSTACK_API_KEY=your_api_key_here
```
