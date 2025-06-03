import json
import os
import requests

PORTFOLIO_FILE = 'portfolio.json'

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    return []

def get_stock_quote(symbol, api_key):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data.get('Global Quote', {})

def get_portfolio_with_quotes(api_key):
    portfolio = load_portfolio()
    results = []

    for stock in portfolio:
        quote = get_stock_quote(stock['ticker'], api_key)
        if quote:
            price = float(quote.get('05. price', 0))
            change_pct = quote.get('10. change percent', 'N/A')
            current_value = round(price * stock['quantity'], 2)
            gain = round((price - stock['buy_price']) * stock['quantity'], 2)
            results.append({
                'id': stock['id'],
                'ticker': stock['ticker'],
                'quantity': stock['quantity'],
                'buy_price': stock['buy_price'],
                'current_price': price,
                'value': current_value,
                'gain': gain,
                'change_percent': change_pct
            })

    return results