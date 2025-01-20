from datetime import datetime, timedelta
import finnhub
import requests
from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   url_for)

from app.database import add_user, authenticate_user, create_db

from .util import predict_stock_price
from dotenv import load_dotenv
import os

load_dotenv()
finnhub_client = finnhub.Client(api_key=os.getenv("FINNHUB_API_KEY"))
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

def fetch_stock_data(ticker):
    try:
        quote = finnhub_client.quote(ticker)
        current_price = quote['c']
        percent_change = quote['dp']
        return {
            "current_price": current_price,
            "percent_change": percent_change
        }
    except Exception as e:
        return {"error": f"Failed to fetch data for {ticker}: {str(e)}"}

@app.route("/get_stock_data", methods=["GET"])
def get_stock_data():
    stocks = ["GOOGL", "MSFT", "AMZN", "AAPL"]
    data = {}

    for stock in stocks:
        stock_data = fetch_stock_data(stock)
        data[stock] = stock_data

    if any("error" in stock_data for stock_data in data.values()):
        return jsonify({"error": "An error occurred while fetching stock data."}), 500

    return jsonify(data)

@app.route("/predict_close", methods=["GET", "POST"])
def predict_close():
    if request.method == "POST":
        try:
            stock_symbol = request.form.get("stock")
            open_price = request.form.get("Open")
            high_price = request.form.get("High")
            low_price = request.form.get("Low")
            volume = request.form.get("Volume")
            print("Apple", open_price, high_price, low_price, volume)
            if stock_symbol == "AAPL":
                result = predict_stock_price(
                    "Apple", open_price, high_price, low_price, volume
                )
            elif stock_symbol == "GOOGL":
                result = predict_stock_price(
                    "Google", open_price, high_price, low_price, volume
                )
            elif stock_symbol == "AMZN":
                result = predict_stock_price(
                    "Amazone", open_price, high_price, low_price, volume
                )
            elif stock_symbol == "MSFT":
                result = predict_stock_price(
                    "Microsoft", open_price, high_price, low_price, volume
                )
            else:
                result = predict_stock_price(
                    "general", open_price, high_price, low_price, volume
                )
            return (
                str(round(result, 2))
                if result is not None
                else "Error: Stock model not loaded."
            )
        except Exception as e:
            return f"An error occurred: {e}"
