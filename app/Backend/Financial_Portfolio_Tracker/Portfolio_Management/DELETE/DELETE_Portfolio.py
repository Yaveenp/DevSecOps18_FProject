import json
import os
from GET import Portfolio

PORTFOLIO_FILE = 'portfolio.json'

class Delete_Portfolio:
    '''
    Delete a investment by investment id for user
    returen: inforantion message
    '''
    def delete_investment(investment_id):
        portfolio = Portfolio.load_portfolio()
        new_portfolio = [inv for inv in portfolio if inv['id'] != investment_id]
        if len(portfolio) == len(new_portfolio):
            return {'error': 'Investment not found'}, 404

        Portfolio.save_portfolio(new_portfolio)
        return {'message': 'Investment deleted successfully.'}

if __name__ == '__main__':
    Delete_Portfolio.add_investment()