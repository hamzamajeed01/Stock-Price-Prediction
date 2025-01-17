
const COMPANIES = {
    IBM: "International Business Machines",
    GOOGL: "Google LLC",
    MSFT: "Microsoft Corporation"
};

function fetchStockData() {
    fetch("/get_stock_data")
        .then((response) => response.json())
        .then((data) => {
            const container = document.getElementById("stocks");
            container.innerHTML = ""; // Clear existing data

            Object.keys(data).forEach((symbol) => {
                const companyData = data[symbol];
                if (companyData.error) {
                    container.innerHTML += `<div class="company-section">
                        <h2>${symbol}</h2>
                        <p>${companyData.error}</p>
                    </div>`;
                    return;
                }

                const stockRows = companyData.stock_data
                    .map(
                        (entry) => `
                    <tr>
                        <td>${entry.timestamp}</td>
                        <td>${entry.open}</td>
                        <td>${entry.high}</td>
                        <td>${entry.low}</td>
                        <td>${entry.close}</td>
                        <td>${entry.volume}</td>
                    </tr>
                `
                    )
                    .join("");

                container.innerHTML += `
                    <div class="company-section">
                        <div class="company-header">
                            <div class="company-name">${symbol} - ${COMPANIES[symbol]}</div>
                            <div class="last-updated">Last Updated: ${companyData.meta["3. Last Refreshed"]}</div>
                        </div>
                        <table class="stock-table">
                            <thead>
                                <tr>
                                    <th>Time</th>
                                    <th>Open</th>
                                    <th>High</th>
                                    <th>Low</th>
                                    <th>Close</th>
                                    <th>Volume</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${stockRows}
                            </tbody>
                        </table>
                    </div>
                `;
            });
        })
        .catch((error) => console.error("Error fetching stock data:", error));
}

// Refresh data every 15 seconds
setInterval(fetchStockData, 15000);

// Fetch data on page load
fetchStockData();
