const STOCKS = {
    'AAPL': 'Apple Inc.',
    'GOOGL': 'Alphabet Inc.',
    'MSFT': 'Microsoft Corporation',
    'AMZN': 'Amazon.com Inc.'
};

const stockTicker = document.getElementById('stockTicker');
const predictionForm = document.getElementById('predictionForm');
const predictionResult = document.getElementById('predictionResult');
let previousPrices = {};
function fetchStockData() {
    fetch('/get_stock_data')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                stockTicker.innerHTML = `
                    <div class="error-message">
                        ${data.error}
                    </div>
                `;
            } else {
                updateTicker(data);
            }
        })
        .catch(error => {
            console.error('Error fetching stock data:', error);
            stockTicker.innerHTML = `
                <div class="error-message">
                    Failed to fetch stock data. Please try again later.
                </div>
            `;
        });
}

function updateTicker(data) {
    stockTicker.innerHTML = ''; 
    
    Object.entries(data).forEach(([symbol, stockData]) => {
        if (!stockData.error) {
            const currentPrice = parseFloat(stockData.stock_data[0].close);
            const prevPrice = previousPrices[symbol] || currentPrice;
            const priceMovement = currentPrice > prevPrice ? 'up' : currentPrice < prevPrice ? 'down' : 'none';
            const tickerItem = document.createElement('div');
            tickerItem.className = 'ticker-item';
            tickerItem.innerHTML = `
                <span class="ticker-symbol">${symbol}</span>
                <span class="ticker-price ${priceMovement === 'up' ? 'price-up' : priceMovement === 'down' ? 'price-down' : ''}">
                    $${currentPrice.toFixed(2)}
                    ${priceMovement === 'up' ? '▲' : priceMovement === 'down' ? '▼' : ''}
                </span>
            `;
            
            stockTicker.appendChild(tickerItem);
            previousPrices[symbol] = currentPrice;
        }
    });
    const tickerItems = stockTicker.innerHTML;
    stockTicker.innerHTML = tickerItems + tickerItems;
}

predictionForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(predictionForm);
    predictionResult.className = 'prediction-result';
    predictionResult.textContent = 'Calculating prediction...';
    predictionResult.style.display = 'block';

    fetch('/predict_close', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(result => {
        predictionResult.className = 'prediction-result success';
        predictionResult.textContent = `Predicted Stock Price: $${parseFloat(result).toFixed(2)}`;
    })
    .catch(error => {
        predictionResult.className = 'prediction-result error';
        predictionResult.textContent = 'Error calculating prediction. Please try again.';
        console.error('Prediction error:', error);
    });
});

fetchStockData();
setInterval(fetchStockData, 15000); // Refresh every 15 seconds

function restartAnimation() {
    const ticker = document.getElementById('stockTicker');
    ticker.style.animation = 'none';
    ticker.offsetHeight; 
    ticker.style.animation = null;
    // console.log('Restarting animation');
}
stockTicker.addEventListener('animationend', restartAnimation);
