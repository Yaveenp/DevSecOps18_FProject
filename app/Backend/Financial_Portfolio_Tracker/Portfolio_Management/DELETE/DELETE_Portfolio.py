import json
from datetime import datetime
from Financial_Portfolio_Tracker.Portfolio_Management.GET.GET_Portfolio import Portfolio

class Delete_Portfolio:
    '''
    Delete an investment by investment id for user
    return: information message
    '''
    
    def __init__(self, portfolio_file: str = None, portfolio_data: list = None):
        """Initialize with portfolio file or data, matching Portfolio class constructor"""
        self.portfolio_instance = Portfolio(portfolio_file=portfolio_file, portfolio_data=portfolio_data)
    
    @staticmethod
    def delete_investment_from_data(portfolio_data, investment_id):
        """
        Delete an investment from the portfolio_data['holdings'] list. Only update the dict, do not commit DB.
        Returns: dict with updated portfolio_data and deleted_ticker for DB logic in main app.
        """
        try:
            if not isinstance(portfolio_data, dict) or 'holdings' not in portfolio_data:
                return {'error': 'Invalid portfolio data structure'}
            holdings = portfolio_data['holdings']
            initial_count = len(holdings)
            # Find the investment to delete for ticker
            deleted_ticker = None
            for inv in holdings:
                if str(inv.get('id')) == str(investment_id):
                    deleted_ticker = inv.get('ticker')
                    break
            new_holdings = [inv for inv in holdings if str(inv.get('id')) != str(investment_id)]
            if len(new_holdings) == initial_count:
                return {'error': f'Investment with ID {investment_id} not found'}
            portfolio_data['holdings'] = new_holdings
            portfolio_data['total_investment'] = sum(item['buy_price'] * item['quantity'] for item in new_holdings)
            portfolio_data['total_value'] = sum(item.get('value', 0.0) for item in new_holdings)
            portfolio_data['total_gain_loss'] = sum(item.get('gain', 0.0) for item in new_holdings)
            portfolio_data['updated_at'] = datetime.now().isoformat()
            return {'portfolio_data': portfolio_data, 'deleted_ticker': deleted_ticker}
        except Exception as e:
            return {'error': f'Error deleting investment: {str(e)}'}
    
