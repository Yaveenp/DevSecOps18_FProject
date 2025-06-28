import json
import os
from Financial_Portfolio_Tracker.Portfolio_Management.GET.GET_Portfolio import Portfolio

class Put_Portfolio:
    '''
    Updates an investment by investment id for user
    return: information message
    '''
    
    def __init__(self, portfolio_file: str = None, portfolio_data: list = None):
        """Initialize with portfolio file or data, matching Portfolio class constructor"""
        self.portfolio_instance = Portfolio(portfolio_file=portfolio_file, portfolio_data=portfolio_data)
    
    def update_investment(self, investment_id, quantity=None, buy_price=None):
        """
        Update investment using instance method (non-static)
        Args:
            investment_id: Unique ID of the investment to update
            quantity: New quantity (optional)
            buy_price: New buy price (optional)
        Returns:
            Dictionary with success message or error tuple
        """
        try:
            # Load current portfolio
            portfolio = self.portfolio_instance.load_portfolio()
            
            # Handle case where portfolio might be None or empty
            if portfolio is None or not isinstance(portfolio, list):
                return {'error': 'Portfolio not found or empty'}, 404
            
            # Find and update the investment
            for investment in portfolio:
                if investment.get('id') == investment_id:
                    # Validate data types
                    if quantity is not None:
                        if not isinstance(quantity, (int, float)) or quantity < 0:
                            return {'error': 'Invalid quantity value'}, 400
                        investment['quantity'] = quantity
                    
                    if buy_price is not None:
                        if not isinstance(buy_price, (int, float)) or buy_price < 0:
                            return {'error': 'Invalid buy_price value'}, 400
                        investment['buy_price'] = buy_price
                    
                    # Save updated portfolio using the instance method
                    self.portfolio_instance.save_portfolio(portfolio)
                    return {'message': 'Investment updated successfully.'}
            
            return {'error': 'Investment not found'}, 404
            
        except Exception as e:
            return {'error': f'Error updating investment: {str(e)}'}, 500
    
    def get_investment(self, investment_id):
        """
        Helper method to get a specific investment by ID
        Args:
            investment_id: Unique ID of the investment
        Returns:
            Investment dictionary or None if not found
        """
        try:
            portfolio = self.portfolio_instance.load_portfolio()
            
            if portfolio is None or not isinstance(portfolio, list):
                return None
            
            for investment in portfolio:
                if investment.get('id') == investment_id:
                    return investment
            
            return None
            
        except Exception as e:
            print(f"Error getting investment: {str(e)}")
            return None