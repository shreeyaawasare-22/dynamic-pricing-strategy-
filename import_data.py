import pandas as pd
import sqlite3

# load CSV
df = pd.read_csv("dataset/ecommerce_dynamic_pricing_100k.csv")

# connect database
conn = sqlite3.connect("pricing.db")

# replace table
df.to_sql("products", conn, if_exists="replace", index=False)

conn.commit()
conn.close()

print("CSV data imported into database successfully")