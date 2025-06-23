from flask import Flask,jsonify, request
from flask_cors import CORS
import datetime

app = Flask(__name__) # flask application
CORS(app)

# temporary users until database will be connected
portfolio_user = [{"user_id": "1000", "username": "chenh", "password": "1234", "first_name": "chen", "last_name": "h"},
                  {"user_id": "1001", "username": "alexb", "password": "9876", "first_name": "alex", "last_name": "bor"},
                  {"user_id": "1002", "username": "timi", "password": "timitim", "first_name": "timi", "last_name": "tim"}
                  ]


class PortfolioUser:  # This class is the portfolio user login and creation and its protected access
    num = 1003  # temporary id until database will return the user id

    def __init__(self, username: str, password: str, first_name: str, last_name: str):
        """
        builder function to see if the user is already in database and if not create him
        :param username: string - the username for the app user
        :param password: string - the username password for the app
        :param first_name: string - The user first name
        :param last_name: string - The user last name
        """
        self.username = username.lower()
        self.password = password.lower()
        self.first_name = first_name.lower()
        self.last_name = last_name.lower()
        self.expiration = None
        self.is_expired = False
        self.user_id = 0

    def user_create(self, username: str, password: str, first_name: str, last_name: str, user_id=num):
        """
        Checks if user is already in database and if not send it to be created
        :param username: string - the username for the app user
        :param password: string - the username password for the app
        :param first_name: string - The user first name
        :param last_name: string - The user last name
        :return: if username exists return an error if not returns a username was registered
        """
        # temporary check until database will be created
        for user in portfolio_user:
            if username == user["username"]:
                return "Username already exist"
        else:
            PortfolioUser(username, password, first_name, last_name)
            # temporary id until database will return the user id
            self.user_id = user_id
            global num
            num = user_id + 1
            # temporary append until database will be connected
            portfolio_user.append({"user_id": f"{self.user_id}", "username": f"{self.username}",
                                   "password": f"{self.password}", "first_name": f"{self.first_name}",
                                   "last_name": f"{self.last_name}"})
            print(portfolio_user)
            return f'User {self.username} was successfully registered. Please login'

    def user_login(self, username: str, password: str):
        """
        Checks user cardinals in database and add session timeout stamp
        :param username: string - the username that the user entered to log in
        :param password: string - the password that the user entered to log in
        :return: session time stamp on successful login message or an error message for invalided credentials
        """
        for user in portfolio_user:
            if username == user["username"]:
                if password == user["password"]:
                    self.expiration = datetime.datetime.now() + datetime.timedelta(minutes=15)
                    self.is_expired = False
                    return jsonify({"message": "successful login"})
                else:
                    return jsonify({"message": "Username or password are wrong or user dont exists"})
            else:
                continue
        return jsonify({"message": "Username or password are wrong or user dont exists"})

    def session_expired(self):
        """
        Checks if user login session is still valid
        :return: Session expired message if session passed 15 minutes or itself if not expired
        """
        if self.expiration < datetime.datetime.now():
            self.is_expired = True
            return jsonify({"message": "Session has expired. Please login again"})
        else:
            return self


@app.get('/api/portfolio/health')  # get the health status of the flask
def health():
    try:
        return jsonify({'status': 'healthy'}), 200
    except Exception as e:
        print(e)
        return jsonify({"status": "not healthy"}), 200


@app.post('/api/portfolio/signup')  # sign up to application endpoint
def signup():
    try:
        try:
            request_data = request.get_json()
            print(request_data)
            username = str(request_data["username"])
            password = str(request_data["password"])
            first_name = str(request_data["first_name"])
            last_name = str(request_data["last_name"])
            if (username.isascii() and password.isascii() and first_name.isascii() and last_name.isascii()
                    and username.__len__() >= 3 and password.__len__() >= 3):
                user = PortfolioUser(username, password, first_name, last_name)
                result = user.user_create(username, password, first_name, last_name)
                print(result)
                if "already exist" in result:
                    return jsonify({"message": "Username already exist, please try again."}), 403
                else:
                    return jsonify({"message": "Successfully registered. Please login."}), 200
            else:
                return jsonify({"message": "permeates are not entered correctly, please try again."}), 403
        except Exception as e:
            print(e)
            return jsonify({"message": "permeates are not entered correctly, please try again."}), 403
    except Exception as e:
        print(e)
        return jsonify({"message": "error was received"}), 403


@app.post('/api/portfolio/signin')  # sign in to application endpoint
def signin():
    try:
        try:
            request_data = request.get_json()
            username = str(request_data["username"])
            password = str(request_data["password"])
            if username.isascii() and password.isascii() and username.__len__() >= 3 and password.__len__() >= 3:
                global user
                user = PortfolioUser(username, password, "", "")
                result = user.user_login(username, password)
                return result, 200
            else:
                return jsonify({"message": "permeates are not entered correctly, please try again."}), 403
        except Exception as e:
            print(e)
            return jsonify({"message": "permeates are not entered correctly, please try again."}), 403
    except Exception as e:
        print(e)
        return jsonify({"message": "error was received"}), 403


@app.get('/api/portfolio')  # Get the current portfolio (list of investments)
def portfolio_list():
    """
    list of investments
    :return: JSON of a list of investments for the user with all details
    """
    try:
        if PortfolioUser.session_expired(user) == "Session has expired. Please login again":
            return jsonify({"message": "Session has expired. Please login again."}), 403
        else:
            # Will return the username portfolio
            return jsonify({"message": "portfolio"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "error was received"}), 403


@app.post('/api/portfolio')  # Add a new investment
def portfolio_add():
    """
    Add a new investment of a user using JSON payload with ticker, quantity, buy_price, etc.
    JSON PAYLOAD:
    ticker
    quantity
    buy_price
    :return: message of successful add of investment or the reason of failure
    """
    try:
        if PortfolioUser.session_expired(user) == "Session has expired. Please login again":
            return jsonify({"message": "Session has expired. Please login again."}), 403
        else:
            # Will start the add new investment process
            return jsonify({"message": "Add a new investment"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "error was received"}), 403


@app.put('/api/portfolio/<investment_id>')  # Update an investment (e.g., edit quantity or buy price)
def portfolio_update():
    """
    update an investment of a user using JSON payload with investment_id, ticker, quantity, buy_price, etc.
    JSON PAYLOAD:
    investment_id
    ticker
    quantity
    buy_price
    :return: message of successful update of investment or the reason of failure
    """
    try:
        if PortfolioUser.session_expired(user) == "Session has expired. Please login again":
            return jsonify({"message": "Session has expired. Please login again."}), 403
        else:
            # Will start the update investment process
            return jsonify({"message": "Update an investment"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "error was received"}), 403


@app.delete('/api/portfolio/<investment_id>')  # Remove an investment
def portfolio_remove():
    """
    Delete an investment of a user using JSON payload with investment_id
    JSON PAYLOAD:
    investment_id
    :return: message of successful delete of investment or the reason of failure
    """
    try:
        if PortfolioUser.session_expired(user) == "Session has expired. Please login again":
            return jsonify({"message": "Session has expired. Please login again."}), 403
        else:
            # Will start the remove an investment process
            return jsonify({"message": "Delete an investment"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "error was received"}), 403


@app.get('/api/stocks/<ticker>')  # Get real-time stock data for a specific ticker symbol
def portfolio_real():
    """
    real-time stock data for a specific ticker symbol
    :return: JSON of all details and data for a specific ticker symbol
    """
    try:
        if PortfolioUser.session_expired(user) == "Session has expired. Please login again":
            return jsonify({"message": "Session has expired. Please login again."}), 403
        else:
            # Will start the remove an investment process
            return jsonify({"message": "Ticker real time data"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "error was received"}), 403


@app.get('/api/stocks/market')  # Get market trends and updates (optional external API integration)
def portfolio_market():
    """
    Market trends and updates
    :return: JSON of trends and JSON for updates
    """
    try:
        if PortfolioUser.session_expired(user) == "Session has expired. Please login again":
            return jsonify({"message": "Session has expired. Please login again."}), 403
        else:
            # Will start the remove an investment process
            return jsonify({"message": "Market trends and updates"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "error was received"}), 403


@app.get('/api/portfolio/analytics')  # Fetch profit/loss data and growth trends for the portfolio
def portfolio_analytics():
    """
    User portfolio profit/loss data and growth trends
    :return: JSON with all analytics data
    """
    try:
        if PortfolioUser.session_expired(user) == "Session has expired. Please login again":
            return jsonify({"message": "Session has expired. Please login again."}), 403
        else:
            # Will start the remove an investment process
            return jsonify({"message": "User portfolio profit/loss data and growth trends"}), 200
    except Exception as e:
        print(e)
        return jsonify({"message": "error was received"}), 403

if __name__ == '__main__':
    app.run(port=5050, debug=True)  # to open to all IP's add host='0.0.0.0', need to remove debug before production
