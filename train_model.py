import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

df = pd.read_csv("dataset/ecommerce_dynamic_pricing_100k.csv")

print("Dataset Loaded")
print(df.head())

df["season"] = df["season"].map({
    "Normal":1,
    "Festive":2,
    "Holiday":3
})

X = df[[
    "cost_price",
    "competitor_price",
    "demand",
    "inventory",
    "traffic",
    "season"
]]
y = df["optimal_price"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(X_train, y_train)

print("Model Training Complete")

predictions = model.predict(X_test)

score = r2_score(y_test, predictions)

print("Model Accuracy (R² Score):", score)

joblib.dump(model, "price_model.pkl")

print("Model Saved Successfully")

sample = pd.DataFrame({
    "cost_price":[300],
    "competitor_price":[450],
    "demand":[600],
    "inventory":[200],
    "traffic":[1500],
    "season":[2]
})

prediction = model.predict(sample)

print("Predicted Price:", prediction)