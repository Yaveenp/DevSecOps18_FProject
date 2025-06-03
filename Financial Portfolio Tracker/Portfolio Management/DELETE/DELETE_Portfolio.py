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

def delete_investment(investment_id):
    portfolio = load_portfolio()
    new_portfolio = [inv for inv in portfolio if inv['id'] != investment_id]
    if len(portfolio) == len(new_portfolio):
        return {'error': 'Investment not found'}, 404

    save_portfolio(new_portfolio)
    return {'message': 'Investment deleted successfully.'}