import sqlite3

conn = sqlite3.connect("pricing.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
product_id INTEGER PRIMARY KEY,
category TEXT,
cost_price REAL,
competitor_price REAL,
demand INTEGER,
inventory INTEGER,
season TEXT,
traffic INTEGER,
optimal_price REAL
)
""")

conn.commit()
conn.close()

print("Products table created successfully")