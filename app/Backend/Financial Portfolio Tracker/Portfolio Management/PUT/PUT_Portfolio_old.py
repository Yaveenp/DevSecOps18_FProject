# add_investment.py

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

    for investment in portfolio:
        if investment['ticker'] == ticker:
            # Merge with existing (optional, or remove this logic if you want separate rows)
            total_quantity = investment['quantity'] + quantity
            investment['buy_price'] = round(
                (investment['buy_price'] * investment['quantity'] + buy_price * quantity) / total_quantity, 2
            )
            investment['quantity'] = total_quantity
            save_portfolio(portfolio)
            return {'message': f"{ticker} updated (merged).", 'id': investment['id']}

    # New entry with unique ID
    new_investment = {
        'id': str(uuid.uuid4()),
        'ticker': ticker,
        'quantity': quantity,
        'buy_price': buy_price
    }
    portfolio.append(new_investment)
    save_portfolio(portfolio)
    return {'message': f"{ticker} added.", 'id': new_investment['id']}

def update_investment(investment_id, quantity=None, buy_price=None):
    portfolio = load_portfolio()
    for investment in portfolio:
        if investment['id'] == investment_id:
            if quantity is not None:
                investment['quantity'] = quantity
            if buy_price is not None:
                investment['buy_price'] = buy_price
            save_portfolio(portfolio)
            return {'message': f"Investment {investment_id} updated successfully."}
    return {'error': f"Investment with ID {investment_id} not found."}, 404
