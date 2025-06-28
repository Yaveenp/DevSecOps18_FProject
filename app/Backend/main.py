from flask import Flask, jsonify, request, session
from flask_cors import CORS
from datetime import datetime, timedelta
import psycopg2
import os
import json
from flask_sqlalchemy import SQLAlchemy
from Financial_Portfolio_Tracker import Delete_Portfolio, Put_Portfolio, Post_Portfolio, Portfolio
from Financial_Portfolio_Tracker import Get_Market_Trends, Get_Ticker

app = Flask(__name__)
CORS(app)

# Secret key for session management
app.secret_key = 'your-secret-key-change-in-production'

# Alpha Vantage API Key - Set this in environment variables
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'your-api-key-here')

# SQLAlchemy DB config for PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:thisisastrongpassword@localhost:5432/investment_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Create User model based on the DB table
class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    last_login = db.Column(db.TIMESTAMP)
    session_expiration = db.Column(db.TIMESTAMP)
    
    # Relationship to portfolio files
    portfolio_files = db.relationship('PortfolioFile', backref='user', lazy=True, cascade='all, delete-orphan')
    # Relationship to portfolio summaries
    portfolio_summaries = db.relationship('PortfolioSummary', backref='user', lazy=True, cascade='all, delete-orphan')

# Portfolio Files model
class PortfolioFile(db.Model):
    __tablename__ = 'portfolio_files'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    filename = db.Column(db.Text, nullable=False)
    filepath = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

# Portfolio Summary model for analytics storage
class PortfolioSummary(db.Model):
    __tablename__ = 'portfolio_summaries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    
    # Portfolio Overview
    total_stocks = db.Column(db.Integer, default=0)
    total_value = db.Column(db.Numeric(15, 2), default=0.0)
    total_investment = db.Column(db.Numeric(15, 2), default=0.0)
    total_gain_loss = db.Column(db.Numeric(15, 2), default=0.0)
    total_gain_loss_percent = db.Column(db.Numeric(8, 4), default=0.0)
    avg_position_size = db.Column(db.Numeric(15, 2), default=0.0)
    
    # Performance Metrics
    winning_stocks = db.Column(db.Integer, default=0)
    losing_stocks = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Numeric(8, 4), default=0.0)
    best_performer_ticker = db.Column(db.String(10))
    best_performer_gain = db.Column(db.Numeric(15, 2))
    best_performer_percent = db.Column(db.Numeric(8, 4))
    worst_performer_ticker = db.Column(db.String(10))
    worst_performer_gain = db.Column(db.Numeric(15, 2))
    worst_performer_percent = db.Column(db.Numeric(8, 4))
    
    # Risk Metrics
    largest_position_weight = db.Column(db.Numeric(8, 4), default=0.0)
    concentration_risk = db.Column(db.String(20), default='Low')
    
    # JSON fields for complex data
    top_holdings = db.Column(db.JSON)
    stock_breakdown = db.Column(db.JSON)
    
    # Timestamps
    created_at = db.Column(db.TIMESTAMP, default=datetime.utcnow)
    updated_at = db.Column(db.TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

   
# Create User model based on the base Portfolio User needed
class PortfolioUser:
    def __init__(self, username: str, password: str, first_name: str, last_name: str):
        """
        Builder function to see if the user is already in database and if not create him
        # CHANGED: Fixed comment typo
        """
        self.username = username.lower()
        self.password = password.lower()
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.last_login = datetime.now() - timedelta(minutes=30)
        self.session_expiration = datetime.now() - timedelta(hours=1)
        self.is_expired = False
        self.user_id = 0

    def user_create(self, username: str, password: str, first_name: str, last_name: str):
        """
        Checks if user is already in database and if not send it to be created
        # CHANGED: Simplified docstring
        """
        try:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                return "Username already exist"
            else:
                # Creates new user using the user database class
                new_user = User(username=username, password=password,
                               first_name=first_name, last_name=last_name)
                db.session.add(new_user)
                db.session.flush()  # get the user_id before commit
                
                # Create initial portfolio file for the new user
                initial_portfolio = PortfolioFile(
                    user_id=new_user.user_id,
                    filename=f"{username}_portfolio.json",
                    filepath=f"/uploads/{username}_portfolio.json"
                )
                db.session.add(initial_portfolio)
                db.session.commit()
                
                # Create empty portfolio JSON file
                self._create_empty_portfolio_file(f"/uploads/{username}_portfolio.json")
                
                self.user_id = new_user.user_id
                return f'User {self.username} was successfully registered. Please login'
        except Exception as e:
            db.session.rollback()
            print(e)
            return "Parameters are not entered correctly, please try again."

    def user_login(self, username: str, password: str):
        """
        Checks user credentials in database and add session timeout stamp
        # CHANGED: Fixed typo "cardinals" -> "credentials"
        """
        try:
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                user.last_login = datetime.now()
                user.session_expiration = user.last_login + timedelta(minutes=15)
                db.session.commit() 
                self.is_expired = False
                self.user_id = user.user_id
                self.session_expiration = user.session_expiration 
                return True 
            return False 
        except Exception as e:
            print(e)
            return False 

    def session_expired(self):
        """
        Checks if user login session is still valid
        """
        if self.session_expiration < datetime.now():
            self.is_expired = True
            return True  
        else:
            return False 
    
    def _create_empty_portfolio_file(self, filepath):
        """
        Create an empty portfolio JSON file for new users
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Create empty portfolio
            empty_portfolio = []
            with open(filepath, 'w') as f:
                json.dump(empty_portfolio, f, indent=4)
        except Exception as e:
            print(f"Error creating portfolio file: {e}") 


def get_current_user():
    """
    Get current logged-in user from session
    """
    if 'user_id' not in session:
        return None
    
    try:
        user = User.query.get(session['user_id'])
        if user and user.session_expiration and user.session_expiration > datetime.now():
            return user
        else:
            # If session expired clean it
            session.clear()
            return None
    except Exception as e:
        print(e)
        return None


def get_user_portfolio_file_path(user_id):
    """
    Get the portfolio file path for a specific user
    """
    portfolio_file = PortfolioFile.query.filter_by(user_id=user_id).first()
    if portfolio_file:
        return portfolio_file.filepath
    return None


def portfolio_summaries(api_key, portfolio_file_path):
    """
    Calculate comprehensive portfolio analytics and summaries
    return: Dictionary with portfolio analytics data
    """
    # Temporarily set the global PORTFOLIO_FILE for the Portfolio class
    original_file = getattr(Portfolio, 'PORTFOLIO_FILE', None)
    Portfolio.PORTFOLIO_FILE = portfolio_file_path
    
    try:
        portfolio_data = Portfolio.get_portfolio_with_quotes(api_key)
    finally:
        # Restore original file path
        if original_file:
            Portfolio.PORTFOLIO_FILE = original_file
    
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


def save_portfolio_summary_to_db(user_id, summary_data):
    """
    Save portfolio summary to database
    """
    try:
        # Check if summary already exists for today
        today = datetime.now().date()
        existing_summary = PortfolioSummary.query.filter_by(user_id=user_id).filter(
            db.func.date(PortfolioSummary.created_at) == today
        ).first()
        
        if existing_summary:
            # Update existing summary
            summary_obj = existing_summary
        else:
            # Create new summary
            summary_obj = PortfolioSummary(user_id=user_id)
            db.session.add(summary_obj)
        
        # Update fields
        overview = summary_data.get('portfolio_overview', {})
        performance = summary_data.get('performance_metrics', {})
        risk = summary_data.get('risk_metrics', {})
        
        summary_obj.total_stocks = overview.get('total_stocks', 0)
        summary_obj.total_value = overview.get('total_value', 0.0)
        summary_obj.total_investment = overview.get('total_investment', 0.0)
        summary_obj.total_gain_loss = overview.get('total_gain_loss', 0.0)
        summary_obj.total_gain_loss_percent = overview.get('total_gain_loss_percent', 0.0)
        summary_obj.avg_position_size = overview.get('avg_position_size', 0.0)
        
        summary_obj.winning_stocks = performance.get('winning_stocks', 0)
        summary_obj.losing_stocks = performance.get('losing_stocks', 0)
        summary_obj.win_rate = performance.get('win_rate', 0.0)
        
        best_performer = performance.get('best_performer', {})
        if best_performer:
            summary_obj.best_performer_ticker = best_performer.get('ticker')
            summary_obj.best_performer_gain = best_performer.get('gain_loss')
            summary_obj.best_performer_percent = best_performer.get('change_percent')
        
        worst_performer = performance.get('worst_performer', {})
        if worst_performer:
            summary_obj.worst_performer_ticker = worst_performer.get('ticker')
            summary_obj.worst_performer_gain = worst_performer.get('gain_loss')
            summary_obj.worst_performer_percent = worst_performer.get('change_percent')
        
        summary_obj.largest_position_weight = risk.get('largest_position_weight', 0.0)
        summary_obj.concentration_risk = risk.get('concentration_risk', 'Low')
        
        summary_obj.top_holdings = summary_data.get('top_holdings', [])
        summary_obj.stock_breakdown = summary_data.get('stock_breakdown', [])
        
        summary_obj.updated_at = datetime.utcnow()
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving portfolio summary: {e}")
        return False


@app.get('/api/portfolio/health')
def health():
    try:
        return jsonify({'status': 'healthy'}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "not healthy"}), 500

@app.post('/api/portfolio/signup')
def signup():
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({"message": "No data provided"}), 400
        
        username = str(request_data.get("username", ""))
        password = str(request_data.get("password", ""))
        first_name = str(request_data.get("first_name", ""))
        last_name = str(request_data.get("last_name", ""))
        
        if (username.isascii() and password.isascii() and first_name.isascii() and last_name.isascii()
                and len(username) >= 3 and len(password) >= 3):
            
            portfolio_user = PortfolioUser(username, password, first_name, last_name)
            result = portfolio_user.user_create(username, password, first_name, last_name)
            
            if "already exist" in result:
                return jsonify({"message": "Username already exists, please try again."}), 403
            else:
                return jsonify({"message": "Successfully registered. Please login."}), 200
        else:
            return jsonify({"message": "Parameters are not entered correctly, please try again."}), 403
            
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred during registration"}), 500

@app.post('/api/portfolio/signin')
def signin():
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({"message": "No data provided"}), 400
        
        username = str(request_data.get("username", ""))
        password = str(request_data.get("password", "")) 
        
        if username.isascii() and password.isascii() and len(username) >= 3 and len(password) >= 3: 
            portfolio_user = PortfolioUser(username, password, "", "") 
            login_success = portfolio_user.user_login(username, password)
            
            if login_success:
                session['user_id'] = portfolio_user.user_id
                session['username'] = username
                return jsonify({"message": "Successful login"}), 200
            else:
                return jsonify({"message": "Username or password are wrong or user doesn't exist"}), 401
        else:
            return jsonify({"message": "Parameters are not entered correctly, please try again."}), 403
            
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred during login"}), 500 
    

@app.get('/api/portfolio')
def portfolio_list():
    """
    List of investments with real-time quotes
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401
        
        # Get user's portfolio file path
        portfolio_file_path = get_user_portfolio_file_path(current_user.user_id)
        if not portfolio_file_path:
            return jsonify({"message": "Portfolio file not found"}), 404
        
        # Load portfolio and get quotes
        try:
            # Temporarily set the global PORTFOLIO_FILE for the Portfolio class
            original_file = Portfolio.PORTFOLIO_FILE if hasattr(Portfolio, 'PORTFOLIO_FILE') else None
            Portfolio.PORTFOLIO_FILE = portfolio_file_path
            
            portfolio_with_quotes = Portfolio.get_portfolio_with_quotes(ALPHA_VANTAGE_API_KEY)
            
            # Restore original file path
            if original_file:
                Portfolio.PORTFOLIO_FILE = original_file
                
            return jsonify({
                "message": "portfolio retrieved successfully", 
                "user": current_user.username,
                "portfolio": portfolio_with_quotes
            }), 200
            
        except Exception as e:
            print(f"Error loading portfolio: {e}")
            return jsonify({"message": "Error loading portfolio data"}), 500
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500

@app.post('/api/portfolio')
def portfolio_add():
    """
    Add a new investment
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401 
        
        request_data = request.get_json()
        if not request_data:
            return jsonify({"message": "No data provided"}), 400
        
        ticker = request_data.get("ticker", "").upper()
        quantity = request_data.get("quantity")
        buy_price = request_data.get("buy_price")
        
        if not ticker or not quantity or not buy_price:
            return jsonify({"message": "Missing required fields: ticker, quantity, buy_price"}), 400
        
        try:
            quantity = float(quantity)
            buy_price = float(buy_price)
        except ValueError:
            return jsonify({"message": "Quantity and buy_price must be numbers"}), 400
        
        # Get user's portfolio file path
        portfolio_file_path = get_user_portfolio_file_path(current_user.user_id)
        if not portfolio_file_path:
            return jsonify({"message": "Portfolio file not found"}), 404
        
        # Temporarily set the global PORTFOLIO_FILE for the Portfolio class
        original_file = getattr(Portfolio, 'PORTFOLIO_FILE', None)
        Portfolio.PORTFOLIO_FILE = portfolio_file_path
        
        result = Post_Portfolio.add_investment(ticker, quantity, buy_price)
        
        # Restore original file path
        if original_file:
            Portfolio.PORTFOLIO_FILE = original_file
        
        return jsonify(result), 200
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500

@app.put('/api/portfolio/<investment_id>')
def portfolio_update(investment_id):
    """
    Update an investment
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401
        
        request_data = request.get_json()
        if not request_data:
            return jsonify({"message": "No data provided"}), 400
        
        quantity = request_data.get("quantity")
        buy_price = request_data.get("buy_price")
        
        if quantity is not None:
            try:
                quantity = float(quantity)
            except ValueError:
                return jsonify({"message": "Quantity must be a number"}), 400
        
        if buy_price is not None:
            try:
                buy_price = float(buy_price)
            except ValueError:
                return jsonify({"message": "Buy price must be a number"}), 400
        
        # Get user's portfolio file path
        portfolio_file_path = get_user_portfolio_file_path(current_user.user_id)
        if not portfolio_file_path:
            return jsonify({"message": "Portfolio file not found"}), 404
        
        # Temporarily set the global PORTFOLIO_FILE for the Portfolio class
        original_file = getattr(Portfolio, 'PORTFOLIO_FILE', None)
        Portfolio.PORTFOLIO_FILE = portfolio_file_path
        
        result = Put_Portfolio.update_investment(investment_id, quantity, buy_price)
        
        # Restore original file path
        if original_file:
            Portfolio.PORTFOLIO_FILE = original_file
        
        if 'error' in result:
            return jsonify(result), 404
        return jsonify(result), 200
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500

@app.delete('/api/portfolio/<investment_id>')
def portfolio_remove(investment_id):
    """
    Delete an investment
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401
        
        # Get user's portfolio file path
        portfolio_file_path = get_user_portfolio_file_path(current_user.user_id)
        if not portfolio_file_path:
            return jsonify({"message": "Portfolio file not found"}), 404
        
        # Temporarily set the global PORTFOLIO_FILE for the Portfolio class
        original_file = getattr(Portfolio, 'PORTFOLIO_FILE', None)
        Portfolio.PORTFOLIO_FILE = portfolio_file_path
        
        result = Delete_Portfolio.delete_investment(investment_id)
        
        # Restore original file path
        if original_file:
            Portfolio.PORTFOLIO_FILE = original_file
        
        if 'error' in result:
            return jsonify(result), 404
        return jsonify(result), 200
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500 

@app.get('/api/stocks/<ticker>')
def portfolio_real(ticker):
    """
    Real-time stock data for a specific ticker symbol
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401
        
        ticker = ticker.upper()
        result = Get_Ticker.get_stock_quote(ticker, ALPHA_VANTAGE_API_KEY)
        
        if 'error' in result:
            return jsonify(result), 404
        
        return jsonify({
            "message": "Stock data retrieved successfully",
            "ticker": ticker,
            "data": result
        }), 200
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500

@app.get('/api/stocks/market')
def portfolio_market():
    """
    Market trends and updates
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401 
        
        # Note: The Get_Market_Trends class needs API key integration
        # For now, return a placeholder response
        try:
            result = Get_Market_Trends.get_top_gainers()
            return jsonify({
                "message": "Market trends retrieved successfully",
                "data": result
            }), 200
        except Exception as e:
            print(f"Market trends error: {e}")
            return jsonify({
                "message": "Market trends service temporarily unavailable",
                "data": []
            }), 200
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500 

@app.get('/api/portfolio/analytics')
def portfolio_analytics():
    """
    User portfolio profit/loss data and growth trends with comprehensive analytics
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401  
        
        # Get user's portfolio file path
        portfolio_file_path = get_user_portfolio_file_path(current_user.user_id)
        if not portfolio_file_path:
            return jsonify({"message": "Portfolio file not found"}), 404
        
        # Calculate portfolio analytics
        try:
            analytics_data = portfolio_summaries(ALPHA_VANTAGE_API_KEY, portfolio_file_path)
            
            if 'error' in analytics_data:
                return jsonify({
                    "message": "Portfolio analytics calculated successfully",
                    "user": current_user.username,
                    "analytics": analytics_data
                }), 200
            
            # Save analytics to database
            save_success = save_portfolio_summary_to_db(current_user.user_id, analytics_data)
            if not save_success:
                print("Warning: Failed to save portfolio summary to database")
            
            return jsonify({
                "message": "Portfolio analytics calculated successfully",
                "user": current_user.username,
                "analytics": analytics_data
            }), 200
            
        except Exception as e:
            print(f"Error calculating portfolio analytics: {e}")
            return jsonify({"message": "Error calculating portfolio analytics"}), 500
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500 

@app.get('/api/portfolio/analytics/history')
def portfolio_analytics_history():
    """
    Get historical portfolio analytics for the current user
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401
        
        # Get historical summaries for the user
        summaries = PortfolioSummary.query.filter_by(user_id=current_user.user_id).order_by(
            PortfolioSummary.created_at.desc()
        ).limit(30).all()  # Get last 30 days
        
        history_data = []
        for summary in summaries:
            history_data.append({
                'date': summary.created_at.isoformat(),
                'total_value': float(summary.total_value),
                'total_investment': float(summary.total_investment),
                'total_gain_loss': float(summary.total_gain_loss),
                'total_gain_loss_percent': float(summary.total_gain_loss_percent),
                'total_stocks': summary.total_stocks,
                'winning_stocks': summary.winning_stocks,
                'losing_stocks': summary.losing_stocks,
                'win_rate': float(summary.win_rate),
                'concentration_risk': summary.concentration_risk
            })
        
        return jsonify({
            "message": "Portfolio analytics history retrieved successfully",
            "user": current_user.username,
            "history": history_data
        }), 200
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5050, debug=True) # Debug mode - Remove before production