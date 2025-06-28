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
        
        if self.PORTFOLIO_FILE:
            try:
                with open(self.PORTFOLIO_FILE, 'r') as f:
                    return json.load(f)
            except FileNotFoundError:
                return []
        return []

    @staticmethod
    def get_stock_quote(symbol, api_key):
        try:
            url = 'https://www.alphavantage.co/query'
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': api_key
            }
            response = requests.get(url, params=params)
            data = response.json()
            return data.get('Global Quote', {})
        except Exception as e:
            print(f"Error getting stock quote for {symbol}: {e}")
            return {}

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
        print(f"Loaded portfolio: {portfolio}")
        results = []

        # Ensure portfolio is a list
        if not isinstance(portfolio, list):
            print(f"Portfolio is not a list, it's: {type(portfolio)}")
            return results

        for stock in portfolio:
            if not isinstance(stock, dict):
                print(f"Stock item is not a dict, it's: {type(stock)}")
                continue
                
            # Ensure required fields exist
            if not all(key in stock for key in ['ticker', 'quantity', 'buy_price', 'id']):
                print(f"Stock missing required fields: {stock}")
                continue
                
            quote = Portfolio.get_stock_quote(stock['ticker'], api_key)
            if quote:
                try:
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
                except (ValueError, TypeError) as e:
                    print(f"Error processing stock {stock.get('ticker', 'unknown')}: {e}")
                    continue

        return results

    def get_portfolio_with_quotes_from_data(self, api_key, portfolio_data):
        """Get portfolio with quotes from provided data"""
        print(f"Getting portfolio with quotes from data: {type(portfolio_data)}")
        print(f"Portfolio data content: {portfolio_data}")
        
        results = []

        # Handle different data formats
        stocks = []
        
        # Handle the case where portfolio_data is a dict with a "portfolio" key containing JSON string
        if isinstance(portfolio_data, dict) and 'portfolio' in portfolio_data:
            portfolio_value = portfolio_data['portfolio']
            if isinstance(portfolio_value, str):
                try:
                    # Parse the JSON string
                    stocks = json.loads(portfolio_value)
                    print(f"Parsed JSON string from 'portfolio' key, found {len(stocks)} stocks")
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON from 'portfolio' key: {e}")
                    return results
            else:
                stocks = portfolio_value
        elif isinstance(portfolio_data, str):
            try:
                # If it's a JSON string, parse it
                portfolio_data = json.loads(portfolio_data)
                stocks = portfolio_data
            except json.JSONDecodeError:
                print("Error: portfolio_data is not valid JSON")
                return results
        elif isinstance(portfolio_data, dict):
            # Check if the data has a 'holdings' key
            if 'holdings' in portfolio_data:
                stocks = portfolio_data['holdings']
                print(f"Found holdings key with {len(stocks)} stocks")
            else:
                # Check if the dict itself looks like a stock (has ticker, quantity, buy_price)
                if all(key in portfolio_data for key in ['ticker', 'quantity', 'buy_price']):
                    stocks = [portfolio_data]
                else:
                    print(f"Dict doesn't have expected keys: {list(portfolio_data.keys())}")
                    return results
        elif isinstance(portfolio_data, list):
            stocks = portfolio_data
        else:
            print(f"Unexpected portfolio_data type: {type(portfolio_data)}")
            return results

        print(f"Processing {len(stocks)} stocks")

        for i, stock in enumerate(stocks):
            print(f"Processing stock {i}: {stock['ticker'] if isinstance(stock, dict) and 'ticker' in stock else 'unknown'}")
            
            if not isinstance(stock, dict):
                print(f"Stock {i} is not a dict, skipping")
                continue
                
            # Ensure required fields exist
            required_fields = ['ticker', 'quantity', 'buy_price']
            if not all(key in stock for key in required_fields):
                print(f"Stock {i} missing required fields: {list(stock.keys())}")
                continue
            
            try:
                # If the stock already has current data, use it; otherwise fetch from API
                if 'current_price' in stock and 'gain' in stock and 'value' in stock:
                    # Use existing data (faster, no API call needed)
                    print(f"Using existing data for {stock['ticker']}")
                    result_stock = {
                        'id': stock.get('id', i),
                        'ticker': stock['ticker'],
                        'quantity': float(stock['quantity']),
                        'buy_price': float(stock['buy_price']),
                        'current_price': float(stock['current_price']),
                        'value': float(stock['value']),
                        'gain': float(stock['gain']),
                        'change_percent': stock.get('change_percent', 'N/A'),
                        'company_name': stock.get('company_name', '')
                    }
                    results.append(result_stock)
                    print(f"Successfully processed stock from existing data: {stock['ticker']}")
                else:
                    # Fetch fresh data from API
                    quote = Portfolio.get_stock_quote(stock['ticker'], api_key)
                    if quote and '05. price' in quote:
                        price = float(quote.get('05. price', 0))
                        change_pct = quote.get('10. change percent', 'N/A')
                        current_value = round(price * float(stock['quantity']), 2)
                        gain = round((price - float(stock['buy_price'])) * float(stock['quantity']), 2)
                        
                        result_stock = {
                            'id': stock.get('id', i),
                            'ticker': stock['ticker'],
                            'quantity': float(stock['quantity']),
                            'buy_price': float(stock['buy_price']),
                            'current_price': price,
                            'value': current_value,
                            'gain': gain,
                            'change_percent': change_pct,
                            'company_name': stock.get('company_name', '')
                        }
                        
                        results.append(result_stock)
                        print(f"Successfully processed stock from API: {result_stock}")
                    else:
                        print(f"No quote data available for {stock['ticker']}")
                        
            except (ValueError, TypeError, KeyError) as e:
                print(f"Error processing stock {stock.get('ticker', 'unknown')}: {e}")
                continue

        print(f"Returning {len(results)} processed stocks")
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
    try:
        # Handle both file path and direct data
        if isinstance(portfolio_data, str) and portfolio_data.endswith('.json'):
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
            try:
                # Basic calculations
                investment_amount = float(stock['buy_price']) * float(stock['quantity'])
                current_value = float(stock['value'])
                gain_loss = float(stock['gain'])
                
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
                
            except (ValueError, TypeError, KeyError) as e:
                print(f"Error processing stock in summary: {e}")
                continue
        
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
            'holdings': portfolio_with_quotes,  # Add the detailed holdings data
            'risk_metrics': {
                'largest_position_weight': max([s['weight'] for s in stock_breakdown]) if stock_breakdown else 0.0,
                'concentration_risk': 'High' if any(s['weight'] > 20 for s in stock_breakdown) else 'Medium' if any(s['weight'] > 10 for s in stock_breakdown) else 'Low'
            }
        }
        
        return summary
        
    except Exception as e:
        print(f"Error in portfolio_summaries: {e}")
        return {
            'error': f'Error calculating portfolio summary: {str(e)}',
            'total_stocks': 0,
            'total_value': 0.0,
            'total_investment': 0.0,
            'total_gain_loss': 0.0,
            'total_gain_loss_percent': 0.0
        }