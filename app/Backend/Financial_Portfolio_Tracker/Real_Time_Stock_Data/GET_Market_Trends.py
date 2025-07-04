import requests
import time
import random

class Get_Market_Trends:
    '''
    Get market trends real time values
    return: Dict with 'top_gainers' (top 3 by percent)
    '''
    @staticmethod
    def get_market_trends(api_key):
        url = "https://www.alphavantage.co/query"
        symbols = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "UNH", "V",
            "JPM", "XOM", "LLY", "AVGO", "JNJ", "WMT", "PG", "MA", "HD", "MRK",
            "COST", "ABBV", "ADBE", "CVX", "PEP", "KO", "BAC", "NFLX", "TMO", "DIS",
            "PFE", "ABT", "CSCO", "MCD", "CRM", "ACN", "DHR", "LIN", "WFC", "VZ",
            "INTC", "TXN", "NEE", "NKE", "ORCL", "AMGN", "MDT", "QCOM", "HON", "IBM"
        ]
        selected_symbols = random.sample(symbols, 5)
        all_changes = []
        for symbol in selected_symbols:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": api_key
            }
            try:
                response = requests.get(url, params=params)
                print(f"Alpha Vantage response for {symbol}: {response.text}")
                if response.status_code != 200:
                    continue
                data = response.json()
                if "Note" in data:
                    return {"error": "Alpha Vantage API rate limit exceeded. Please try again later."}
                if "Error Message" in data:
                    return {"error": f"Invalid ticker symbol '{symbol}' or API error."}
                if "Time Series (Daily)" not in data:
                    continue
                dates = sorted(data["Time Series (Daily)"].keys())
                if len(dates) < 2:
                    continue
                latest_date = dates[-1]
                latest = data["Time Series (Daily)"][latest_date]
                close_price = float(latest["4. close"])
                open_price = float(latest["1. open"])
                change = close_price - open_price
                change_percent = (change / open_price) * 100 if open_price else 0.0
                all_changes.append({
                    "ticker": symbol,
                    "price": close_price,
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 2)
                })
            except Exception as e:
                print(f"Exception for {symbol}: {e}")
                continue
            time.sleep(2)
        if not all_changes:
            return {"error": "No market data could be retrieved. Check API key or rate limits."}
        # Sort for top gainers (top 3 by percent)
        top_gainers = sorted(all_changes, key=lambda x: x["change_percent"], reverse=True)[:3]
        return {
            "top_gainers": top_gainers
        }

if __name__ == '__main__':
    api_key = "YOUR_API_KEY"  # Replace with your actual API key
    result = Get_Market_Trends.get_market_trends(api_key)
    print(result)
