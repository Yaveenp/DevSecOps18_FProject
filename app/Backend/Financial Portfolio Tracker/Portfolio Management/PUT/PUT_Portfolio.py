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

def update_investment(investment_id, quantity=None, buy_price=None):
    portfolio = load_portfolio()
    for investment in portfolio:
        if investment['id'] == investment_id:
            if quantity is not None:
                investment['quantity'] = quantity
            if buy_price is not None:
                investment['buy_price'] = buy_price
            save_portfolio(portfolio)
            return {'message': 'Investment updated successfully.'}
    return {'error': 'Investment not found'}, 404