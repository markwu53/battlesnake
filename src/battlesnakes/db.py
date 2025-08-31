import sqlite3

# Connect to a database (creates file if it doesn't exist)
conn = sqlite3.connect("my_database.db")

# Create a cursor object to execute SQL commands
# cur = conn.cursor()

conn.close()
