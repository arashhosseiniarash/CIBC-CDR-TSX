import sqlite3
import requests
import csv

# Establish a connection to the SQLite database
conn = sqlite3.connect('stock_market_one_month.db')
cursor = conn.cursor()

# Create the SQL stock_data table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        "symbol" TEXT,
        "date" DATE,
        "monthly_open" FLOAT,
        "monthly_high" FLOAT,
        "monthly_low" FLOAT,
        "monthly_volume" INTEGER
    )
''')

# List of symbols to retrieve data for
symbols = ["MSFT", "IBM"]
api_key = "YOUR_API_KEY"  # Replace with your actual API key

# Loop over each symbol
for symbol in symbols:
    # Make a request to the Alpha Vantage API to retrieve data
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey=V79H8UJ4G6QJ1YPS'
    r = requests.get(url)
    data = r.json()

    # Extract relevant data from the API response
    meta_data = data["Meta Data"]
    symbol_data = meta_data["2. Symbol"]
    monthly_time_series = data["Monthly Time Series"]

    # Loop over each date and stock data for the symbol
    for date, stock_data in monthly_time_series.items():
        monthly_open_data = stock_data["1. open"]
        monthly_high_data = stock_data["2. high"]
        monthly_low_data = stock_data["3. low"]
        monthly_volume_data = stock_data["5. volume"]

        # Insert the data into the database
        cursor.execute('''
            INSERT INTO stock_data (symbol, date, monthly_open, monthly_high, monthly_low, monthly_volume)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (symbol_data, date, monthly_open_data, monthly_high_data, monthly_low_data, monthly_volume_data))

# Execute a SELECT query to retrieve data from the table
cursor.execute('SELECT * FROM stock_data')

# Fetch all rows returned by the query
rows = cursor.fetchall()

# Define the CSV file path
csv_file_path = 'stock_data.csv'

# Open the CSV file in write mode
with open(csv_file_path, 'w', newline='') as csv_file:
    # Create a CSV writer object
    csv_writer = csv.writer(csv_file)

    # Write the header row
    csv_writer.writerow(['symbol', 'date', 'monthly_open', 'monthly_high', 'monthly_low', 'monthly_volume'])

    # Write the data rows
    csv_writer.writerows(rows)

print(f'Stock data exported to {csv_file_path}')

# Commit the changes to the database and close the connection
conn.commit()
conn.close()
