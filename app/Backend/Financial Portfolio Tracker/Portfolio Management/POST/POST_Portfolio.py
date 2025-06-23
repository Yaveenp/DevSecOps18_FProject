import json
import os
import uuid

PORTFOLIO_FILE = 'portfolio.json'

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, 'r') as f:
            return json.load(f)
    return []

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, 'w') as f:
        json.dump(portfolio, f, indent=4)

def add_investment(ticker, quantity, buy_price):
    portfolio = load_portfolio()
    ticker = ticker.upper()

    new_investment = {
        'id': str(uuid.uuid4()),
        'ticker': ticker,
        'quantity': quantity,
        'buy_price': buy_price
    }
    portfolio.append(new_investment)
    save_portfolio(portfolio)
    return {'message': f"{ticker} added.", 'id': new_investment['id']}