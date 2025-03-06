import os
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class MarketDataService:
    def __init__(self):
        self.api_key = os.getenv("MARKETSTACK_API_KEY")
        self.base_url = "http://api.marketstack.com/v1"

    def get_stock_price(self, symbol: str) -> Optional[Dict]:
        """
        Fetch real-time stock price for a given symbol
        """
        endpoint = f"{self.base_url}/intraday"
        params = {
            "access_key": self.api_key,
            "symbols": symbol,
            "limit": 1
        }

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("data"):
                return {
                    "symbol": symbol,
                    "price": data["data"][0]["close"],
                    "timestamp": data["data"][0]["date"]
                }
            return None
        except Exception as e:
            print(f"Error fetching stock price: {str(e)}")
            return None

    def get_historical_data(self, symbol: str, from_date: str, to_date: str) -> List[Dict]:
        """
        Fetch historical stock data for a given symbol and date range
        """
        endpoint = f"{self.base_url}/eod"
        params = {
            "access_key": self.api_key,
            "symbols": symbol,
            "date_from": from_date,
            "date_to": to_date
        }

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            return data.get("data", [])
        except Exception as e:
            print(f"Error fetching historical data: {str(e)}")
            return []

    def get_company_info(self, symbol: str) -> Optional[Dict]:
        """
        Fetch company information for a given symbol
        """
        endpoint = f"{self.base_url}/tickers/{symbol}"
        params = {
            "access_key": self.api_key
        }

        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching company info: {str(e)}")
            return None 