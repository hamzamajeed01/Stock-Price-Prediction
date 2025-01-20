# Stock Price Prediction 🏦📈

This application leverages advanced AI models to predict stock prices based on key input parameters such as opening price, highest price, lowest price, and trading volume. By analyzing historical stock data, it provides actionable insights into potential stock price trends, aiding in informed decision-making.

The project uses financial data from **Yahoo Finance (yfinance)** for major companies like **Google, Amazon, Apple, and Microsoft**. Individual models were trained for each company, along with a **general model** trained on combined data for enhanced flexibility.

## 📋 Features

- **AI-Powered Predictions**: Uses cutting-edge machine learning models to deliver accurate stock price forecasts.
- **Multiple Company Models**: Individual models trained for Google, Amazon, Apple, and Microsoft, as well as a general model for other scenarios.
- **User-Friendly Interface**: Simplified input for key parameters (Opening Price, Highest Price, Lowest Price, and Trading Volume).
- **Flexible Deployment**: Easily scales to include additional companies or data sources.
- **Robust Input Validation**: Ensures input parameters are meaningful, reducing the risk of errors.
- **Integrated Data Source**: Historical data seamlessly fetched using `yfinance`.

## 🛠️ Technologies Used

- **Python**: Core language for backend processing and AI model execution.
- **Machine Learning**: Models trained using:
  - Libraries: `scikit-learn`, `XGBoost`, or similar.
  - Algorithms: Regression models fine-tuned for stock price prediction.
- **Flask**: Provides a lightweight and efficient framework for hosting the web interface.
- **Frontend**: Simple and intuitive forms built using:
  - HTML5 for structure.
  - CSS for styling.
  - JavaScript for interactive validations.

## 🚀 How It Works

1. **Input Parameters**: Users provide stock-specific details:
   - **Opening Price**: The stock's opening price on the trading day.
   - **Highest Price**: The highest price the stock reached.
   - **Lowest Price**: The lowest price the stock reached.
   - **Trading Volume**: The number of shares traded during the day.
2. **AI Models**:
   - Loads a pre-trained model for the selected company or the general model.
   - Scales input data using trained scalers for normalization.
3. **Prediction**:
   - Processes input data through the AI model.
   - Outputs the **predicted closing price** or trends.

## 🧪 Example Input/Output

### Input:

- **Opening Price**: $100
- **Highest Price**: $105
- **Lowest Price**: $98
- **Trading Volume**: 1,000,000

### Output:

- **Predicted Closing Price**: $102.5

### Example Workflow:

1. Enter stock parameters in the input form.
2. Select the company (Google, Amazon, Apple, Microsoft, or General).
3. Click "Predict."
4. View the predicted stock price on the result page.

## 📊 Data Source

Historical stock data was downloaded using [yfinance](https://pypi.org/project/yfinance/) for:

- **Google**
- **Amazon**
- **Apple**
- **Microsoft**

The data was preprocessed, cleaned, and used to train individual and general models.

TO run the application create a .env file and do
FINNHUB_API_KEY=your api key for finhub
