import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import mysql.connector

# connect database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="shreeya.22",
    database="pricing_system"
)

# load data
query = "SELECT demand FROM products LIMIT 5000"
df = pd.read_sql(query, db)

# create time index
df["time"] = range(len(df))

X = df[["time"]]
y = df["demand"]

model = LinearRegression()
model.fit(X,y)

joblib.dump(model,"demand_forecast.pkl")

print("Demand forecasting model trained")