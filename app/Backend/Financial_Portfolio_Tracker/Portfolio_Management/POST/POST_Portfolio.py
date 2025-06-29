import json
from datetime import datetime
from Financial_Portfolio_Tracker.Portfolio_Management.GET.GET_Portfolio import Portfolio

class Post_Portfolio:
    '''
    Adding an investment by investment id for user
    return: information message
    '''
    
    def __init__(self, portfolio_file: str = None, portfolio_data: dict = None):
        """Initialize with portfolio file or data, matching Portfolio class constructor"""
        self.portfolio_instance = Portfolio(portfolio_file=portfolio_file, portfolio_data=portfolio_data)
    
    @staticmethod
    def add_investment_static(ticker, quantity, buy_price, portfolio_file: str = None, portfolio_data: dict = None):
        """
        Static method version for backward compatibility
        """
        post_portfolio = Post_Portfolio(portfolio_file=portfolio_file, portfolio_data=portfolio_data)
        return post_portfolio.add_investment(ticker, quantity, buy_price)

    @staticmethod
    def add_investment(portfolio_data, ticker, quantity, buy_price):
        # Defensive: if portfolio_data is None, make it a dict with base fields
        if portfolio_data is None or not isinstance(portfolio_data, dict):
            portfolio_data = {
                "portfolio_name": "New Portfolio",
                "total_value": 0.0,
                "total_investment": 0.0,
                "total_gain_loss": 0.0,
                "holdings": []
            }
        ticker = ticker.upper()
        if portfolio_data['holdings']:
            existing_ids = [inv.get('id', -1) for inv in portfolio_data['holdings'] if isinstance(inv.get('id', 0), int) or (isinstance(inv.get('id', 0), str) and inv.get('id', 0).isdigit())]
            existing_ids = [int(i) for i in existing_ids]
            next_id = max(existing_ids) + 1 if existing_ids else 0
        else:
            next_id = 0
        new_investment = {
            'id': next_id,
            'ticker': ticker,
            'quantity': quantity,
            'buy_price': buy_price,
            'current_price': 0.0,
            'value': 0.0,
            'gain': 0.0,
            'change_percent': 0.0,
            'company_name': '',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        portfolio_data['holdings'].append(new_investment)
        portfolio_data['total_investment'] = sum(item['buy_price'] * item['quantity'] for item in portfolio_data['holdings'])
        portfolio_data['total_value'] = sum(item.get('value', 0.0) for item in portfolio_data['holdings'])
        portfolio_data['total_gain_loss'] = sum(item.get('gain', 0.0) for item in portfolio_data['holdings'])
        portfolio_data['updated_at'] = datetime.now().isoformat()
        return {
            'portfolio_data': portfolio_data,
            'message': f"{ticker} added.",
            'id': new_investment['id'],
            'ticker': ticker,
            'quantity': quantity,
            'buy_price': buy_price
        }

