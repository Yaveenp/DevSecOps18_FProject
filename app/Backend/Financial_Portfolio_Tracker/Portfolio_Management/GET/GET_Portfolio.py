import json
import os
import requests
import datetime

PORTFOLIO_FILE = 'portfolio.json'

class Portfolio:
    '''
    Get portfolio for a user
    returen: JSON of portfolio with quotes for user
    '''
    def __init__(self, PORTFOLIO_FILE: json):
        self.PORTFOLIO_FILE = PORTFOLIO_FILE
        
    def load_portfolio():
        if os.path.exists(PORTFOLIO_FILE):
            with open(PORTFOLIO_FILE, 'r') as f:
                return json.load(f)
        return []

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

    def save_portfolio(portfolio):
        with open(PORTFOLIO_FILE, 'w') as f:
            json.dump(portfolio, f, indent=4)

    def get_portfolio_with_quotes(api_key):
        portfolio = Portfolio.load_portfolio()
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

def portfolio_summaries(api_key):
    """
    Calculate comprehensive portfolio analytics and summaries
    return: Dictionary with portfolio analytics data
    """
    portfolio_data = Portfolio.get_portfolio_with_quotes(api_key)
    
    if not portfolio_data:
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
    for stock in portfolio_data:
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
    total_stocks = len(portfolio_data)
    avg_position_size = (total_value / total_stocks) if total_stocks > 0 else 0.0
    
    # Prepare summary response
    summary = {
        'timestamp': datetime.now().isoformat(),
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

if __name__ == '__main__':
    Portfolio.get_portfolio_with_quotes()