import os

import joblib
import numpy as np
import pandas as pd

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
