# add_investment.py

import json
import os

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

    for investment in portfolio:
        if investment['ticker'] == ticker:
            total_quantity = investment['quantity'] + quantity
            investment['buy_price'] = round(
                (investment['buy_price'] * investment['quantity'] + buy_price * quantity) / total_quantity, 2
            )
            investment['quantity'] = total_quantity
            break
    else:
        portfolio.append({
            'ticker': ticker,
            'quantity': quantity,
            'buy_price': buy_price
        })

    save_portfolio(portfolio)
    return {'message': f"{ticker} added/updated successfully."}