import os
from datetime import datetime
from typing import Dict, List, Optional, Union
import requests
from dotenv import load_dotenv

load_dotenv()

class MarketDataService:
    def __init__(self):
        self.api_key = os.getenv("MARKETSTACK_API_KEY")
        self.base_url = "http://api.marketstack.com/v1"
        self.session = requests.Session()
        self.session.params = {'access_key': self.api_key}

    def _make_request(self, endpoint: str, params: Dict = None) -> Union[Dict, List, None]:
        """Make a request to the MarketStack API with error handling"""
        try:
            response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {endpoint}: {str(e)}")
            return None

    def get_eod_data(self, symbol: str, from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get end-of-day data for a symbol"""
        params = {'symbols': symbol}
        if from_date:
            params['date_from'] = from_date
        if to_date:
            params['date_to'] = to_date
        
        data = self._make_request('eod', params)
        return data.get('data', []) if data else []

    def get_intraday_data(self, symbol: str, interval: str = '1min') -> List[Dict]:
        """Get intraday data for a symbol"""
        params = {
            'symbols': symbol,
            'interval': interval
        }
        data = self._make_request('intraday', params)
        return data.get('data', []) if data else []

    def get_company_info(self, symbol: str = None) -> Union[Dict, List[Dict]]:
        """Get detailed company information"""
        endpoint = f"tickers/{symbol}" if symbol else "tickers"
        data = self._make_request(endpoint)
        return data.get('data', {}) if data else {}

    def get_exchanges(self) -> List[Dict]:
        """Get list of stock exchanges"""
        data = self._make_request('exchanges')
        return data.get('data', []) if data else []

    def get_index_data(self, index_symbol: str, from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get data for market indices"""
        params = {'symbols': index_symbol}
        if from_date:
            params['date_from'] = from_date
        if to_date:
            params['date_to'] = to_date
        
        data = self._make_request('eod', params)
        return data.get('data', []) if data else []

    def get_dividends(self, symbol: str, from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get dividend information for a symbol"""
        params = {'symbols': symbol}
        if from_date:
            params['date_from'] = from_date
        if to_date:
            params['date_to'] = to_date
        
        data = self._make_request('dividends', params)
        return data.get('data', []) if data else []

    def get_splits(self, symbol: str, from_date: str = None, to_date: str = None) -> List[Dict]:
        """Get stock split information for a symbol"""
        params = {'symbols': symbol}
        if from_date:
            params['date_from'] = from_date
        if to_date:
            params['date_to'] = to_date
        
        data = self._make_request('splits', params)
        return data.get('data', []) if data else [] 