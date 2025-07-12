import requests

class Get_Ticker:
    '''
    Get ticker real time values
    return: JSON of the ticker data
    '''
    @staticmethod
    def get_stock_quote(ticker, api_key):
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': ticker,
            'apikey': api_key
        }
        try:
            response = requests.get(url, params=params)
            data = response.json()
            # Log the raw response for debugging
            print(f"Alpha Vantage response for {ticker}: {data}")

            if "Note" in data:
                return {"error": "Alpha Vantage API rate limit exceeded. Please try again later."}
            if "Error Message" in data:
                return {"error": f"Invalid ticker symbol '{ticker}' or API error."}
            quote = data.get("Global Quote", {})
            if not quote or not quote.get("01. symbol"):
                return {"error": f"No data found for ticker '{ticker}'. It may be invalid or unavailable."}

            return {
                'symbol': quote.get('01. symbol', ticker),
                'open': float(quote.get('02. open', 0)),
                'high': float(quote.get('03. high', 0)),
                'low': float(quote.get('04. low', 0)),
                'price': float(quote.get('05. price', 0)),
                'volume': int(quote.get('06. volume', 0)),
                'latest_trading_day': quote.get('07. latest trading day', ''),
                'previous_close': float(quote.get('08. previous close', 0)),
                'change': float(quote.get('09. change', 0)),
                'change_percent': quote.get('10. change percent', '0')
            }
        except Exception as e:
            print(f"Exception in get_stock_quote: {e}")
            return {"error": "Internal server error while fetching stock data."}

if __name__ == '__main__':
    # Example usage: Get_Ticker.get_stock_quote('AAPL', 'YOUR_API_KEY')
    ticker = 'AAPL'
    api_key = 'YOUR_API_KEY'
    result = Get_Ticker.get_stock_quote(ticker, api_key)
    print(result)