from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import numpy as np
from scipy import stats
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from backend.models.ipo import IPOListing, IPOStatus, IPOFinancials
from backend.models.stock import StockPrice
from backend.models.competitor import Competitor, CompetitorFinancials
from backend.services.cache import cache_result

class MarketAnalysis:
    def __init__(self, db: Session):
        self.db = db

    def _prepare_time_series(self, prices: List[float], dates: List[datetime]) -> pd.DataFrame:
        """Prepare time series data for analysis"""
        df = pd.DataFrame({
            'date': dates,
            'price': prices
        }).set_index('date')
        df.index = pd.DatetimeIndex(df.index)
        return df

    @cache_result("stock_prediction", expire=1800)  # Cache for 30 minutes
    async def predict_stock_movement(
        self,
        symbol: str,
        days_ahead: int = 30,
        model_type: str = 'auto'  # 'auto', 'arima', 'prophet', or 'holtwinters'
    ) -> Dict:
        """Predict future stock movements using multiple time series models.
        
        Args:
            symbol: Stock symbol to predict
            days_ahead: Number of days to forecast
            model_type: Type of model to use for prediction
        """
        # Get historical prices with batch query
        prices = self.db.query(StockPrice)\
            .filter(StockPrice.symbol == symbol)\
            .order_by(StockPrice.timestamp)\
            .all()

        if len(prices) < 60:  # Need sufficient historical data
            return {"error": "Insufficient historical data for prediction"}

        # Prepare data
        df = pd.DataFrame([
            {'ds': p.timestamp, 'y': p.price}
            for p in prices
        ])
        
        results = {}
        
        try:
            if model_type in ['auto', 'holtwinters']:
                # Holt-Winters model
                hw_model = ExponentialSmoothing(
                    df['y'],
                    seasonal_periods=5,
                    trend='add',
                    seasonal='add'
                ).fit()
                
                hw_forecast = hw_model.forecast(days_ahead)
                results['holtwinters'] = {
                    "forecast": hw_forecast.values.tolist(),
                    "model_accuracy": hw_model.aic
                }

            if model_type in ['auto', 'arima']:
                # ARIMA model
                from pmdarima import auto_arima
                arima_model = auto_arima(
                    df['y'],
                    seasonal=True,
                    m=5,
                    suppress_warnings=True,
                    error_action="ignore"
                )
                
                arima_forecast = arima_model.predict(n_periods=days_ahead)
                results['arima'] = {
                    "forecast": arima_forecast.tolist(),
                    "model_accuracy": arima_model.aic()
                }

            if model_type in ['auto', 'prophet']:
                # Prophet model
                from prophet import Prophet
                prophet_model = Prophet(
                    daily_seasonality=True,
                    weekly_seasonality=True,
                    yearly_seasonality=True
                )
                prophet_model.fit(df)
                
                future_dates = prophet_model.make_future_dataframe(periods=days_ahead)
                prophet_forecast = prophet_model.predict(future_dates)
                
                results['prophet'] = {
                    "forecast": prophet_forecast['yhat'].tail(days_ahead).tolist(),
                    "lower_bound": prophet_forecast['yhat_lower'].tail(days_ahead).tolist(),
                    "upper_bound": prophet_forecast['yhat_upper'].tail(days_ahead).tolist()
                }

            # If auto, combine models using weighted average based on accuracy
            if model_type == 'auto' and len(results) > 1:
                weights = {}
                total_weight = 0
                
                for model_name, result in results.items():
                    if model_name != 'prophet':  # Prophet uses different accuracy metric
                        weight = 1 / result.get('model_accuracy', float('inf'))
                        weights[model_name] = weight
                        total_weight += weight
                
                # Normalize weights
                weights = {k: v/total_weight for k, v in weights.items()}
                
                # Combine forecasts
                combined_forecast = np.zeros(days_ahead)
                for model_name, result in results.items():
                    if model_name in weights:
                        combined_forecast += np.array(result['forecast']) * weights[model_name]
                
                results['ensemble'] = {
                    "forecast": combined_forecast.tolist(),
                    "weights": weights
                }

            # Prepare final response
            forecast_dates = pd.date_range(
                start=df['ds'].iloc[-1] + pd.Timedelta(days=1),
                periods=days_ahead
            )

            return {
                "symbol": symbol,
                "forecast_dates": forecast_dates.strftime('%Y-%m-%d').tolist(),
                "models": results,
                "recommended_model": "ensemble" if model_type == "auto" else model_type
            }

        except Exception as e:
            return {
                "error": f"Error during prediction: {str(e)}",
                "symbol": symbol
            }

    @cache_result("volatility", expire=300)  # Cache for 5 minutes
    async def analyze_volatility(
        self,
        symbols: List[str],  # Changed to accept multiple symbols
        window_days: int = 30
    ) -> Dict:
        """Analyze stock price volatility for multiple symbols efficiently."""
        cutoff_date = datetime.utcnow() - timedelta(days=window_days)
        
        # Batch fetch all prices
        prices = self.db.query(StockPrice)\
            .filter(
                StockPrice.symbol.in_(symbols),
                StockPrice.timestamp >= cutoff_date
            )\
            .order_by(StockPrice.timestamp)\
            .all()

        # Organize prices by symbol
        prices_by_symbol = {}
        for price in prices:
            if price.symbol not in prices_by_symbol:
                prices_by_symbol[price.symbol] = []
            prices_by_symbol[price.symbol].append({
                'timestamp': price.timestamp,
                'price': price.price
            })

        results = {}
        for symbol in symbols:
            symbol_prices = prices_by_symbol.get(symbol, [])
            if not symbol_prices:
                results[symbol] = {"error": "No price data available"}
                continue

            df = pd.DataFrame(symbol_prices)
            price_values = df['price'].values
            returns = np.diff(price_values) / price_values[:-1]

            results[symbol] = {
                "volatility": float(np.std(returns) * np.sqrt(252)),  # Annualized
                "max_drawdown": float(min(returns)) if returns.size > 0 else 0,
                "sharpe_ratio": float(np.mean(returns) / np.std(returns)) if returns.size > 0 else 0,
                "period_days": window_days
            }

        return results

    @cache_result("ipo_success", expire=3600)  # Cache for 1 hour
    async def analyze_ipo_success_rate(
        self,
        timeframe_days: int,
        therapeutic_area: Optional[str] = None
    ) -> Dict:
        """Analyze IPO success rates and performance metrics with efficient data retrieval."""
        cutoff_date = datetime.utcnow() - timedelta(days=timeframe_days)
        
        # Batch query for IPOs
        query = self.db.query(IPOListing)\
            .filter(IPOListing.filing_date >= cutoff_date)\
            .filter(IPOListing.status != IPOStatus.UPCOMING)

        if therapeutic_area:
            query = query.filter(IPOListing.therapeutic_area == therapeutic_area)

        ipos = query.all()
        total_ipos = len(ipos)
        
        if total_ipos == 0:
            return {"error": "No IPO data found for the specified criteria"}

        # Get all relevant symbols
        completed_symbols = [
            ipo.symbol for ipo in ipos 
            if ipo.status == IPOStatus.COMPLETED and ipo.symbol
        ]

        # Batch fetch all relevant stock prices
        if completed_symbols:
            prices = self.db.query(
                StockPrice.symbol,
                func.min(StockPrice.price).label('first_day_price'),
                func.max(StockPrice.timestamp).label('latest_date'),
                func.min(StockPrice.timestamp).label('first_date')
            )\
            .filter(StockPrice.symbol.in_(completed_symbols))\
            .group_by(StockPrice.symbol)\
            .all()

            # Create lookup dictionaries
            price_data = {
                p.symbol: {
                    'first_day_price': p.first_day_price,
                    'latest_date': p.latest_date,
                    'first_date': p.first_date
                }
                for p in prices
            }

            # Get current prices in batch
            current_prices = self.db.query(StockPrice)\
                .filter(
                    StockPrice.symbol.in_(completed_symbols),
                    StockPrice.timestamp >= datetime.utcnow() - timedelta(days=1)
                )\
                .all()

            current_price_lookup = {
                p.symbol: p.price for p in current_prices
            }
        else:
            price_data = {}
            current_price_lookup = {}

        # Calculate metrics
        completed = sum(1 for ipo in ipos if ipo.status == IPOStatus.COMPLETED)
        withdrawn = sum(1 for ipo in ipos if ipo.status == IPOStatus.WITHDRAWN)
        
        # Calculate price performance
        price_performance = []
        for ipo in ipos:
            if (ipo.status == IPOStatus.COMPLETED and 
                ipo.symbol in price_data and 
                ipo.symbol in current_price_lookup):
                
                first_price = price_data[ipo.symbol]['first_day_price']
                current_price = current_price_lookup[ipo.symbol]
                
                if first_price and current_price:
                    performance = (current_price - first_price) / first_price
                    price_performance.append(performance)

        result = {
            "total_ipos": total_ipos,
            "completion_rate": completed / total_ipos if total_ipos > 0 else 0,
            "withdrawal_rate": withdrawn / total_ipos if total_ipos > 0 else 0,
            "avg_price_performance": float(np.mean(price_performance)) if price_performance else None,
            "median_price_performance": float(np.median(price_performance)) if price_performance else None,
            "therapeutic_area": therapeutic_area,
            "timeframe_days": timeframe_days,
            "total_analyzed": len(price_performance)
        }

        # Add statistical analysis
        if price_performance:
            t_stat, p_value = stats.ttest_1samp(price_performance, 0)
            result['statistical_analysis'] = {
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05
            }
        
        # Add visualization data
        if price_performance:
            result['visualization_data'] = {
                'performance_distribution': {
                    'bins': np.histogram(price_performance, bins=10)[0].tolist(),
                    'bin_edges': np.histogram(price_performance, bins=10)[1].tolist()
                },
                'completion_rates': {
                    'labels': ['Completed', 'Withdrawn', 'Other'],
                    'values': [
                        result['completion_rate'],
                        result['withdrawal_rate'],
                        1 - result['completion_rate'] - result['withdrawal_rate']
                    ]
                }
            }
        
        return result

    @cache_result("pricing_trends", expire=3600)  # Cache for 1 hour
    async def analyze_pricing_trends(
        self,
        therapeutic_area: Optional[str] = None
    ) -> Dict:
        """Analyze IPO pricing trends and valuation metrics"""
        # Base query for completed IPOs
        query = self.db.query(IPOListing)\
            .filter(IPOListing.status == IPOStatus.COMPLETED)

        if therapeutic_area:
            query = query.filter(IPOListing.therapeutic_area == therapeutic_area)

        ipos = query.all()
        
        if not ipos:
            return {"error": "No completed IPO data found"}

        # Collect pricing data
        pricing_data = []
        for ipo in ipos:
            if ipo.price_range_low and ipo.price_range_high:
                mid_price = (ipo.price_range_low + ipo.price_range_high) / 2
                pricing_data.append({
                    "date": ipo.filing_date,
                    "mid_price": mid_price,
                    "valuation": ipo.initial_valuation
                })

        df = pd.DataFrame(pricing_data)
        if df.empty:
            return {"error": "Insufficient pricing data"}

        # Calculate trends
        df['rolling_avg_price'] = df['mid_price'].rolling(window=10).mean()
        df['rolling_avg_valuation'] = df['valuation'].rolling(window=10).mean()

        result = {
            "price_trend": df['rolling_avg_price'].tolist(),
            "valuation_trend": df['rolling_avg_valuation'].tolist(),
            "dates": df['date'].tolist(),
            "avg_valuation": df['valuation'].mean(),
            "median_valuation": df['valuation'].median(),
            "therapeutic_area": therapeutic_area
        }
        
        if 'error' not in result:
            # Add regression analysis
            dates_numeric = pd.to_numeric(pd.to_datetime(result['dates']))
            X = dates_numeric.values.reshape(-1, 1)
            y = result['price_trend']
            
            model = LinearRegression()
            model.fit(X, y)
            
            trend_prediction = model.predict(X)
            
            result['trend_analysis'] = {
                'trend_line': trend_prediction.tolist(),
                'slope': float(model.coef_[0]),
                'r_squared': float(model.score(X, y))
            }
            
            # Add visualization-ready format
            result['visualization_data'] = {
                'time_series': {
                    'x': result['dates'],
                    'y': result['price_trend'],
                    'trend': trend_prediction.tolist()
                },
                'valuation_distribution': {
                    'bins': np.histogram(result['valuation_trend'], bins=10)[0].tolist(),
                    'bin_edges': np.histogram(result['valuation_trend'], bins=10)[1].tolist()
                }
            }
        
        return result

    @cache_result("market_impact", expire=1800)  # Cache for 30 minutes
    async def analyze_market_impact(
        self,
        ipo_symbol: str,
        days_before: int = 30,
        days_after: int = 30
    ) -> Dict:
        """Analyze market impact of IPO on competitors using correlation analysis"""
        ipo = self.db.query(IPOListing)\
            .filter(IPOListing.symbol == ipo_symbol)\
            .first()
        
        if not ipo:
            return {"error": "IPO not found"}

        # Get all competitors in same therapeutic area
        competitors = self.db.query(Competitor)\
            .filter(Competitor.therapeutic_area == ipo.therapeutic_area)\
            .all()

        ipo_date = ipo.expected_date or ipo.filing_date
        start_date = ipo_date - timedelta(days=days_before)
        end_date = ipo_date + timedelta(days=days_after)

        # Batch fetch all relevant stock prices
        all_symbols = [ipo_symbol] + [comp.symbol for comp in competitors]
        all_prices = self.db.query(StockPrice)\
            .filter(
                StockPrice.symbol.in_(all_symbols),
                StockPrice.timestamp.between(start_date, end_date)
            )\
            .order_by(StockPrice.timestamp)\
            .all()

        # Organize prices by symbol
        prices_by_symbol = {}
        for price in all_prices:
            if price.symbol not in prices_by_symbol:
                prices_by_symbol[price.symbol] = []
            prices_by_symbol[price.symbol].append({
                'timestamp': price.timestamp,
                'price': price.price
            })

        # Get IPO price series
        ipo_prices = prices_by_symbol.get(ipo_symbol, [])
        if not ipo_prices:
            return {"error": "No price data available for IPO"}

        ipo_df = pd.DataFrame(ipo_prices).set_index('timestamp')
        ipo_returns = ipo_df['price'].pct_change()

        impact_data = []
        correlations = []
        volumes = []

        for competitor in competitors:
            comp_prices = prices_by_symbol.get(competitor.symbol, [])
            if comp_prices:
                comp_df = pd.DataFrame(comp_prices).set_index('timestamp')
                comp_returns = comp_df['price'].pct_change()

                # Calculate correlation only for overlapping dates
                overlap_idx = ipo_returns.index.intersection(comp_returns.index)
                if len(overlap_idx) > 1:  # Need at least 2 points for correlation
                    correlation = ipo_returns[overlap_idx].corr(comp_returns[overlap_idx])
                    correlations.append(correlation)

                    # Calculate pre/post IPO metrics
                    pre_ipo = comp_df[comp_df.index < ipo_date]['price'].mean()
                    post_ipo = comp_df[comp_df.index > ipo_date]['price'].mean()
                    price_change = (post_ipo - pre_ipo) / pre_ipo if pre_ipo else None

                    impact_data.append({
                        "competitor": competitor.symbol,
                        "correlation": correlation,
                        "price_change": price_change,
                        "pre_ipo_avg": float(pre_ipo) if pre_ipo else None,
                        "post_ipo_avg": float(post_ipo) if post_ipo else None
                    })

        if not impact_data:
            return {"error": "Insufficient data for market impact analysis"}

        # Calculate statistical significance
        correlations = np.array([d["correlation"] for d in impact_data])
        t_stat, p_value = stats.ttest_1samp(correlations, 0)

        result = {
            "ipo_symbol": ipo_symbol,
            "therapeutic_area": ipo.therapeutic_area,
            "ipo_date": ipo_date,
            "competitor_impacts": impact_data,
            "avg_correlation": float(np.mean(correlations)),
            "median_correlation": float(np.median(correlations)),
            "correlation_std": float(np.std(correlations)),
            "total_competitors_analyzed": len(impact_data),
            "statistical_analysis": {
                't_statistic': float(t_stat),
                'p_value': float(p_value),
                'significant': p_value < 0.05
            }
        }

        # Add visualization-ready format
        result['visualization_data'] = {
            'correlation_heatmap': {
                'competitors': [d['competitor'] for d in impact_data],
                'correlations': [d['correlation'] for d in impact_data]
            },
            'price_changes': {
                'competitors': [d['competitor'] for d in impact_data],
                'changes': [d['price_change'] for d in impact_data]
            },
            'correlation_distribution': {
                'bins': np.histogram(correlations, bins=10)[0].tolist(),
                'bin_edges': np.histogram(correlations, bins=10)[1].tolist()
            }
        }

        return result 