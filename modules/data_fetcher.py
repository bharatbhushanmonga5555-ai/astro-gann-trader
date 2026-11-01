"""
Market Data Fetcher
Uses yfinance for free data (limited for Indian F&O).
For production, replace with TrueData / broker API.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, List
import pandas as pd

try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False


# Symbol mapping (yfinance free symbols - approximate)
SYMBOLS = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "GOLD": "GC=F",          # COMEX Gold
    "CRUDEOIL": "CL=F",      # WTI Crude
    "NATURALGAS": "NG=F",    # Natural Gas
    # Indian alternatives if available
    "NIFTY_IN": "^NSEI",
    "SENSEX": "^BSESN",
}


def fetch_price_data(symbol_key: str = "NIFTY", period: str = "5d", interval: str = "15m") -> Optional[pd.DataFrame]:
    """
    Fetch OHLCV data.
    period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
    interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    """
    if not HAS_YFINANCE:
        return None
    
    ticker = SYMBOLS.get(symbol_key.upper(), symbol_key)
    
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        if data.empty:
            return None
        
        # Flatten multi-index columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        data = data.reset_index()
        data.columns = [c.lower() if isinstance(c, str) else c for c in data.columns]
        
        # Standardize column names
        rename_map = {
            "datetime": "datetime",
            "date": "datetime",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close",
            "volume": "volume"
        }
        data = data.rename(columns={k: v for k, v in rename_map.items() if k in data.columns})
        
        return data
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None


def get_latest_price(symbol_key: str = "NIFTY") -> Optional[float]:
    """Get the most recent closing / last price."""
    df = fetch_price_data(symbol_key, period="5d", interval="15m")
    if df is not None and not df.empty and "close" in df.columns:
        return float(df["close"].iloc[-1])
    return None


def get_multi_prices(symbols: List[str] = None) -> Dict[str, float]:
    """Get latest prices for multiple instruments."""
    if symbols is None:
        symbols = ["NIFTY", "BANKNIFTY", "GOLD", "CRUDEOIL", "NATURALGAS"]
    
    result = {}
    for sym in symbols:
        price = get_latest_price(sym)
        result[sym] = price
    return result


def get_support_resistance_from_price_action(df: pd.DataFrame, lookback: int = 50) -> Dict:
    """Simple pivot based S/R from recent price action."""
    if df is None or len(df) < 10:
        return {"supports": [], "resistances": []}
    
    recent = df.tail(lookback)
    
    # Simple method: recent swing highs / lows
    highs = recent["high"].nlargest(5).values.tolist()
    lows = recent["low"].nsmallest(5).values.tolist()
    
    return {
        "resistances": sorted(set([round(h, 2) for h in highs]), reverse=True),
        "supports": sorted(set([round(l, 2) for l in lows]))
    }
