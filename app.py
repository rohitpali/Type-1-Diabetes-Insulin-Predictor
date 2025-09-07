from flask import Flask, render_template, request, redirect, url_for, session, flash
import joblib
import os
import json
import pandas as pd

# ------------------- FLASK APP SETUP -------------------
app = Flask(__name__)
# Use environment variable for secret key, fallback to a random default
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24))

# ------------------- LOAD ML MODEL -------------------
try:
    pkg = joblib.load("insulin_predictor_final.pkl")
    model = pkg.get("model")
    feature_list = pkg.get("features", [])
except Exception as e:
    print(f"Error loading model: {e}")
    model, feature_list = None, []

# ------------------- LOG FILE -------------------
LOG_FILE = "Logs/users.json"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        json.dump({}, f)

# ------------------- MEALS DATA WITH CALORIES -------------------
MEALS_DATA = {
    "Breakfast": {
        "Oatmeal": 150, "Boiled Eggs": 78, "Paratha": 250, "Idli": 70, "Dosa": 120,
        "Poha": 200, "Upma": 180, "Bread Toast": 80, "Paneer Bhurji": 220, "Vegetable Sandwich": 160
    },
    "Lunch": {
        "Chapati + Dal": 300, "Rice + Rajma": 350, "Rice + Chole": 360, "Dal Khichdi": 250,
        "Vegetable Pulao": 300, "Chicken Curry": 400, "Paneer Curry": 350
    },
    "Snack": {
        "Samosa": 150, "Kachori": 180, "Sandwich": 200, "Burger (small)": 250
    },
    "Dinner": {
        "Chapati + Dal": 300, "Rice + Rajma": 350, "Vegetable Curry + Roti": 320,
        "Paneer Curry": 350, "Chicken Curry": 400
    }
}

# ------------------- HELPER FUNCTIONS -------------------
def load_users():
    try:
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    try:
        with open(LOG_FILE, "w") as f:
            json.dump(users, f)
    except Exception as e:
        print(f"Error saving users: {e}")

def to_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def calculate_total_calories(selected_items, quantities, meal_data):
    total = 0
    for item, qty in zip(selected_items, quantities):
        try:
            total += meal_data.get(item, 0) * int(qty)
        except (ValueError, TypeError):
            continue
    return total

# ------------------- ROUTES -------------------
@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        users = load_users()
        if user in users:
            flash("User already exists! Try login.", "warning")
            return redirect(url_for("signup"))
        users[user] = password
        save_users(users)
        flash("Signup successful! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username")
        password = request.form.get("password")
        users = load_users()
        if users.get(user) == password:
            session["user"] = user
            return redirect(url_for("instructions"))
        flash("Invalid credentials!", "danger")
    return render_template("login.html")

@app.route("/instructions")
def instructions():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("instructions.html")

@app.route("/meals")
def meals():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("meals.html")

@app.route("/calories/<meal_type>", methods=["GET", "POST"])
def calories(meal_type):
    if "user" not in session:
        return redirect(url_for("login"))

    items_dict = MEALS_DATA.get(meal_type, {})
    total_calories = None

    if request.method == "POST":
        selected_items = request.form.getlist("item[]")
        quantities = request.form.getlist("quantity[]")
        total_calories = calculate_total_calories(selected_items, quantities, items_dict)
        session["calories"] = total_calories
        return redirect(url_for("predict"))

    return render_template(
        "calories.html",
        meal_type=meal_type,
        items=items_dict,
        total_calories=total_calories
    )

@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect(url_for("login"))

    prediction = None
    if request.method == "POST":
        try:
            glucose = to_float(request.form.get("glucose"))
            carb_rate = to_float(request.form.get("carb_rate"))
            sIOB = to_float(request.form.get("sIOB"))
            dIOB = to_float(request.form.get("dIOB"))
            weight = to_float(request.form.get("weight"))
            ICR = to_float(request.form.get("ICR"))
            ISF = to_float(request.form.get("ISF"))
            adj_carbs = to_float(session.get("calories", 0))

            meal = request.form.get("meal", "breakfast")
            data = {
                "glucose_level": glucose,
                "adj_carbs_g": adj_carbs,
                "carb_rate_g_per_hr": carb_rate,
                "sIOB": sIOB,
                "dIOB": dIOB,
                "weight_kg": weight,
                "median_ICR": ICR,
                "median_ISF": ISF,
                "meal_breakfast": 1 if meal=="breakfast" else 0,
                "meal_lunch": 1 if meal=="lunch" else 0,
                "meal_dinner": 1 if meal=="dinner" else 0,
                "meal_snack": 1 if meal=="snack" else 0,
            }

            df_input = pd.DataFrame([data]).reindex(columns=feature_list, fill_value=0).astype(float)
            if model:
                prediction = round(model.predict(df_input.values)[0], 2)
            else:
                prediction = "Model not loaded"

        except Exception as e:
            prediction = f"Error: {str(e)}"

    return render_template("predict.html", prediction=prediction, calories=session.get("calories", 0))

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("welcome"))

# ------------------- MAIN -------------------
if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", False))
