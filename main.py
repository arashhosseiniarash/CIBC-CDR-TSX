import sqlite3 # For database
import requests #For HTTP requests in Python
import csv # For CSV functionalities
import matplotlib.pyplot as plt # For chart visualization
import pandas as pd #For data manipulation and analysis
import datetime

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

# Separate the values into lists for Matplotlib
dates = []
opens = []
highs = []
lows = []
volumes = []

for row in rows:
    dates.append(row[2])  # Assuming the date column is at index 2
    opens.append(row[3])  # Assuming the monthly_open column is at index 3
    highs.append(row[4])  # Assuming the monthly_high column is at index 4
    lows.append(row[5])  # Assuming the monthly_low column is at index 5
    volumes.append(row[6])  # Assuming the monthly_volume column is at index 6

# Commit the changes to the database and close the connection
conn.commit()
conn.close()

# Define the CSV file path
csv_file_path = 'stock_data.csv'

# Open the CSV file in write mode
with open(csv_file_path, 'w', newline='') as csv_file:
    # Create a CSV writer object
    csv_writer = csv.writer(csv_file)

    # Write the header row
    csv_writer.writerow(['id','symbol', 'date', 'monthly_open', 'monthly_high', 'monthly_low', 'monthly_volume'])


    # Write the data rows
    csv_writer.writerows(rows)

print(f'Stock data exported to {csv_file_path}')

# Analysing the dataset using pandas through the CSV created
df = pd.read_csv('stock_data.csv')

# Display the first few rows of the DataFrame
print(df.head(10))

# Get summary statistics of the DataFrame
print(df.describe())

# Check the data types of each column
print(df.dtypes)

# Check the number of rows and columns in the DataFrame
print(df.shape)

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



# Set the desired minimum and maximum dates
min_date = datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
max_date = datetime.datetime.strptime("2023-01-01", "%Y-%m-%d")

# Filter the dates and corresponding data within the specified range
filtered_dates = []
filtered_highs = []
filtered_lows = []
for date, high, low in zip(dates, highs, lows):
    date = datetime.datetime.strptime(date, "%Y-%m-%d")  # Convert date string to datetime object
    if min_date <= date <= max_date:
        filtered_dates.append(date)
        filtered_highs.append(high)
        filtered_lows.append(low)

# Plotting the data
plt.plot(filtered_dates, filtered_highs, label='Monthly High (IBM)', color='blue')  # Set the color for IBM data
plt.plot(filtered_dates, filtered_lows, label='Monthly High (MSFT)', color='red')  # Set the color for MSFT data

# Set the x-axis limits to specify the date range
plt.xlim(min_date, max_date)

plt.show()
plt.savefig('stock_plot.png')

