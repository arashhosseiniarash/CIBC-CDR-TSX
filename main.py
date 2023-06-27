import sqlite3
import requests
#shift F10
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

# Make a request to the Alpha Vantage API to retrieve data
url = 'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=IBM&apikey=V79H8UJ4G6QJ1YPS'
r = requests.get(url)
data = r.json()  # Parse the JSON response into a Python dictionary

print(data)

## Extract relevant data from the API response to fill the database
meta_data = data["Meta Data"]  # Access the list of data objects
symbol = meta_data["2. Symbol"]  # Access the symbol within the data object

monthly_time_series = data["Monthly Time Series"] # Access the time within the data object
for date, stock_data in monthly_time_series.items():
    monthly_open_data = stock_data["1. open"]  # Access the open price for each data object, float() function is used as the data in a string
    monthly_high_data = stock_data["2. high"]  # Access the high price for each data object
    monthly_low_data = stock_data["3. low"]  # Access the low price for each data object
    monthly_volume_data = stock_data["5. volume"]

cursor.execute('''
    INSERT INTO stock_data (symbol,date, monthly_open, monthly_high, monthly_low, monthly_volume)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', ( symbol, date, monthly_open_data, monthly_high_data, monthly_low_data, monthly_volume_data)
    )

# Commit the changes to the database and close the connection
conn.commit()
conn.close()