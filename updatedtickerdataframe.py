import os
import pandas as pd
from dotenv import load_dotenv
import httpx
import json 

load_dotenv()
API_KEY = os.getenv("POLYGON_API_KEY")
BASE_URL = "https://api.polygon.io"


async def get_daily_bars(client, ticker: str, start_date: str, end_date: str):
    url = f"{BASE_URL}/v2/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}"
    resp = await client.get(url, params={"adjusted": "true", "limit": 50000, "apiKey": API_KEY})
    results = resp.json().get("results", [])
    if not results:
        return pd.DataFrame()  # no data
    df = pd.DataFrame(results)
    df["Date"] = pd.to_datetime(df["t"], unit="ms")
    df = df.rename(columns={"o": "Open", "h": "High", "l": "Low", "c": "Close", "v": "Volume"})
    return df[["Date", "Open", "High", "Low", "Close", "Volume"]].set_index("Date")


async def get_indicator(client, ticker: str, indicator: str, window: int, timespan="week"):
    url = f"{BASE_URL}/v1/indicators/{indicator}/{ticker}"
    params = {
        "timespan": timespan,
        "window": window,
        "series_type": "close",
        "adjusted": "true",
        "apiKey": API_KEY
    }
    resp = await client.get(url, params=params)

    try:
        data_json = resp.json()
    except json.JSONDecodeError:
        print(f"❌ JSON decode error for {ticker}-{indicator}:")
        print(resp.text[:200])  # show first 200 chars of the bad response
        return None

    data = data_json.get("results", {}).get("values", [])
    return data[-1]["value"] if data else None

async def main():
    ticker = "AAPL"
    start_date = "2025-01-01"
    end_date = "2025-12-31"

    async with httpx.AsyncClient(timeout=15) as client:
        
        # --- Get Prices ---
        df = await get_daily_bars(client, ticker, start_date, end_date)
        if df.empty:
            print("No price data.")
            return
        
        # Convert to weekly OHLC
        weekly = df.resample("W").agg({
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum"
        })

        # --- Get Indicators from Polygon (no math) ---
        weekly["SMA20"] = await get_indicator(client, ticker, "sma", 20)
        weekly["EMA20"] = await get_indicator(client, ticker, "ema", 20)
        weekly["RSI14"] = await get_indicator(client, ticker, "rsi", 14)
        weekly["MACD20"] = await get_indicator(client, ticker, "macd", 20)
        print(weekly.tail())


import asyncio
asyncio.run(main())
