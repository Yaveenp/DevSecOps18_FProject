import json
import os
from GET import Portfolio

PORTFOLIO_FILE = 'portfolio.json'

class Put_Portfolio:
    '''
    Updates a 
    returen: JSON if the ticker data
    '''
    def update_investment(investment_id, quantity=None, buy_price=None):
        portfolio = Portfolio.load_portfolio()
        for investment in portfolio:
            if investment['id'] == investment_id:
                if quantity is not None:
                    investment['quantity'] = quantity
                if buy_price is not None:
                    investment['buy_price'] = buy_price
                Portfolio.save_portfolio(portfolio)
                return {'message': 'Investment updated successfully.'}
        return {'error': 'Investment not found'}, 404
    
if __name__ == '__main__':
    Put_Portfolio.update_investment()