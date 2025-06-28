import json
import requests
import datetime

class Portfolio:
    '''
    Get portfolio for a user
    return: JSON of portfolio with quotes for user
    '''
    def __init__(self, portfolio_file: str = None, portfolio_data: dict = None):
        self.PORTFOLIO_FILE = portfolio_file
        self.portfolio_data = portfolio_data
        
    def load_portfolio(self):
        """Load portfolio from file or use provided data"""
        print("start load_portfolio")
        
        # If portfolio data is provided directly, use it
        if self.portfolio_data is not None:
            print("Using provided portfolio data")
            return self.portfolio_data
        
        # if self.PORTFOLIO_FILE:
        #     try:
        #         with open(self.PORTFOLIO_FILE, 'r') as f:
        #             return json.load(f)
        #     except FileNotFoundError:
        #         return []
        # return []

    @staticmethod
    def get_stock_quote(symbol, api_key):
        url = 'https://www.alphavantage.co/query'
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': api_key
        }
        response = requests.get(url, params=params)
        data = response.json()
        return data.get('Global Quote', {})

    def save_portfolio(self, portfolio):
        """Save portfolio to file (only works if portfolio_file is set)"""
        if self.PORTFOLIO_FILE:
            with open(self.PORTFOLIO_FILE, 'w') as f:
                json.dump(portfolio, f, indent=4)
        else:
            # If no file path, update the internal data
            self.portfolio_data = portfolio

    def get_portfolio_with_quotes(self, api_key):
        """Get portfolio with current stock quotes"""
        portfolio = self.load_portfolio()
        print(portfolio)
        results = []

        for stock in portfolio:
            quote = Portfolio.get_stock_quote(stock['ticker'], api_key)
            if quote:
                price = float(quote.get('05. price', 0))
                change_pct = quote.get('10. change percent', 'N/A')
                current_value = round(price * stock['quantity'], 2)
                gain = round((price - stock['buy_price']) * stock['quantity'], 2)
                results.append({
                    'id': stock['id'],
                    'ticker': stock['ticker'],
                    'quantity': stock['quantity'],
                    'buy_price': stock['buy_price'],
                    'current_price': price,
                    'value': current_value,
                    'gain': gain,
                    'change_percent': change_pct
                })

        return results

    def get_portfolio_with_quotes_from_data(self, api_key, portfolio_data):
        """Get portfolio with quotes from provided data"""
        print("Getting portfolio with quotes from data")
        results = []

        for stock in portfolio_data['portfolio']:
            quote = Portfolio.get_stock_quote(stock['ticker'], api_key)
            if quote:
                price = float(quote.get('05. price', 0))
                change_pct = quote.get('10. change percent', 'N/A')
                current_value = round(price * stock['quantity'], 2)
                gain = round((price - stock['buy_price']) * stock['quantity'], 2)
                results.append({
                    'id': stock['id'],
                    'ticker': stock['ticker'],
                    'quantity': stock['quantity'],
                    'buy_price': stock['buy_price'],
                    'current_price': price,
                    'value': current_value,
                    'gain': gain,
                    'change_percent': change_pct
                })

        return results

    @classmethod
    def get_portfolio_with_quotes_static(cls, api_key):
        """
        Static method that uses the class-level PORTFOLIO_FILE attribute
        This is for backward compatibility with your Flask app
        """
        if not hasattr(cls, 'PORTFOLIO_FILE') or not cls.PORTFOLIO_FILE:
            return []
        
        portfolio_instance = cls(cls.PORTFOLIO_FILE)
        return portfolio_instance.get_portfolio_with_quotes(api_key)

def portfolio_summaries(api_key, portfolio_data):
    """
    Calculate comprehensive portfolio analytics and summaries
    portfolio_data: Either file path (str) or portfolio data (list/dict)
    return: Dictionary with portfolio analytics data
    """
    # Handle both file path and direct data
    if isinstance(portfolio_data, str):
        # It's a file path (backward compatibility)
        portfolio_instance = Portfolio(portfolio_file=portfolio_data)
        portfolio_with_quotes = portfolio_instance.get_portfolio_with_quotes(api_key)
    else:
        # It's direct portfolio data
        portfolio_instance = Portfolio()
        portfolio_with_quotes = portfolio_instance.get_portfolio_with_quotes_from_data(api_key, portfolio_data)
    
    if not portfolio_with_quotes:
        return {
            'error': 'No portfolio data available',
            'total_stocks': 0,
            'total_value': 0.0,
            'total_investment': 0.0,
            'total_gain_loss': 0.0,
            'total_gain_loss_percent': 0.0
        }
    
    # Initialize summary variables
    total_value = 0.0
    total_investment = 0.0
    total_gain_loss = 0.0
    winning_stocks = 0
    losing_stocks = 0
    best_performer = None
    worst_performer = None
    stock_breakdown = []
    
    # Calculate portfolio metrics
    for stock in portfolio_with_quotes:
        # Basic calculations
        investment_amount = stock['buy_price'] * stock['quantity']
        current_value = stock['value']
        gain_loss = stock['gain']
        
        # Accumulate totals
        total_value += current_value
        total_investment += investment_amount
        total_gain_loss += gain_loss
        
        # Count winners and losers
        if gain_loss > 0:
            winning_stocks += 1
        elif gain_loss < 0:
            losing_stocks += 1
        
        # Track best and worst performers
        try:
            change_percent = float(stock['change_percent'].replace('%', '')) if isinstance(stock['change_percent'], str) else float(stock['change_percent'])
        except (ValueError, AttributeError):
            change_percent = 0.0
        
        stock_performance = {
            'ticker': stock['ticker'],
            'gain_loss': gain_loss,
            'change_percent': change_percent,
            'value': current_value,
            'weight': 0  # Will calculate after total_value is known
        }
        
        if best_performer is None or change_percent > best_performer['change_percent']:
            best_performer = stock_performance.copy()
        
        if worst_performer is None or change_percent < worst_performer['change_percent']:
            worst_performer = stock_performance.copy()
        
        stock_breakdown.append(stock_performance)
    
    # Calculate portfolio-level metrics
    total_gain_loss_percent = (total_gain_loss / total_investment * 100) if total_investment > 0 else 0.0
    
    # Calculate stock weights in portfolio
    for stock in stock_breakdown:
        stock['weight'] = (stock['value'] / total_value * 100) if total_value > 0 else 0.0
    
    # Sort stocks by value for additional insights
    top_holdings = sorted(stock_breakdown, key=lambda x: x['value'], reverse=True)[:5]
    
    # Calculate diversification metrics
    total_stocks = len(portfolio_with_quotes)
    avg_position_size = (total_value / total_stocks) if total_stocks > 0 else 0.0
    
    # Prepare summary response
    summary = {
        'timestamp': datetime.datetime.now().isoformat(),
        'portfolio_overview': {
            'total_stocks': total_stocks,
            'total_value': round(total_value, 2),
            'total_investment': round(total_investment, 2),
            'total_gain_loss': round(total_gain_loss, 2),
            'total_gain_loss_percent': round(total_gain_loss_percent, 2),
            'avg_position_size': round(avg_position_size, 2)
        },
        'performance_metrics': {
            'winning_stocks': winning_stocks,
            'losing_stocks': losing_stocks,
            'win_rate': round((winning_stocks / total_stocks * 100), 2) if total_stocks > 0 else 0.0,
            'best_performer': best_performer,
            'worst_performer': worst_performer
        },
        'top_holdings': top_holdings,
        'stock_breakdown': stock_breakdown,
        'risk_metrics': {
            'largest_position_weight': max([s['weight'] for s in stock_breakdown]) if stock_breakdown else 0.0,
            'concentration_risk': 'High' if any(s['weight'] > 20 for s in stock_breakdown) else 'Medium' if any(s['weight'] > 10 for s in stock_breakdown) else 'Low'
        }
    }
    
    return summary