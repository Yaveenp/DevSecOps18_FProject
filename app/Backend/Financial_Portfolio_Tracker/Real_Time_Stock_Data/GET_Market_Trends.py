import requests
import time
import random

class Get_Market_Trends:
    '''
    Get market trends real time values
    return: List of top gainers as dicts, or error string
    '''
    @staticmethod
    def get_top_gainers(api_key):
        # Alpha Vantage does not have a direct 'top gainers' endpoint in the free API.
        # We'll use the 'TIME_SERIES_DAILY' for a random sample of 5 from a static list of 50 popular symbols.
        url = "https://www.alphavantage.co/query"
        symbols = [
            "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BRK.B", "UNH", "V",
            "JPM", "XOM", "LLY", "AVGO", "JNJ", "WMT", "PG", "MA", "HD", "MRK",
            "COST", "ABBV", "ADBE", "CVX", "PEP", "KO", "BAC", "NFLX", "TMO", "DIS",
            "PFE", "ABT", "CSCO", "MCD", "CRM", "ACN", "DHR", "LIN", "WFC", "VZ",
            "INTC", "TXN", "NEE", "NKE", "ORCL", "AMGN", "MDT", "QCOM", "HON", "IBM"
        ]
        # Randomly select 5 unique symbols from the list
        selected_symbols = random.sample(symbols, 5)
        gainers = []
        for symbol in selected_symbols:
            params = {
                "function": "TIME_SERIES_DAILY",
                "symbol": symbol,
                "apikey": api_key
            }
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
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
                    gainers.append({
                        "symbol": symbol,
                        "price": close_price,
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2)
                    })
                else:
                    continue
            except Exception:
                continue
            # Alpha Vantage free API allows 5 requests per minute; sleep to avoid hitting the limit
            time.sleep(2)
        # Sort by change_percent descending and return all (should be 10)
        gainers.sort(key=lambda x: x["change_percent"], reverse=True)
        return gainers

if __name__ == '__main__':
    api_key = "YOUR_API_KEY"  # Replace with your actual API key
    top_gainers = Get_Market_Trends.get_top_gainers(api_key)
    print(top_gainers)
