import json
import os
from Financial_Portfolio_Tracker.Portfolio_Management.GET.GET_Portfolio import Portfolio

class Delete_Portfolio:
    '''
    Delete an investment by investment id for user
    return: information message
    '''
    
    def __init__(self, portfolio_file: str = None, portfolio_data: list = None):
        """Initialize with portfolio file or data, matching Portfolio class constructor"""
        self.portfolio_instance = Portfolio(portfolio_file=portfolio_file, portfolio_data=portfolio_data)
    
    def delete_investment(self, investment_id):
        """
        Delete investment using instance method (non-static)
        Args:
            investment_id: Unique ID of the investment to delete
        Returns:
            Dictionary with success message or error tuple
        """
        try:
            # Load current portfolio
            portfolio = self.portfolio_instance.load_portfolio()
            
            # Handle case where portfolio might be None or empty
            if portfolio is None or not isinstance(portfolio, list):
                return {'error': 'Portfolio not found or empty'}, 404
            
            # Find the investment to delete and get its ticker for confirmation message
            deleted_ticker = None
            for investment in portfolio:
                if investment.get('id') == investment_id:
                    deleted_ticker = investment.get('ticker', 'Unknown')
                    break
            
            # Create new portfolio without the specified investment
            new_portfolio = [inv for inv in portfolio if inv.get('id') != investment_id]
            
            # Check if investment was actually found and removed
            if len(portfolio) == len(new_portfolio):
                return {'error': 'Investment not found'}, 404
            
            # Save the updated portfolio
            self.portfolio_instance.save_portfolio(new_portfolio)
            
            # Return success message with ticker info if available
            if deleted_ticker:
                return {'message': f'Investment {deleted_ticker} deleted successfully.'}
            else:
                return {'message': 'Investment deleted successfully.'}
                
        except Exception as e:
            return {'error': f'Error deleting investment: {str(e)}'}, 500
    
    def delete_multiple_investments(self, investment_ids):
        """
        Delete multiple investments by their IDs
        Args:
            investment_ids: List of investment IDs to delete
        Returns:
            Dictionary with results of deletion operation
        """
        try:
            portfolio = self.portfolio_instance.load_portfolio()
            
            if portfolio is None or not isinstance(portfolio, list):
                return {'error': 'Portfolio not found or empty'}, 404
            
            if not isinstance(investment_ids, list):
                return {'error': 'investment_ids must be a list'}, 400
            
            # Track what was deleted
            deleted_tickers = []
            not_found_ids = []
            
            # Find tickers for investments that exist
            for investment in portfolio:
                if investment.get('id') in investment_ids:
                    deleted_tickers.append(investment.get('ticker', 'Unknown'))
            
            # Create new portfolio without the specified investments
            new_portfolio = [inv for inv in portfolio if inv.get('id') not in investment_ids]
            
            # Calculate how many were actually deleted
            deleted_count = len(portfolio) - len(new_portfolio)
            not_found_count = len(investment_ids) - deleted_count
            
            if deleted_count == 0:
                return {'error': 'No investments found to delete'}, 404
            
            # Save the updated portfolio
            self.portfolio_instance.save_portfolio(new_portfolio)
            
            # Prepare response message
            message = f'{deleted_count} investment(s) deleted successfully.'
            if deleted_tickers:
                message += f' Deleted: {", ".join(deleted_tickers)}'
            if not_found_count > 0:
                message += f' {not_found_count} investment(s) not found.'
            
            return {'message': message, 'deleted_count': deleted_count, 'not_found_count': not_found_count}
            
        except Exception as e:
            return {'error': f'Error deleting investments: {str(e)}'}, 500
    
    def clear_portfolio(self):
        """
        Delete all investments from the portfolio
        Returns:
            Dictionary with success message or error
        """
        try:
            portfolio = self.portfolio_instance.load_portfolio()
            
            if portfolio is None or not isinstance(portfolio, list):
                return {'error': 'Portfolio not found or empty'}, 404
            
            investment_count = len(portfolio)
            if investment_count == 0:
                return {'message': 'Portfolio is already empty.'}
            
            # Save empty portfolio
            self.portfolio_instance.save_portfolio([])
            
            return {'message': f'Portfolio cleared successfully. {investment_count} investment(s) removed.'}
            
        except Exception as e:
            return {'error': f'Error clearing portfolio: {str(e)}'}, 500
 