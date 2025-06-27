from flask import Flask, jsonify, request, session
from flask_cors import CORS
from datetime import datetime, timedelta
import psycopg2
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

# ADDED: Secret key for session management
app.secret_key = 'your-secret-key-change-in-production'

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
                db.session.commit()
                self.user_id = new_user.user_id
                return f'User {self.username} was successfully registered. Please login'
        except Exception as e:
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
    List of investments
    # CHANGED: Simplified docstring
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401
        
        # TODO: Implement actual portfolio retrieval logic
        return jsonify({"message": "portfolio", "user": current_user.username}), 200
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500

@app.post('/api/portfolio')
def portfolio_add():
    """
    Add a new investment
    # CHANGED: Simplified docstring
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401 
        
        # TODO: Implement actual investment addition logic
        return jsonify({"message": "Add a new investment"}), 200
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500

@app.put('/api/portfolio/<investment_id>')
def portfolio_update(investment_id):
    """
    Update an investment
    # CHANGED: Simplified docstring
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401
        
        # TODO: Implement actual investment update logic
        return jsonify({"message": "Update an investment"}), 200
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500

@app.delete('/api/portfolio/<investment_id>')
def portfolio_remove(investment_id):
    """
    Delete an investment
    # CHANGED: Simplified docstring
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401
        
        # TODO: Implement actual investment deletion logic
        return jsonify({"message": "Delete an investment"}), 200
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500 

@app.get('/api/stocks/<ticker>')
def portfolio_real(ticker):
    """
    Real-time stock data for a specific ticker symbol
    # CHANGED: Simplified docstring
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401
        
        # TODO: Implement actual stock data retrieval logic
        return jsonify({"message": "Ticker real time data", "ticker": ticker}), 200
        
    except Exception as e:
        print(e)
        return jsonify({"message": "Error occurred"}), 500

@app.get('/api/stocks/market')
def portfolio_market():
    """
    Market trends and updates
    # CHANGED: Simplified docstring
    """
    try:
        current_user = get_current_user()
        if not current_user:
            return jsonify({"message": "Please login and try again"}), 401 
        
        # TODO: Implement actual market data retrieval logic
        return jsonify({"message": "Market trends and updates"}), 200
        
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
            "last_name": u.last_name
        } for u in users]), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "Failed to fetch users"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5050, debug=True) # Debug mode - Remove before production