import requests

API_KEY = 'TU9HXAGCT30ECLY8'
BASE_URL = 'https://www.alphavantage.co/query'
Stocks_Name = ['AAPL', 'MSFT', 'GOOG']

def get_stock_quote(Stock_Name):
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': Stock_Name,
        'apikey': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    return data.get('Global Quote', {})

portfolio = []

for Stock_Name in Stocks_Name:
    quote = get_stock_quote(Stock_Name)
    if quote:
        portfolio.append({
            'symbol': quote.get('01. symbol'),
            'price': quote.get('05. price'),
            'change': quote.get('09. change'),
            'percent_change': quote.get('10. change percent')
        })
for stock in portfolio:
    print(f"{stock['symbol']}: ${stock['price']} ({stock['percent_change']})")