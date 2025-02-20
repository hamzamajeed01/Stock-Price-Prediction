import os
import secrets
from datetime import datetime, timedelta
from functools import wraps

import finnhub
import requests
from dotenv import load_dotenv
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)

from app.database import add_user, authenticate_user, create_db, get_user_by_id

from .util import predict_stock_price

load_dotenv()
finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.permanent_session_lifetime = timedelta(hours=24)
create_db()


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
        quote = finnhub_client.quote(ticker)
        current_price = quote["c"]
        percent_change = quote["dp"]
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
