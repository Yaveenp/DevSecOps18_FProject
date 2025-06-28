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

# ADDED: Secret key for session management
app.secret_key = 'your-secret-key-change-in-production'

# ADDED: Alpha Vantage API Key - Set this in environment variables
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

# Fixed Portfolio Files model
class PortfolioFile(db.Model):
    __tablename__ = 'portfolio_files'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    filename = db.Column(db.Text, nullable=False)
    filepath = db.Column(db.Text, nullable=False)
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
    User portfolio profit/loss data and growth trends
    # CHANGED: Simplified docstring
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401  
        
        # TODO: Implement actual analytics logic
        return jsonify({"message": "User portfolio profit/loss data and growth trends"}), 200
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500 

#Logout endpoint for session management
@app.post('/api/portfolio/logout')
def logout():
    """
    Logout current user
    """
    try:
        session.clear()
        return jsonify({"message": "Successfully logged out"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred during logout"}), 500

# Debug endpoint - Remove before production
@app.get('/api/portfolio/users')
def list_users():
    try:
        users = User.query.all()
        return jsonify([{
            "user_id": u.user_id,
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "portfolio_files_count": len(u.portfolio_files)
        } for u in users]), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Failed to fetch users"}), 500

# Debug endpoint for portfolio files - Remove before production
@app.get('/api/portfolio/files')
def list_portfolio_files():
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401
            
        files = PortfolioFile.query.filter_by(user_id=current_user.user_id).all()
        return jsonify([{
            "id": f.id,
            "filename": f.filename,
            "filepath": f.filepath,
            "created_at": f.created_at.isoformat() if f.created_at else None,
            "updated_at": f.updated_at.isoformat() if f.updated_at else None
        } for f in files]), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Failed to fetch portfolio files"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5050, debug=True) # Debug mode - Remove before production