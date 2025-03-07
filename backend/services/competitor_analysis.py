import requests
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("MARKETSTACK_API_KEY")

class CompetitorAnalyzer:
    def __init__(self, db):
        self.db = db
        self.scaler = MinMaxScaler(feature_range=(0, 100))

    def get_stock_data(self, symbol: str):
        """Fetch stock price, market cap, and growth trend"""
        url = f"http://api.marketstack.com/v1/tickers/{symbol}"
        response = requests.get(url, params={"access_key": API_KEY})
        return response.json()

    def calculate_score(self, company_data):
        """Compute a competitiveness score"""
        industry_match = 1 if company_data["sector"] in ["Biotechnology", "AI Pharma"] else 0.5
        market_cap_score = np.log10(company_data.get("market_cap", 1)) / 10
        ipo_status_score = 1 if company_data.get("ipo_status") == "RECENT" else 0.5
        funding_score = min(company_data.get("funding", 1) / 1e9, 1)

        final_score = (0.3 * industry_match) + (0.25 * market_cap_score) + \
                      (0.2 * ipo_status_score) + (0.15 * funding_score) + \
                      (0.1 * np.random.rand())  # Random noise for uniqueness
        
        return round(final_score * 100, 2)

    def analyze_company(self, symbol: str):
        """Fetch and score a company"""
        company_data = self.get_stock_data(symbol)
        score = self.calculate_score(company_data)
        return {"symbol": symbol, "name": company_data["name"], "score": score}