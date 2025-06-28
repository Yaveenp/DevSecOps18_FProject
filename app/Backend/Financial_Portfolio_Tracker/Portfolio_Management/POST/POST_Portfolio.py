import json
import os
import uuid
from Financial_Portfolio_Tracker.Portfolio_Management.GET.GET_Portfolio import Portfolio

class Post_Portfolio:
    '''
    Adding an investment by investment id for user
    return: information message
    '''
    
    def __init__(self, portfolio_file: str = None, portfolio_data: dict = None):
        """Initialize with portfolio file or data, matching Portfolio class constructor"""
        self.portfolio_instance = Portfolio(portfolio_file=portfolio_file, portfolio_data=portfolio_data)
    
    def add_investment(self, ticker, quantity, buy_price):
        """
        Add investment using instance method (non-static)
        Args:
            ticker: Stock ticker symbol
            quantity: Number of shares
            buy_price: Price per share when purchased
        Returns:
            Dictionary with message and investment ID
        """
        # Load current portfolio
        portfolio = self.portfolio_instance.load_portfolio()
        
        # Handle case where portfolio might be None
        if portfolio is None:
            portfolio = []
        
        ticker = ticker.upper()

        new_investment = {
            'id': str(uuid.uuid4()),
            'ticker': ticker,
            'quantity': quantity,
            'buy_price': buy_price
        }
        
        portfolio.append(new_investment)
        
        # Save portfolio using the instance method
        self.portfolio_instance.save_portfolio(portfolio)
        
        return {'message': f"{ticker} added.", 'id': new_investment['id']}
    
    @staticmethod
    def add_investment_static(ticker, quantity, buy_price, portfolio_file: str = None, portfolio_data: dict = None):
        """
        Static method version for backward compatibility
        """
        post_portfolio = Post_Portfolio(portfolio_file=portfolio_file, portfolio_data=portfolio_data)
        return post_portfolio.add_investment(ticker, quantity, buy_price)

def add_investment_to_file(ticker, quantity, buy_price, portfolio_file):
    """Helper function to add investment to a file-based portfolio"""
    post_portfolio = Post_Portfolio(portfolio_file=portfolio_file)
    return post_portfolio.add_investment(ticker, quantity, buy_price)

def add_investment_to_data(ticker, quantity, buy_price, portfolio_data):
    """Helper function to add investment to in-memory portfolio data"""
    post_portfolio = Post_Portfolio(portfolio_data=portfolio_data)
    return post_portfolio.add_investment(ticker, quantity, buy_price)
