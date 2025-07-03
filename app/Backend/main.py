from flask import Flask, jsonify, request, session
from flask_cors import CORS
from datetime import datetime, timedelta
import psycopg2
import os
import json
import psutil
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.mutable import MutableDict
from Financial_Portfolio_Tracker.Portfolio_Management.PUT.PUT_Portfolio import Put_Portfolio
from Financial_Portfolio_Tracker.Portfolio_Management.DELETE.DELETE_Portfolio import Delete_Portfolio
from Financial_Portfolio_Tracker.Portfolio_Management.GET.GET_Portfolio import Portfolio
from Financial_Portfolio_Tracker.Portfolio_Management.POST.POST_Portfolio import Post_Portfolio
from Financial_Portfolio_Tracker.Real_Time_Stock_Data.GET_Market_Trends import Get_Market_Trends
from Financial_Portfolio_Tracker.Real_Time_Stock_Data.GET_Ticker import Get_Ticker
from prometheus_client import Counter, Histogram, generate_latest, Gauge, CONTENT_TYPE_LATEST

app = Flask(__name__)
CORS(app)

# Prometheus metrics
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ['method', 'endpoint'])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency", ['endpoint'])
CPU_USAGE = Gauge("container_cpu_usage_percent", "CPU usage percent")
MEMORY_USAGE = Gauge("container_memory_usage_bytes", "Memory usage in bytes")

@app.before_request
def start_timer():
    request.start_time = datetime.now()

@app.after_request
def record_request_data(response):
    duration = (datetime.now() - request.start_time).total_seconds()
    REQUEST_LATENCY.labels(request.path).observe(duration)
    REQUEST_COUNT.labels(request.method, request.path).inc()
    return response

# Secret key for session management
app.secret_key = 'your-secret-key-change-in-production'

# Alpha Vantage API Key - Set this in environment variables
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'X6NBB1E83XW59B9M') #API Key for test, should be?

# SQLAlchemy DB config for PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:thisisastrongpassword@postgres:5432/investment_db'
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True, nullable=False)
    filename = db.Column(db.Text, nullable=False)
    file_content = db.Column(MutableDict.as_mutable(db.JSON), nullable=False)
    created_at = db.Column(db.TIMESTAMP, default=datetime.now())
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now(), onupdate=datetime.now())
    

# Portfolio Summary model for analytics storage
class PortfolioSummary(db.Model):
    __tablename__ = 'portfolio_summaries'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True, nullable=False)
    
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
    created_at = db.Column(db.TIMESTAMP, default=datetime.now())
    updated_at = db.Column(db.TIMESTAMP, default=datetime.now(), onupdate=datetime.now())

   
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
                    file_content={
                        "portfolio_name": f"{username} Diversified Portfolio",
                        "total_value": 0.0,
                        "total_investment": 0.0,
                        "total_gain_loss": 0.0,
                        "holdings": []
                    }
                )
                db.session.add(initial_portfolio)
                db.session.commit()
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

def get_current_user():
    """
    Get current logged-in user from session
    """
    if 'user_id' not in session:
        return None
    
    try:
        user = db.session.get(User, session['user_id'])
        if user and user.session_expiration and user.session_expiration > datetime.now():
            return user
        else:
            # If session expired clean it
            session.clear()
            return None
    except Exception as e:
        print(e)
        return None


def get_user_portfolio_data(user_id):
    """
    Get the portfolio data for a specific user from database
    """
    portfolio_file = PortfolioFile.query.filter_by(user_id=user_id).first()
    if portfolio_file:
        return portfolio_file.file_content
    return None


def portfolio_summaries(api_key, portfolio_data):
    """
    Calculate comprehensive portfolio analytics and summaries
    return: Dictionary with portfolio analytics data
    """
    if not portfolio_data:
        return {
            'error': 'No portfolio data available',
            'total_stocks': 0,
            'total_value': 0.0,
            'total_investment': 0.0,
            'total_gain_loss': 0.0,
            'total_gain_loss_percent': 0.0
        }
    
    # Extract stocks from portfolio data structure
    stocks = []
    if isinstance(portfolio_data, dict) and 'holdings' in portfolio_data:
        stocks = portfolio_data['holdings']
    elif isinstance(portfolio_data, list):
        stocks = portfolio_data
    else:
        return {
            'error': 'Invalid portfolio data format',
            'total_stocks': 0,
            'total_value': 0.0,
            'total_investment': 0.0,
            'total_gain_loss': 0.0,
            'total_gain_loss_percent': 0.0
        }
    
    # Use the stocks directly since they already have current prices
    portfolio_with_quotes = stocks
    
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
    from datetime import timezone
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
        
        summary_obj.updated_at = datetime.now(timezone.utc)
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving portfolio summary: {e}")
        return False


@app.get('/api/portfolio/health') # WORKS
def health():
    try:
        return jsonify({'status': 'healthy'}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "not healthy"}), 500

@app.post('/api/portfolio/signup') # WORKS
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

@app.post('/api/portfolio/signin') # WORKS
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
    

@app.get('/api/portfolio') # WORKS
def portfolio_list():
    """
    List of investments with real-time quotes
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401
        
        # Get user's portfolio data from database
        portfolio_data = get_user_portfolio_data(current_user.user_id)
        if not portfolio_data:
            return jsonify({"message": "Portfolio data not found"}), 404
        
        # Load portfolio and get quotes
        try:
            # Create Portfolio instance and get quotes from JSON data
            portfolio_instance = Portfolio()
            portfolio_with_quotes = portfolio_instance.get_portfolio_with_quotes_from_data(ALPHA_VANTAGE_API_KEY, portfolio_data)
            
            # Always return a dict, never a list directly
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
        company_name = request_data.get("company_name", "")
        current_price = request_data.get("current_price", 0.0)
        value = request_data.get("value", 0.0)
        gain = request_data.get("gain", 0.0)
        change_percent = request_data.get("change_percent", 0.0)

        if not ticker or not quantity or not buy_price:
            return jsonify({"message": "Missing required fields: ticker, quantity, buy_price"}), 400

        try:
            quantity = float(quantity)
            buy_price = float(buy_price)
            current_price = float(current_price)
            value = float(value)
            gain = float(gain)
            change_percent = float(change_percent)
        except ValueError:
            return jsonify({"message": "All numeric fields must be valid numbers"}), 400

        portfolio_file = PortfolioFile.query.filter_by(user_id=current_user.user_id).first()
        if not portfolio_file:
            return jsonify({"message": "Portfolio not found"}), 404

        if any(inv.get('ticker', '').upper() == ticker for inv in portfolio_file.file_content.get('holdings', [])):
            return jsonify({"message": f"Investment with ticker '{ticker}' already exists."}), 409

        # Add investment to portfolio data
        result = Post_Portfolio.add_investment(
            portfolio_file.file_content,
            ticker,
            quantity,
            buy_price
        )

        if result['portfolio_data']['holdings']:
            last_investment = result['portfolio_data']['holdings'][-1]
            last_investment['ticker'] = ticker
            last_investment['company_name'] = company_name
            last_investment['quantity'] = quantity
            last_investment['buy_price'] = buy_price
            last_investment['current_price'] = current_price
            last_investment['value'] = value
            last_investment['gain'] = gain
            last_investment['change_percent'] = change_percent
            if 'created_at' not in last_investment:
                last_investment['created_at'] = datetime.now().isoformat()
            last_investment['updated_at'] = datetime.now().isoformat()

        portfolio_file.file_content = result['portfolio_data']
        portfolio_file.updated_at = datetime.now()

        db.session.execute(
            db.text("""
                INSERT INTO stocks (user_id, ticker, quantity, buy_price, current_price, value, gain, change_percent, created_at, updated_at)
                VALUES (:user_id, :ticker, :quantity, :buy_price, :current_price, :value, :gain, :change_percent, :created_at, :updated_at)
                ON CONFLICT (user_id, ticker) DO UPDATE SET
                    quantity = EXCLUDED.quantity,
                    buy_price = EXCLUDED.buy_price,
                    current_price = EXCLUDED.current_price,
                    value = EXCLUDED.value,
                    gain = EXCLUDED.gain,
                    change_percent = EXCLUDED.change_percent,
                    updated_at = EXCLUDED.updated_at
            """), {
                "user_id": current_user.user_id,
                "ticker": ticker,
                "quantity": quantity,
                "buy_price": buy_price,
                "current_price": current_price,
                "value": value,
                "gain": gain,
                "change_percent": change_percent,
                "created_at": last_investment['created_at'],
                "updated_at": last_investment['updated_at']
            }
        )
        db.session.commit()

        analytics_data = portfolio_summaries(ALPHA_VANTAGE_API_KEY, result['portfolio_data'])
        save_portfolio_summary_to_db(current_user.user_id, analytics_data)

        return jsonify({"message": "Investment added successfully"}), 200

    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500

@app.put('/api/portfolio/<investment_id>') # WORKS
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
        # Both fields are optional
        quantity = request_data.get("quantity", None)
        buy_price = request_data.get("buy_price", None)
        update_quantity = quantity is not None
        update_buy_price = buy_price is not None
        if update_quantity:
            try:
                quantity = float(quantity)
            except ValueError:
                return jsonify({"message": "Quantity must be a number"}), 400
        if update_buy_price:
            try:
                buy_price = float(buy_price)
            except ValueError:
                return jsonify({"message": "Buy price must be a number"}), 400
        if not update_quantity and not update_buy_price:
            return jsonify({"message": "At least one of quantity or buy_price must be provided"}), 400
        # Get user's portfolio data from database
        portfolio_file = PortfolioFile.query.filter_by(user_id=current_user.user_id).first()
        if not portfolio_file:
            return jsonify({"message": "Portfolio not found"}), 404
        # Update investment in portfolio data
        result = Put_Portfolio.update_investment_in_data(
            portfolio_file.file_content,
            investment_id,
            quantity if update_quantity else None,
            buy_price if update_buy_price else None
        )
        if 'error' in result:
            return jsonify(result), 404
        # Find the updated investment for stocks table
        updated_inv = result.get('updated_investment')
        if updated_inv:
            db.session.execute(
                db.text("""
                    UPDATE stocks SET
                        quantity = :quantity,
                        buy_price = :buy_price,
                        updated_at = :updated_at
                    WHERE user_id = :user_id AND ticker = :ticker
                """), {
                    "user_id": current_user.user_id,
                    "ticker": updated_inv['ticker'],
                    "quantity": updated_inv['quantity'],
                    "buy_price": updated_inv['buy_price'],
                    "updated_at": updated_inv['updated_at']
                }
            )
        # Update the database with modified portfolio data
        portfolio_file.file_content = result['portfolio_data']
        portfolio_file.updated_at = datetime.now()
        db.session.commit()
        # Update portfolio_summaries
        analytics_data = portfolio_summaries(ALPHA_VANTAGE_API_KEY, result['portfolio_data'])
        save_portfolio_summary_to_db(current_user.user_id, analytics_data)
        return jsonify({"message": "Investment updated successfully"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500

@app.delete('/api/portfolio/<investment_id>') # WORKS
def portfolio_remove(investment_id):
    """
    Delete an investment
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401
        # Get user's portfolio data from database
        portfolio_file = PortfolioFile.query.filter_by(user_id=current_user.user_id).first()
        if not portfolio_file:
            return jsonify({"message": "Portfolio not found"}), 404
        # Delete investment from portfolio data (no DB commit in CRUD)
        result = Delete_Portfolio.delete_investment_from_data(
            portfolio_file.file_content, investment_id
        )
        if 'error' in result:
            return jsonify(result), 404
        # Remove from stocks table if ticker is known
        deleted_ticker = result.get('deleted_ticker')
        if deleted_ticker:
            db.session.execute(
                db.text("DELETE FROM stocks WHERE user_id = :user_id AND ticker = :ticker"),
                {"user_id": current_user.user_id, "ticker": deleted_ticker}
            )
        # Update the database with modified portfolio data
        portfolio_file.file_content = result['portfolio_data']
        portfolio_file.updated_at = datetime.now()
        db.session.commit()
        # Update portfolio_summaries
        analytics_data = portfolio_summaries(ALPHA_VANTAGE_API_KEY, result['portfolio_data'])
        save_portfolio_summary_to_db(current_user.user_id, analytics_data)
        return jsonify({"message": "Investment deleted successfully"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500 

@app.get('/api/stocks/<ticker>') # WORKS
def portfolio_real(ticker):
    """
    Real-time stock data for a specific ticker symbol
    Also updates the ticker data in all tables (stocks, portfolio_files, portfolio_summaries)
    Returns the updated ticker data from all sources.
    """
    from datetime import timezone
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401
        ticker = ticker.upper()
        # Get real-time data
        result = Get_Ticker.get_stock_quote(ticker, ALPHA_VANTAGE_API_KEY)
        if 'error' in result:
            return jsonify(result), 404
        utcnow = datetime.now(timezone.utc)
        # Fetch the stock row for this user and ticker
        stock_row = db.session.execute(
            db.text("SELECT * FROM stocks WHERE user_id = :user_id AND ticker = :ticker"),
            {"user_id": current_user.user_id, "ticker": ticker}
        ).fetchone()
        updated_stock = None
        if stock_row:
            col_names = stock_row.keys() if hasattr(stock_row, 'keys') else []
            idx = lambda name, default: col_names.index(name) if name in col_names else default
            idx_quantity = idx('quantity', 2)
            idx_buy_price = idx('buy_price', 3)
            idx_company_name = idx('company_name', None)
            quantity = float(stock_row[idx_quantity])
            buy_price = float(stock_row[idx_buy_price])
            # Try to get company_name from stocks table if present, else fallback to result
            company_name = None
            if idx_company_name is not None:
                company_name = stock_row[idx_company_name]
            if not company_name:
                company_name = result.get('01. company name', '')
            # Update all fields in stocks table
            db.session.execute(
                db.text("""
                    UPDATE stocks SET
                        current_price = :current_price,
                        value = :value,
                        gain = :gain,
                        change_percent = :change_percent,
                        updated_at = :updated_at
                    WHERE user_id = :user_id AND ticker = :ticker
                """), {
                    "user_id": current_user.user_id,
                    "ticker": ticker,
                    "current_price": float(result.get('05. price', 0)),
                    "value": float(result.get('05. price', 0)) * quantity,
                    "gain": (float(result.get('05. price', 0)) - buy_price) * quantity,
                    "change_percent": float(result.get('10. change percent', '0').replace('%','')) if '10. change percent' in result else 0.0,
                    "updated_at": utcnow
                }
            )
            # Get updated stock row
            updated_stock = db.session.execute(
                db.text("SELECT * FROM stocks WHERE user_id = :user_id AND ticker = :ticker"),
                {"user_id": current_user.user_id, "ticker": ticker}
            ).fetchone()
        # Update portfolio_files JSON for this ticker
        portfolio_file = PortfolioFile.query.filter_by(user_id=current_user.user_id).first()
        updated_investment = None
        if portfolio_file and 'holdings' in portfolio_file.file_content:
            for inv in portfolio_file.file_content['holdings']:
                if inv.get('ticker', '').upper() == ticker:
                    inv['current_price'] = float(result.get('05. price', 0))
                    inv['value'] = float(result.get('05. price', 0)) * float(inv.get('quantity', 0))
                    inv['gain'] = (float(result.get('05. price', 0)) - float(inv.get('buy_price', 0))) * float(inv.get('quantity', 0))
                    inv['change_percent'] = float(result.get('10. change percent', '0').replace('%','')) if '10. change percent' in result else 0.0
                    inv['company_name'] = result.get('01. company name', inv.get('company_name', ''))
                    inv['updated_at'] = utcnow.isoformat()
                    updated_investment = inv
            portfolio_file.updated_at = utcnow
        # Commit changes to DB
        db.session.commit()
        # Update portfolio_summaries
        analytics_data = portfolio_summaries(ALPHA_VANTAGE_API_KEY, portfolio_file.file_content)
        save_portfolio_summary_to_db(current_user.user_id, analytics_data)
        # Get updated summary for this ticker
        summary_row = PortfolioSummary.query.filter_by(user_id=current_user.user_id).first()
        summary_data = None
        if summary_row:
            summary_data = {
                'total_stocks': summary_row.total_stocks,
                'total_value': float(summary_row.total_value),
                'total_investment': float(summary_row.total_investment),
                'total_gain_loss': float(summary_row.total_gain_loss),
                'total_gain_loss_percent': float(summary_row.total_gain_loss_percent),
                'avg_position_size': float(summary_row.avg_position_size),
                'updated_at': summary_row.updated_at.isoformat() if summary_row.updated_at else None
            }
        return jsonify({
            "message": "Stock data retrieved and updated successfully",
            "ticker": ticker,
            "real_time_data": result,
            "stocks_table": dict(updated_stock._mapping) if updated_stock else None,
            "portfolio_file_investment": updated_investment,
            "portfolio_summary": summary_data
        }), 200
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"message": f"Error occurred: {str(e)}"}), 500

@app.get('/api/stocks/market') # WORKS
def portfolio_market():
    """
    Market trends and updates using Alpha Vantage API key from environment/config.
    Returns the data as JSON on GET request.
    Handles string result from Get_Market_Trends gracefully and avoids backend error prints.
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({'error': 'Unauthorized'}), 401
        api_key = ALPHA_VANTAGE_API_KEY
        try:
            result = Get_Market_Trends.get_top_gainers(api_key)
            if isinstance(result, str):
                return jsonify({'error': result}), 500
            # result is a list of dicts (top 10 gainers)
            return jsonify({'top_gainers': result}), 200
        except Exception as e:
            print(e)
            return jsonify({'error': 'Failed to fetch market data'}), 500
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500 

@app.get('/api/portfolio/analytics') # WORKS
def portfolio_analytics():
    """
    User portfolio profit/loss data and growth trends with comprehensive analytics
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401  
        
        # Get user's portfolio data from database
        portfolio_data = get_user_portfolio_data(current_user.user_id)
        if not portfolio_data:
            return jsonify({"message": "Portfolio data not found"}), 404
        
        # Calculate portfolio analytics
        try:
            analytics_data = portfolio_summaries(ALPHA_VANTAGE_API_KEY, portfolio_data)
            
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

@app.get('/api/portfolio/analytics/history') # WORKS
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

@app.route('/')
def home():
    return 'Hello, To use the API, please visit /api/portfolio/signup to register or /api/portfolio/signin to login.'

@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics for monitoring
    This endpoint provides CPU and memory usage metrics for the Flask application.
    It uses the psutil library to gather system metrics and the prometheus_client library to format
    them for Prometheus scraping.
    The metrics include:
    - CPU usage percentage
    - Memory usage in bytes
    The metrics are exposed at the /metrics endpoint, which can be scraped by Prometheus.
    The metrics are updated in real-time and can be used to monitor the performance of the Flask application.
    The metrics are in the Prometheus text format and can be scraped by Prometheus servers.
    The metrics are updated every time the /metrics endpoint is accessed.
    """
    process = psutil.Process(os.getpid())
    cpu_percent = psutil.cpu_percent(interval=None)
    mem_info = process.memory_info().rss

    CPU_USAGE.set(cpu_percent)
    MEMORY_USAGE.set(mem_info)

    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    with app.app_context():
        print("DB-URI actually used:", app.config['SQLALCHEMY_DATABASE_URI'], flush=True)
        db.create_all()
    app.run(host='0.0.0.0', port=5050, debug=True) # Debug mode - Remove before production