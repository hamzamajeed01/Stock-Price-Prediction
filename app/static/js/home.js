const STOCKS = {
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
};

const stockTicker = document.getElementById('stockTicker');
const predictionForm = document.getElementById('predictionForm');
const predictionResult = document.getElementById('predictionResult');
let previousPrices = {};
let tickerInitialized = false;
let animationDuration = 0;
let dataFetchInterval = null;

function updateTickerData(data) {
    const tickerItems = document.querySelectorAll('.ticker-item');
    
    if (!tickerItems.length) {
        // If ticker items don't exist (possibly due to previous error), reinitialize
        initializeTicker(data);
        return;
    }

    tickerItems.forEach(item => {
        const symbol = item.querySelector('.ticker-symbol').textContent;
        const stockData = data[symbol];
        
        if (stockData && !stockData.error) {
            const currentPrice = stockData.current_price;
            const percentChange = stockData.percent_change;
            const prevPrice = previousPrices[symbol] || currentPrice;
            const priceMovement = currentPrice > prevPrice ? 'up' : currentPrice < prevPrice ? 'down' : 'none';

            const priceElement = item.querySelector('.ticker-price');
            const percentElement = item.querySelector('.percent-change');

            priceElement.textContent = `$${currentPrice.toFixed(2)}`;
            priceElement.className = `ticker-price ${priceMovement === 'up' ? 'price-up' : priceMovement === 'down' ? 'price-down' : ''}`;
            
            percentElement.textContent = `${percentChange >= 0 ? '▲' : '▼'} ${Math.abs(percentChange).toFixed(2)}%`;
            percentElement.className = `percent-change ${percentChange >= 0 ? 'price-up' : 'price-down'}`;

            previousPrices[symbol] = currentPrice;
        }
    });
}

function initializeTicker(data) {
    const tempContainer = document.createElement('div');
    tempContainer.className = 'ticker-content';

    Object.entries(data).forEach(([symbol, stockData]) => {
        if (!stockData.error) {
            const currentPrice = stockData.current_price;
            const percentChange = stockData.percent_change;

            const tickerItem = document.createElement('div');
            tickerItem.className = 'ticker-item';
            tickerItem.innerHTML = `
                <div class="company-info">
                    <span class="ticker-symbol">${symbol}</span>
                    <span class="company-name">${STOCKS[symbol] || symbol}</span>
                </div>
                <div class="price-info">
                    <span class="ticker-price">
                        $${currentPrice.toFixed(2)}
                    </span>
                    <span class="percent-change ${percentChange >= 0 ? 'price-up' : 'price-down'}">
                        ${percentChange >= 0 ? '▲' : '▼'} ${Math.abs(percentChange).toFixed(2)}%
                    </span>
                </div>
            `;

            tempContainer.appendChild(tickerItem);
            previousPrices[symbol] = currentPrice;
        }
    });

    // Clone the ticker items to create a seamless loop
    const clone = tempContainer.cloneNode(true);
    
    stockTicker.innerHTML = '';
    const wrapper = document.createElement('div');
    wrapper.className = 'ticker-wrap';
    
    const ticker = document.createElement('div');
    ticker.className = 'ticker';
    
    ticker.appendChild(tempContainer);
    ticker.appendChild(clone);
    
    wrapper.appendChild(ticker);
    stockTicker.appendChild(wrapper);

    // Calculate animation duration based on content width
    const contentWidth = tempContainer.offsetWidth;
    animationDuration = contentWidth / 50; // Increased speed (changed from 25 to 50)
    ticker.style.animationDuration = `${animationDuration}s`;

    // Reset and start new data fetch interval
    if (dataFetchInterval) {
        clearInterval(dataFetchInterval);
    }
    // Set interval to fetch new data at 75% of animation duration
    const fetchInterval = Math.max(animationDuration * 750, 10000); // minimum 10 seconds
    dataFetchInterval = setInterval(fetchStockData, fetchInterval);
}

function fetchStockData() {
    fetch('/get_stock_data')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            if (!tickerInitialized) {
                initializeTicker(data);
                tickerInitialized = true;
            } else {
                updateTickerData(data);
            }
        })
        .catch(error => {
            console.error('Error fetching stock data:', error);
            // Don't clear existing ticker on error if it's already initialized
            if (!tickerInitialized) {
                stockTicker.innerHTML = `
                    <div class="error-message">
                        Failed to fetch stock data. Retrying...
                    </div>
                `;
            }
            // Retry after 5 seconds on error
            setTimeout(fetchStockData, 5000);
        });
}

// Initial load
fetchStockData();

predictionForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Get the stock symbol from the dropdown
    const stockSymbol = document.getElementById('stock').value; // Assuming the dropdown has ID 'stock'

    // Create FormData object and append the selected stock symbol
    const formData = new FormData(predictionForm);
    formData.append('stock', stockSymbol); // Append the selected stock symbol to the form data

    // Show loading message
    predictionResult.className = 'prediction-result';
    predictionResult.textContent = 'Calculating prediction...';
    predictionResult.style.display = 'block';

    // Send the request to the backend
    fetch('/predict_close', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text()) // Parse the response
    .then(result => {
        // Display the prediction result
        predictionResult.className = 'prediction-result success';
        predictionResult.textContent = `Predicted Stock Price for ${stockSymbol}: $${parseFloat(result).toFixed(2)}`;
    })
    .catch(error => {
        // Display error message if the prediction fails
        predictionResult.className = 'prediction-result error';
        predictionResult.textContent = 'Error calculating prediction. Please try again.';
        console.error('Prediction error:', error);
    });
});


