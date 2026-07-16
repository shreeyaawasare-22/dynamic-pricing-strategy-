from email.policy import default
from flask import Flask, render_template, request, redirect, url_for,session
import joblib
import pandas as pd
import plotly.express as px
import plotly.io as pio
import mysql.connector
import matplotlib
matplotlib.use("Agg")

app = Flask(__name__)
app.secret_key = "secret123"

forecast_model = joblib.load("demand_forecast.pkl")

# ---------------- DATABASE CONNECTION ----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="shreeya.22",
    database="pricing_system"
)

cursor = db.cursor()

# ---------------- LOAD ML MODEL ----------------
model = joblib.load("price_model.pkl")

# ---------------- HOME PAGE ----------------
@app.route("/")
def home():
    return render_template("index.html")


# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            session['user'] = email
            return redirect('/')
        else:
            return render_template("login.html", error="Invalid credentials ❌")

    return render_template("login.html")


# 📝 REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match ❌")

        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            return render_template("register.html", error="User already exists ⚠️")

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            (name, email, password)
        )
        db.commit()

        return redirect('/login')

    return render_template("register.html")


# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# ---------------- PRICE PREDICTION ----------------
@app.route("/predict", methods=["POST"])
def predict():

    cost_price = float(request.form["cost_price"])
    competitor_price = float(request.form["competitor_price"])
    demand = float(request.form["demand"])
    inventory = float(request.form["inventory"])
    traffic = float(request.form["traffic"])
    season = int(request.form["season"])

    season_map = {1: "Normal", 2: "Festive", 3: "Holiday"}
    season_name = season_map.get(season, "Normal")

    sample = pd.DataFrame({
        "cost_price":[cost_price],
        "competitor_price":[competitor_price],
        "demand":[demand],
        "inventory":[inventory],
        "traffic":[traffic],
        "season":[season]
    })

    # -------- AI PRICE PREDICTION --------
    prediction = model.predict(sample)
    base_price = round(prediction[0],2)

    # -------- SURGE PRICING --------
    # -------- SURGE PRICING --------
    surge_multiplier = 1.0

    if demand > 900:
        surge_multiplier += 0.25
    elif demand > 700:
        surge_multiplier += 0.15
    elif demand < 200:
        surge_multiplier -= 0.1

# 🔥 ADD THESE HERE (not below)
    if traffic > 800:
        surge_multiplier += 0.1

    if inventory < 100:
        surge_multiplier += 0.1

    surge_price = round(base_price * surge_multiplier,2)

    # -------- PRICE RANGE --------
    min_price = round(surge_price * 0.9,2)
    max_price = round(surge_price * 1.1,2)

    # -------- COMPETITOR MONITORING --------
    price_diff = competitor_price - surge_price

    if price_diff < -50:
        adjusted_price = competitor_price * 0.97   # aggressive competition

    elif price_diff > 100:
        adjusted_price = surge_price * 1.08        # premium pricing

    else:
        adjusted_price = surge_price

    adjusted_price = round(adjusted_price, 2)
    
    # -------- REVENUE & PROFIT --------
    revenue = adjusted_price * demand
    profit = (adjusted_price - cost_price) * demand

    # -------- PRICE OPTIMIZATION --------
    best_price = adjusted_price
    best_profit = profit

    for test_price in range(int(min_price), int(max_price)+1, 5):

        test_profit = (test_price - cost_price) * demand

        if test_profit > best_profit:
            best_profit = test_profit
            best_price = test_price

    # -------- STRATEGY --------
    if demand > 800 and inventory < 200:
        strategy = "Increase price due to high demand and low inventory"
    elif inventory > 700:
        strategy = "Reduce price to clear excess inventory"
    elif competitor_price < base_price:
        strategy = "Keep price competitive with market"
    else:
        strategy = "Maintain current pricing strategy"

    # -------- RISK ANALYSIS --------
    if adjusted_price > competitor_price * 1.2:
        risk = "High Risk: Price much higher than competitor"
    elif adjusted_price < cost_price:
        risk = "Loss Risk: Price below cost"
    else:
        risk = "Safe Pricing Zone"
        
    # -------- SAVE TO DATABASE --------
    cursor.execute("""
    INSERT INTO pricing_history
    (product_id, predicted_price, revenue, profit)
    VALUES (%s,%s,%s,%s)
""",(1, adjusted_price, revenue, profit))

    db.commit()

    # -------- AI INSIGHT --------
    if demand > 800:
        insight = "High demand detected — increase pricing opportunity"
    elif inventory > 700:
        insight = "Excess inventory — consider discounts"
    else:
        insight = "Balanced market condition"

# -------- DEMAND FORECAST --------

    future_time = [[demand]]   # using demand as simple time feature
    predicted_demand = forecast_model.predict(future_time)[0]

    predicted_demand = round(predicted_demand,2)
    
    return render_template(
    "index.html",
    prediction_text=surge_price,
    competitor_adjusted_price=adjusted_price,
    optimal_price=best_price,
    optimal_profit=round(best_profit,2),
    base_price=base_price,
    surge_multiplier=surge_multiplier,
    min_price=min_price,
    max_price=max_price,
    revenue=round(revenue,2),
    profit=round(profit,2),
    strategy=strategy,
    risk=risk,
    forecast=predicted_demand,
    insight=insight
)

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    # -------- USER INPUT FROM PREDICTION --------
    def get_float(value, default=0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    demand_input = get_float(request.args.get("demand"))
    inventory_input = get_float(request.args.get("inventory"))
    competitor_input = get_float(request.args.get("competitor_price"))
    price_input = get_float(request.args.get("predicted_price"))
    season_input = int(request.args.get("season", 1))
    # -------- LOAD DATA FROM DATABASE --------
    if demand_input > 0:
        query = f"""
    SELECT * FROM products
    WHERE demand BETWEEN {demand_input-200} AND {demand_input+200}
    LIMIT 3000
    """
    else:
        query = "SELECT * FROM products ORDER BY RAND() LIMIT 3000"

    df = pd.read_sql(query, db)

# if very few rows are returned fallback to random data
    if len(df) < 50:
        df = pd.read_sql("SELECT * FROM products ORDER BY RAND() LIMIT 3000", db)

    # -------- DEMAND VS PRICE --------
    fig1 = px.scatter(
        df,
        x="demand",
        y="optimal_price",
        opacity=0.4,
        trendline="ols",
        title="Demand vs Optimal Price"
    )

    fig1.add_scatter(
        x=[demand_input],
        y=[price_input],
        mode="markers",
        marker=dict(color="red", size=15),
        name="Your Product Price"
    )

    fig1.add_vline(
    x=demand_input,
    line_color="red",
    line_dash="dash"
)
    demand_graph = pio.to_html(fig1, full_html=False)

    # -------- COMPETITOR PRICE --------
    fig2 = px.scatter(
        df,
        x="competitor_price",
        y="optimal_price",
        opacity=0.4,
        trendline="ols",
        title="Competitor Price Impact"
    )

    fig2.add_scatter(
        x=[competitor_input],
        y=[price_input],
        mode="markers",
        marker=dict(color="green", size=15),
        name="Your Product"
    )

    competitor_graph = pio.to_html(fig2, full_html=False)

    # -------- INVENTORY GRAPH --------
    fig3 = px.scatter(
        df,
        x="inventory",
        y="optimal_price",
        opacity=0.4,
        title="Inventory vs Price"
    )

    fig3.add_scatter(
        x=[inventory_input],
        y=[price_input],
        mode="markers",
        marker=dict(color="orange", size=15),
        name="Your Product"
    )

    inventory_graph = pio.to_html(fig3, full_html=False)

    # -------- DEMAND DISTRIBUTION --------
    df_temp = df.copy()

    new_row = df_temp.iloc[-1].copy()
    new_row["demand"] = demand_input

    df_temp = pd.concat([df_temp, new_row.to_frame().T], ignore_index=True)

    fig4 = px.histogram(
    df,
    x="demand",
    nbins=30,   # more bins = better clarity
    title="Demand Distribution with User Input",
    opacity=0.75
)

# 🔴 Vertical Line (Your Input)
    fig4.add_vline(
    x=demand_input,
    line_width=4,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Your Demand: {demand_input}",
    annotation_position="top"
)
    fig4.update_layout(
    xaxis_title="Demand",
    yaxis_title="Frequency",
    plot_bgcolor="white",
    paper_bgcolor="white",
    bargap=0.1
)

    fig4.update_xaxes(showgrid=True, gridcolor="lightgray")
    fig4.update_yaxes(showgrid=True, gridcolor="lightgray")

    fig4.update_traces(
    marker=dict(
        color="#4a90e2",
        line=dict(width=1, color="black")
    )
)
    demand_dist_graph = pio.to_html(fig4, full_html=False)
    # -------- SEASONAL IMPACT --------
    season_map = {
    "1": "Normal",
    "2": "Festive",
    "3": "Holiday"
}

    season_label = season_map.get(str(season_input), "Normal")

    fig5 = px.box(
        df,
        x="season",
        y="optimal_price",
        title="Seasonal Pricing Impact"
    )

    fig5.add_scatter(
        x=[season_label],
        y=[price_input],
        mode="markers",
        marker=dict(color="red", size=14),
        name="Your Product"
    )

    season_graph = pio.to_html(fig5, full_html=False)

    # -------- DEMAND FORECAST GRAPH --------
    df["time"] = range(len(df))

    future_steps = list(range(len(df), len(df) + 5))
    future_preds = forecast_model.predict([[t] for t in future_steps])

    fig_forecast = px.line(df, x="time", y="demand", title="Demand Trend with Forecast")

    fig_forecast.add_scatter(
    x=future_steps,
    y=future_preds,
    mode="lines+markers",
    line=dict(color="red", dash="dash"),
    name="Forecast"
)

    forecast_graph = pio.to_html(fig_forecast, full_html=False)

# -------- SINGLE VALUE FOR TREND --------
    predicted_demand = float(future_preds[0])

    # -------- BUSINESS METRICS --------
    avg_price = df["optimal_price"].mean()
    avg_demand = df["demand"].mean()
    total_inventory = df["inventory"].sum()
    total_revenue = (df["optimal_price"] * df["demand"]).sum()
    avg_inventory = df["inventory"].mean()
    max_price = df["optimal_price"].max()

    # -------- AI BUSINESS INSIGHTS --------

        # Market status
    if avg_demand > 700:
     market_status = "High Demand Market 🔥"
    elif avg_demand < 300:
     market_status = "Low Demand Market 🟢"
    else:
        market_status = "Stable Market 📊"

# Pricing suggestion
    if avg_inventory > 700:
        pricing_suggestion = "Reduce price to clear stock"
    elif avg_demand > 800:
        pricing_suggestion = "Increase price to maximize profit"
    else:
        pricing_suggestion = "Maintain balanced pricing"

# Demand trend
    # -------- DEMAND TREND --------
    if predicted_demand > avg_demand:
        demand_trend = "Demand expected to increase 📈"
    else:
        demand_trend = "Demand may decline 📉"

# Risk level
    if avg_price > competitor_input * 1.2:
        risk_level = "High Pricing Risk ⚠️"
    else:
        risk_level = "Safe Pricing Zone ✅"

    return render_template(
    "dashboard.html",
    avg_price=round(avg_price,2),
    avg_demand=round(avg_demand,2),
    inventory=total_inventory,
    revenue="{:,.2f}".format(total_revenue),
    avg_inventory=round(avg_inventory,2),
    max_price=round(max_price,2),
    
    demand_graph=demand_graph,
    competitor_graph=competitor_graph,
    inventory_graph=inventory_graph,
    demand_dist_graph=demand_dist_graph,
    season_graph=season_graph,
    forecast_graph=forecast_graph,
    market_status=market_status,
    pricing_suggestion=pricing_suggestion,
    demand_trend=demand_trend,
    risk_level=risk_level
    
)


# ---------------- PRODUCTS TABLE ----------------
@app.route("/products")
def products():

    cursor.execute("SELECT * FROM products LIMIT 1000")
    data = cursor.fetchall()

    return render_template("products.html", data=data)


@app.route("/forecast")
def forecast():

    query = "SELECT demand FROM products LIMIT 5000"
    df = pd.read_sql(query, db)

    # -------- DEMAND FORECAST --------
    df["time"] = range(len(df))

    next_time = [[len(df)]]

    predicted_demand = forecast_model.predict(next_time)[0]

    return render_template(
    "forecast.html",
    forecast=round(predicted_demand,2)
)

@app.route("/live-dashboard-data")
def live_dashboard_data():

    import random

    # Generate multiple points (for graph)
    demand_data = [random.randint(100,1000) for _ in range(10)]
    price_data = [round(d * random.uniform(0.8,1.2),2) for d in demand_data]

    latest_demand = demand_data[-1]
    latest_price = price_data[-1]

    return {
        "demand_series": demand_data,
        "price_series": price_data,
        "latest_demand": latest_demand,
        "latest_price": latest_price
    
    }
@app.route("/live-plot")
def live_plot():

    import random
    import pandas as pd
    import plotly.express as px
    import plotly.io as pio

    demand = [random.randint(100,1000) for _ in range(10)]
    price = [d * random.uniform(0.8,1.2) for d in demand]

    df = pd.DataFrame({
        "time": list(range(1,11)),
        "demand": demand,
        "price": price
    })

    fig = px.line(df, x="time", y=["demand","price"],
                  title="Live Demand vs Price Trend")

    return pio.to_html(fig, full_html=False)


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(debug=True)