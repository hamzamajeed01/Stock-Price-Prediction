from flask import Flask, render_template, request, redirect, url_for, flash,jsonify
from app.database import add_user, authenticate_user, create_db
import requests
from datetime import datetime, timedelta
app = Flask(__name__)
import secrets
app.secret_key = secrets.token_hex(16)
create_db()
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    if authenticate_user(email, password):
        return redirect(url_for("home"))
    else:
        flash("Invalid email or password. Please try again.")
        return redirect(url_for("index"))

@app.route("/signup", methods=["POST"])
def signup():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    if password != confirm_password:
        flash("Passwords do not match.")
        return redirect(url_for("index"))
    if add_user(first_name, last_name, email, password):
        return redirect(url_for("home"))
    else:
        flash("A user with this email already exists.Please login instead.")
        return redirect(url_for("index"))

@app.route("/home")
def home():
    return render_template("home.html")  

API_KEY = "r_MlFnWgHnQaxrc0v2v9RC6K20cYx69D"
BASE_URL = "https://api.polygon.io/v2/aggs/ticker/{stocksTicker}/range/{multiplier}/{timespan}/{start}/{to}"

# Function to fetch stock data from the Polygon API
def fetch_stock_data(ticker, multiplier=1, timespan="day", start_date=None, end_date=None):
    if not start_date:
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    url = BASE_URL.format(
        stocksTicker=ticker,
        multiplier=multiplier,
        timespan=timespan,
        start=start_date,
        to=end_date
    )
    params = {
        "adjusted": "true",
        "sort": "desc",
        "apiKey": API_KEY
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "results" in data:
            results = data["results"]
            stock_data = [
                {
                    "timestamp": datetime.utcfromtimestamp(item["t"] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                    "open": item["o"],
                    "high": item["h"],
                    "low": item["l"],
                    "close": item["c"],
                    "volume": item["v"]
                }
                for item in results
            ]
            return {"stock_data": stock_data, "meta": {"3. Last Refreshed": start_date}}
        else:
            return {"error": f"No results found for {ticker}"}
    else:
        return {"error": f"Failed to fetch data for {ticker}. Status code: {response.status_code}"}


# Flask route to fetch stock data
@app.route("/get_stock_data", methods=["GET"])
def get_stock_data():
    stocks = ["IBM", "GOOGL", "MSFT"]
    data = {}
    for stock in stocks:
        stock_data = fetch_stock_data(stock)
        data[stock] = stock_data
    print(data)
    return jsonify(data)



@app.route('/predict_close', methods=['GET', 'POST'])
def predict_close():
    if request.method == 'POST':
        try:
            inputs = [
                float(request.form.get('Open')),
                float(request.form.get('High')),
                float(request.form.get('Low')),
                float(request.form.get('Volume'))
            ]

            close_prediction = 23.45
            return str(round(close_prediction, 2)) if close_prediction is not None else "Error: Stock model not loaded."
        except Exception as e:
            return f"An error occurred: {e}"
    # If it's a GET request, render the stock.html page
    return render_template('stock.html')