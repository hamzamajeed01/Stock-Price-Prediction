import os
import secrets
from datetime import datetime, timedelta
from functools import wraps
import threading
import time

import finnhub
import requests
from dotenv import load_dotenv
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)

from app.database import add_user, authenticate_user, create_db, get_user_by_id, save_stock_alert, get_user_alerts, delete_stock_alert, get_alerts_by_frequency, update_last_alert_time

from .util import predict_stock_price, send_stock_alert_email

load_dotenv()
finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.permanent_session_lifetime = timedelta(hours=24)
create_db()

# Define available stocks
STOCKS = {
    'AAPL': 'Apple Inc.',
    'GOOGL': 'Alphabet Inc.',
    'MSFT': 'Microsoft Corporation',
    'AMZN': 'Amazon.com Inc.',
    'TSLA': 'Tesla Inc.',
    'NFLX': 'Netflix Inc.',
    'NVDA': 'NVIDIA Corporation',
    'META': 'Meta Platforms Inc.',
    'BTC': 'Bitcoin',
    'ETH': 'Ethereum',
    'DOGE': 'Dogecoin',
    'BNB': 'Binance Coin',
    'XRP': 'Ripple'
}

# Add available frequencies for alerts
ALERT_FREQUENCIES = {
    'every_minute': '1 minute',
    'every_5_minutes': '5 minutes',
    'every_30_minutes': '30 minutes',
    'hourly': '1 hour',
    'daily': '24 hours',
    'weekly': '7 days'
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login to access this page.")
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("home"))
    return render_template("index.html")


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    user = authenticate_user(email, password)
    if user:
        session.permanent = True
        session["user_id"] = user[0]  # Store user ID in session
        session["email"] = user[3]  # Store email in session
        session["name"] = user[1]  # Store first name in session
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

    user = add_user(first_name, last_name, email, password)
    if user:
        session.permanent = True
        session["user_id"] = user[0]  # Store user ID in session
        session["email"] = user[3]  # Store email in session
        session["name"] = user[1]  # Store first name in session
        return redirect(url_for("home"))
    else:
        flash("A user with this email already exists. Please login instead.")
        return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.")
    return redirect(url_for("index"))


@app.route("/home")
@login_required
def home():
    return render_template("home.html")


def fetch_stock_data(ticker):
    try:
        # Add prefix for crypto symbols if not already present
        if ticker in ['BTC', 'ETH', 'DOGE', 'BNB', 'XRP']:
            ticker = f"BINANCE:{ticker}USDT"
            
        quote = finnhub_client.quote(ticker)
        
        # Validate the quote data
        if not quote or 'c' not in quote or 'dp' not in quote:
            return {"error": f"Invalid quote data received for {ticker}"}
            
        current_price = quote['c']
        percent_change = quote['dp']
        
        # Validate price data
        if current_price is None or percent_change is None:
            return {"error": f"Missing price data for {ticker}"}
            
        return {"current_price": current_price, "percent_change": percent_change}
    except Exception as e:
        return {"error": f"Failed to fetch data for {ticker}: {str(e)}"}

def get_all_stock_data():
    stocks = ["GOOGL", "MSFT", "AMZN", "AAPL", "TSLA", "NFLX", "NVDA", "META"]
    cryptos = ["BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:DOGEUSDT", "BINANCE:BNBUSDT", "BINANCE:XRPUSDT"]

    all_data = {}

    for stock in stocks + cryptos:
        stock_data = fetch_stock_data(stock)
        all_data[stock] = stock_data

    return all_data

@app.route("/get_stock_data", methods=["GET"])
def get_stock_data():
    data = get_all_stock_data()
    
    if any("error" in stock_data for stock_data in data.values()):
        return jsonify({"error": "An error occurred while fetching stock data."}), 500

    return jsonify(data)





@app.route("/predict_close", methods=["POST"])
def predict_close():
    try:
        stock_symbol = request.form.get("stock")
        open_price = request.form.get("Open")
        high_price = request.form.get("High")
        low_price = request.form.get("Low")
        volume = request.form.get("Volume")

        symbol_map = {
            "AAPL": "Apple", "GOOGL": "Google", "AMZN": "Amazon", "MSFT": "Microsoft",
            "TSLA": "Tesla", "NFLX": "Netflix", "NVDA": "Nvidia", "META": "Meta",
            "BTC": "Bitcoin", "ETH": "Ethereum", "DOGE": "Dogecoin", "BNB": "Binance", "XRP": "Ripple"
        }

        result = predict_stock_price(symbol_map.get(stock_symbol, "general"), open_price, high_price, low_price, volume)

        return str(round(result, 2)) if result is not None else "Error: Stock model not loaded."

    except Exception as e:
        return f"An error occurred: {e}"

@app.route("/alerts")
@login_required
def alerts():
    user_alerts = get_user_alerts(session['user_id'])
    return render_template("alerts.html", 
                         stocks=STOCKS, 
                         frequencies=ALERT_FREQUENCIES,
                         current_alerts=user_alerts)

@app.route("/set_alert", methods=["POST"])
@login_required
def set_alert():
    stock_symbol = request.form.get("stock")
    frequency = request.form.get("frequency")
    
    if not stock_symbol or not frequency:
        flash("Please select both stock and frequency")
        return redirect(url_for("alerts"))
    
    if frequency not in ALERT_FREQUENCIES:
        flash("Invalid frequency selected")
        return redirect(url_for("alerts"))
    
    success = save_stock_alert(session['user_id'], stock_symbol, frequency)
    
    if success:
        flash(f"Alert set successfully for {stock_symbol}")
    else:
        flash("Error setting alert. Please try again.")
    
    return redirect(url_for("alerts"))

@app.route("/delete_alert", methods=["POST"])
@login_required
def delete_alert():
    stock_symbol = request.form.get("stock")
    
    if not stock_symbol:
        flash("Invalid request")
        return redirect(url_for("alerts"))
    
    success = delete_stock_alert(session['user_id'], stock_symbol)
    
    if success:
        flash(f"Alert deleted successfully for {stock_symbol}")
    else:
        flash("Error deleting alert. Please try again.")
    
    return redirect(url_for("alerts"))

def process_alerts(frequency):
    while True:
        try:
            alerts = get_alerts_by_frequency(frequency)
            for alert_id, email, stock_symbol, _, last_alert_time in alerts:
                try:
                    # Get stock data
                    stock_data = fetch_stock_data(stock_symbol)
                    
                    if "error" in stock_data:
                        print(f"Error fetching stock data: {stock_data['error']}")
                        continue
                    
                    current_price = stock_data["current_price"]
                    percent_change = stock_data["percent_change"]
                    
                    # Attempt to send email
                    if send_stock_alert_email(email, stock_symbol, current_price, percent_change):
                        update_last_alert_time(alert_id)
                    else:
                        print(f"Failed to send alert for {stock_symbol} to {email}")
                        
                except Exception as e:
                    print(f"Error processing alert for {stock_symbol}: {e}")
                    continue
                
                # Add a small delay between processing each alert to avoid rate limits
                time.sleep(1)
                
        except Exception as e:
            print(f"Error in alert processor: {e}")
        
        # Sleep based on frequency
        sleep_times = {
            'every_minute': 60,
            'every_5_minutes': 300,
            'every_30_minutes': 1800,
            'hourly': 3600,
            'daily': 86400,
            'weekly': 604800
        }
        time.sleep(sleep_times.get(frequency, 3600))

# Start alert processing threads
def start_alert_processors():
    print("Starting alert processors...")
    for frequency in ALERT_FREQUENCIES:
        thread = threading.Thread(target=process_alerts, args=(frequency,), daemon=True)
        thread.start()
        print(f"Started processor for frequency: {frequency}")

# Start alert processors when the app starts
start_alert_processors()
