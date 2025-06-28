import json
import os
import uuid
from GET import Portfolio

PORTFOLIO_FILE = 'portfolio.json'

class Post_Portfolio:
    '''
    Adding an investment by investment id for user
    returen: inforantion message
    '''
    def add_investment(ticker, quantity, buy_price):
        portfolio = Portfolio.load_portfolio()
        ticker = ticker.upper()

        new_investment = {
            'id': str(uuid.uuid4()),
            'ticker': ticker,
            'quantity': quantity,
            'buy_price': buy_price
        }
        portfolio.append(new_investment)
        Portfolio.save_portfolio(portfolio)
        return {'message': f"{ticker} added.", 'id': new_investment['id']}
    
if __name__ == '__main__':
    Post_Portfolio.add_investment()