# ---------------- IMPORT LIBRARIES ----------------
import joblib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor


# ---------------- LOAD DATASET ----------------
df = pd.read_csv("dataset/ecommerce_dynamic_pricing_100k.csv")


# ---------------- DATA PREPROCESSING ----------------
df["season"] = df["season"].map({
    "Normal": 1,
    "Festive": 2,
    "Holiday": 3
})


# ---------------- DATA VISUALIZATION ----------------

# Demand vs Optimal Price
sns.scatterplot(x="demand", y="optimal_price", data=df)
plt.title("Demand vs Optimal Price")
plt.show()

# Competitor Price Impact
sns.scatterplot(x="competitor_price", y="optimal_price", data=df)
plt.title("Competitor Price Impact")
plt.show()

# Inventory vs Price
sns.scatterplot(x="inventory", y="optimal_price", data=df)
plt.title("Inventory vs Price")
plt.show()

# Seasonal Pricing
sns.boxplot(x="season", y="optimal_price", data=df)
plt.title("Seasonal Pricing")
plt.show()


# ---------------- CORRELATION HEATMAP ----------------
plt.figure(figsize=(10,6))

corr = df.corr(numeric_only=True)

sns.heatmap(corr, annot=True, cmap="coolwarm")

plt.title("Feature Correlation Heatmap")

plt.show()


# ---------------- MODEL FOR FEATURE IMPORTANCE ----------------

X = df[[
    "cost_price",
    "competitor_price",
    "demand",
    "inventory",
    "traffic",
    "season"
]]

y = df["optimal_price"]

model = joblib.load("price_model.pkl")

# ---------------- FEATURE IMPORTANCE ----------------
features = X.columns
importance = model.feature_importances_

plt.figure(figsize=(8,5))

sns.barplot(x=importance, y=features)

plt.title("Feature Importance in Dynamic Pricing")

plt.xlabel("Importance Score")
plt.ylabel("Features")

plt.show()


# ---------------- DEMAND ELASTICITY ----------------
sample_df = df.sample(3000)

sns.regplot(
    x="demand",
    y="optimal_price",
    data=sample_df,
    scatter_kws={"alpha": 0.3}
)

plt.title("Demand vs Optimal Price Trend")

plt.show()

# ---------------- SAMPLE PRICE PREDICTION ----------------

sample_input = [[
    200,  # cost_price
    250,  # competitor_price
    500,  # demand
    300,  # inventory
    7000, # traffic
    2     # season (Festive)
]]

predicted_price = model.predict(sample_input)

print("Predicted Optimal Price:", predicted_price[0])


# ---------------- PROFIT CALCULATION ----------------

df["predicted_price"] = model.predict(X)

df["profit"] = df["predicted_price"] - df["cost_price"]

print(df[["cost_price","predicted_price","profit"]].head())

# ---------------- REVENUE ANALYSIS ----------------

df["revenue"] = df["optimal_price"] * df["demand"]

sample_df = df.sample(3000)

sns.scatterplot(x="demand", y="revenue", data=sample_df)

plt.title("Demand vs Revenue")

plt.show()

# ---------------- DATA EXPLORATION ----------------

# First 5 rows
print(df.head())

# Dataset information
print(df.info())

# Statistical summary
print(df.describe())
