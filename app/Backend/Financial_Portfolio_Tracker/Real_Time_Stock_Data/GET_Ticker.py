import requests

class Get_Ticker:
    '''
    Get ticker real time values
    returen: JSON if the ticker data
    '''
    def get_stock_quote(ticker, api_key):
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': ticker,
            'apikey': api_key
        }
        response = requests.get(url, params=params)
        data = response.json()

        quote = data.get("Global Quote", {})
        if not quote:
            return {'error': 'No data found for ticker.'}, 404

        try:
            return {
                'symbol': quote['01. symbol'],
                'open': float(quote['02. open']),
                'high': float(quote['03. high']),
                'low': float(quote['04. low']),
                'price': float(quote['05. price']),
                'volume': int(quote['06. volume']),
                'latest_trading_day': quote['07. latest trading day'],
                'previous_close': float(quote['08. previous close']),
                'change': float(quote['09. change']),
                'change_percent': quote['10. change percent']
            }
        except (KeyError, ValueError):
            return {'error': 'Failed to parse stock data.'}, 500

if __name__ == '__main__':
    Get_Ticker.get_stock_quote()