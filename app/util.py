import os
import time

import joblib
import numpy as np
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import pytz
BASE_DIR = os.getcwd()
MODELS_DIR = os.path.join(BASE_DIR, "Notebooks")


def predict_stock_price(company_name, open_price, high_price, low_price, volume):
    try:
        print(company_name, open_price, high_price, low_price, volume)
        print(MODELS_DIR)
        model_name = os.path.join(MODELS_DIR, f"{company_name}_model.pkl")
        X_scaler_name = os.path.join(MODELS_DIR, f"{company_name}_X_scaler.pkl")
        y_scaler_name = os.path.join(MODELS_DIR, f"{company_name}_Y_scaler.pkl")
        if not os.path.exists(model_name):
            raise FileNotFoundError(f"Model file not found: {model_name}")
        if not os.path.exists(X_scaler_name):
            raise FileNotFoundError(f"X scaler file not found: {X_scaler_name}")
        if not os.path.exists(y_scaler_name):
            raise FileNotFoundError(f"Y scaler file not found: {y_scaler_name}")
        model = joblib.load(model_name)
        X_scaler = joblib.load(X_scaler_name)
        y_scaler = joblib.load(y_scaler_name)

        new_data = pd.DataFrame(
            {
                "Open": [open_price],
                "High": [high_price],
                "Low": [low_price],
                "Volume": [volume],
            }
        )
        new_data_scaled = X_scaler.transform(new_data)
        predictions_scaled = model.predict(new_data_scaled)
        predictions = y_scaler.inverse_transform(predictions_scaled.reshape(-1, 1))
        result = predictions[0][0]
        print(f"Predicted closing price for {company_name}: {result}")
        return result
    except FileNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}

def send_stock_alert_email(recipient_email, stock_symbol, current_price, percent_change):
    server = None
    try:
        # Validate inputs
        if current_price is None or percent_change is None:
            raise ValueError("Price data is missing or invalid")

        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")

        if not all([smtp_username, smtp_password]):
            raise ValueError("SMTP credentials not configured")

        utc_now = datetime.utcnow()  # Get current UTC time
        eastern_tz = pytz.timezone("America/New_York")  # Eastern Time Zone (EST/EDT)
        est_now = utc_now.replace(tzinfo=pytz.utc).astimezone(eastern_tz)
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = recipient_email
        msg['Subject'] = f"Stock Alert: {stock_symbol}"

        body = f"""
        <html>
            <body>
                <h2>Stock Price Alert for {stock_symbol}</h2>
                <p>Current Price: ${current_price:.2f}</p>
                <p>24h Change: {percent_change:+.2f}%</p>
                <p>Time: {est_now.strftime('%Y-%m-%d %H:%M:%S')} EST</p>
                <p>This is an automated alert from your Stock Price Predictor.</p>
            </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        # Create SMTP connection with timeout
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=30)
        server.starttls()
        
        # Try to login multiple times in case of temporary connection issues
        max_retries = 3
        retry_delay = 5  # seconds
        
        for attempt in range(max_retries):
            try:
                server.login(smtp_username, smtp_password)
                break
            except smtplib.SMTPException as e:
                if attempt == max_retries - 1:  # Last attempt
                    raise
                print(f"SMTP login attempt {attempt + 1} failed: {e}")
                time.sleep(retry_delay)

        server.send_message(msg)
        return True

    except (ValueError, smtplib.SMTPException) as e:
        print(f"Error sending email alert: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error sending email alert: {e}")
        return False
    finally:
        if server:
            try:
                server.quit()
            except Exception as e:
                print(f"Error closing SMTP connection: {e}")

