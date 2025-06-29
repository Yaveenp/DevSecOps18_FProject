import json
from datetime import datetime

class Put_Portfolio:
    '''
    Updates an investment by investment id for user
    return: information message
    '''
    @staticmethod
    def update_investment_in_data(portfolio_data, investment_id, quantity=None, buy_price=None):
        """
        Update an investment in the portfolio_data['holdings'] list. Only update the dict, do not commit DB.
        Returns: dict with updated portfolio_data and updated investment for DB logic in main app.
        """
        try:
            if not isinstance(portfolio_data, dict) or 'holdings' not in portfolio_data:
                return {'error': 'Invalid portfolio data structure'}
            holdings = portfolio_data['holdings']
            investment_found = False
            updated_investment = None
            for investment in holdings:
                if str(investment.get('id')) == str(investment_id):
                    investment_found = True
                    if quantity is not None:
                        if not isinstance(quantity, (int, float)) or quantity < 0:
                            return {'error': 'Invalid quantity value'}
                        investment['quantity'] = float(quantity)
                    if buy_price is not None:
                        if not isinstance(buy_price, (int, float)) or buy_price < 0:
                            return {'error': 'Invalid buy_price value'}
                        investment['buy_price'] = float(buy_price)
                    investment['updated_at'] = datetime.now().isoformat()
                    updated_investment = investment
                    break
            if not investment_found:
                return {'error': f'Investment with ID {investment_id} not found'}
            portfolio_data['total_investment'] = sum(item['buy_price'] * item['quantity'] for item in holdings)
            portfolio_data['total_value'] = sum(item.get('value', 0.0) for item in holdings)
            portfolio_data['total_gain_loss'] = sum(item.get('gain', 0.0) for item in holdings)
            portfolio_data['updated_at'] = datetime.now().isoformat()
            return {'portfolio_data': portfolio_data, 'updated_investment': updated_investment}
        except Exception as e:
            return {'error': f'Error updating investment: {str(e)}'}