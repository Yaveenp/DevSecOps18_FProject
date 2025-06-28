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
    
    @staticmethod
    def update_investment_in_data(portfolio_data, investment_id, quantity=None, buy_price=None):
        """
        Static method to update investment in portfolio data
        Args:
            portfolio_data: Portfolio data (list, dict, or JSON string)
            investment_id: Unique ID of the investment to update
            quantity: New quantity (optional)
            buy_price: New buy price (optional)
        Returns:
            Dictionary with updated portfolio_data or error
        """
        try:
            # Debug: Print the type and structure of portfolio_data
            print(f"Portfolio data type: {type(portfolio_data)}")
            print(f"Portfolio data: {portfolio_data}")
            
            # Handle different data formats
            if isinstance(portfolio_data, str):
                try:
                    portfolio = json.loads(portfolio_data)
                except json.JSONDecodeError:
                    return {'error': 'Invalid JSON data'}
            elif isinstance(portfolio_data, list):
                portfolio = portfolio_data
            elif isinstance(portfolio_data, dict):
                # If it's a dict, it might contain the portfolio data
                # Check common keys where portfolio data might be stored
                if 'portfolio' in portfolio_data:
                    portfolio = portfolio_data['portfolio']
                elif 'data' in portfolio_data:
                    portfolio = portfolio_data['data']
                elif 'investments' in portfolio_data:
                    portfolio = portfolio_data['investments']
                else:
                    # If it's a single investment object, wrap it in a list
                    if 'id' in portfolio_data:
                        portfolio = [portfolio_data]
                    else:
                        return {'error': 'Invalid portfolio data structure'}
            else:
                return {'error': f'Invalid portfolio data format. Type: {type(portfolio_data)}'}
            
            # Handle case where portfolio might be None or empty
            if portfolio is None or not isinstance(portfolio, list):
                return {'error': 'Portfolio not found or empty'}
            
            # Find and update the investment
            investment_found = False
            for investment in portfolio:
                if str(investment.get('id')) == str(investment_id):  # Convert both to string for comparison
                    investment_found = True
                    
                    # Validate and update quantity
                    if quantity is not None:
                        if not isinstance(quantity, (int, float)) or quantity < 0:
                            return {'error': 'Invalid quantity value'}
                        investment['quantity'] = float(quantity)  # Ensure it's stored as float
                    
                    # Validate and update buy_price
                    if buy_price is not None:
                        if not isinstance(buy_price, (int, float)) or buy_price < 0:
                            return {'error': 'Invalid buy_price value'}
                        investment['buy_price'] = float(buy_price)  # Ensure it's stored as float
                    
                    break
            
            if not investment_found:
                return {'error': f'Investment with ID {investment_id} not found'}
            
            # Return the updated portfolio data in the same format as input
            if isinstance(portfolio_data, str):
                return {'portfolio_data': json.dumps(portfolio)}
            elif isinstance(portfolio_data, dict):
                # If original was a dict, put portfolio back in the same structure
                if 'portfolio' in portfolio_data:
                    portfolio_data['portfolio'] = portfolio
                elif 'data' in portfolio_data:
                    portfolio_data['data'] = portfolio
                elif 'investments' in portfolio_data:
                    portfolio_data['investments'] = portfolio
                else:
                    # If it was a single investment, return the updated investment
                    if len(portfolio) == 1:
                        return {'portfolio_data': portfolio[0]}
                    else:
                        return {'portfolio_data': portfolio}
                return {'portfolio_data': portfolio_data}
            else:
                return {'portfolio_data': portfolio}
                
        except Exception as e:
            return {'error': f'Error updating investment: {str(e)}'}
    
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