import sqlite3
import yfinance as yf
import csv
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import requests

# Function to fetch data from Alpha Vantage API
def fetch_alpha_vantage_data(symbol):
    api_key = "YOUR_API_KEY"  # Replace with your actual API key
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol={symbol}&apikey={api_key}'
    r = requests.get(url)
    return r.json()

# Function to fetch data from Yahoo Finance API
def fetch_yahoo_finance_data(symbol, start_date, end_date):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period='1mo', start=start_date, end=end_date)
    return data

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
symbols = ["MSFT", "MSFT.NE"]

# Loop over each symbol
for symbol in symbols:
    if ".NE" in symbol:  # Check if the symbol is non-US
        data = fetch_yahoo_finance_data(symbol, "1999-12-31", "2023-08-02")  # Specify your start and end dates
        for date, row in data.iterrows():
            monthly_open_data = row['Open']
            monthly_high_data = row['High']
            monthly_low_data = row['Low']
            monthly_volume_data = row['Volume']
            cursor.execute('''
                INSERT INTO stock_data (symbol, date, monthly_open, monthly_high, monthly_low, monthly_volume)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symbol, date.strftime('%Y-%m-%d'), monthly_open_data, monthly_high_data, monthly_low_data, monthly_volume_data))
    else:
        data = fetch_alpha_vantage_data(symbol)
        meta_data = data["Meta Data"]
        symbol_data = meta_data["2. Symbol"]
        monthly_time_series = data["Monthly Time Series"]
        for date, stock_data in monthly_time_series.items():
            monthly_open_data = stock_data["1. open"]
            monthly_high_data = stock_data["2. high"]
            monthly_low_data = stock_data["3. low"]
            monthly_volume_data = stock_data["5. volume"]
            cursor.execute('''
                INSERT INTO stock_data (symbol, date, monthly_open, monthly_high, monthly_low, monthly_volume)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (symbol_data, date, float(monthly_open_data), float(monthly_high_data), float(monthly_low_data), int(monthly_volume_data)))

# Execute a SELECT query to retrieve data from the table
cursor.execute('SELECT * FROM stock_data')

# Fetch all rows returned by the query
rows = cursor.fetchall()

# Commit the changes to the database and close the connection
conn.commit()
conn.close()

# Define the CSV file path
csv_file_path = 'C:/Users/arash/PycharmProjects/pythonProject/stock_data.csv'

# Open the CSV file in write mode with the specified path
with open(csv_file_path, 'w', newline='') as csv_file:
    # Create a CSV writer object
    csv_writer = csv.writer(csv_file)

    # Write the header row
    csv_writer.writerow(['id','symbol', 'date', 'monthly_open', 'monthly_high', 'monthly_low', 'monthly_volume'])

    # Write the data rows
    csv_writer.writerows(rows)

print(f'Stock data exported to {csv_file_path}')

# Analysing the dataset using pandas through the CSV created
df = pd.read_csv(csv_file_path)

# Check for duplicate entries
date_counts = df.groupby('date').size()
duplicate_dates = date_counts[date_counts > 1]
if not duplicate_dates.empty:
    print("Duplicate entries found for the following dates:")
    print(duplicate_dates)

# Display the first few rows of the DataFrame
print(df.head(10))

# Get summary statistics of the DataFrame
print(df.describe())

# Check the data types of each column
print(df.dtypes)

# Convert the "date" column to datetime format
df['date'] = pd.to_datetime(df['date'])

# Find the minimum and maximum dates
min_date = df['date'].min()
max_date = df['date'].max()

# Print the results
print(f"Minimum date: {min_date}")
print(f"Maximum date: {max_date}")

# Plotting the data
plt.figure(figsize=(12, 6))

# Set the desired minimum
