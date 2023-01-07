import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
from datetime import date

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///cheapkuk.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Take Orders to Cart"""
    user_id = session["user_id"]
    today = date.today()

    if request.method == "POST":
        # Add TAPA to cart
        if request.form.get('button') == '1':
            check = db.execute("SELECT * FROM cart WHERE product_id = 1 AND customer_id = ? AND date = ? AND status IS NULL", user_id, today)
            if len(check) == 1:
                db.execute("UPDATE cart SET amount = amount + 1, total = total + 190.00 WHERE product_id = 1 AND customer_id = ? AND date = ? AND status IS NULL", user_id, today)
            else:
                db.execute("INSERT INTO cart (product_id, amount, total, customer_id, date) VALUES (1, 1, 190.00, ?, ?)", user_id, today)
            return redirect("/cart")

        # Add LONGGANISA to cart
        elif request.form.get('button') == '2':
            check = db.execute("SELECT * FROM cart WHERE product_id = 2 AND customer_id = ? AND date = ? AND status IS NULL", user_id, today)
            if len(check) == 1:
                db.execute("UPDATE cart SET amount = amount + 1, total = total + 140.00 WHERE product_id = 2 AND customer_id = ? AND date = ? AND status IS NULL", user_id, today)
            else:
                db.execute("INSERT INTO cart (product_id, amount, total, customer_id, date) VALUES (2, 1, 140.00, ?, ?)", user_id, today)
            return redirect("/cart")

        # Add LIEMPO to cart
        elif request.form.get('button') == '3':
            check = db.execute("SELECT * FROM cart WHERE product_id = 3 AND customer_id = ? AND date = ? AND status IS NULL", user_id, today)
            if len(check) == 1:
                db.execute("UPDATE cart SET amount = amount + 1, total = total + 170.00 WHERE product_id = 3 AND customer_id = ? AND date = ? AND status IS NULL", user_id, today)
            else:
                db.execute("INSERT INTO cart (product_id, amount, total, customer_id, date) VALUES (3, 1, 170.00, ?, ?)", user_id, today)
            return redirect("/cart")

        # Add ADOBO FLAKES to cart
        elif request.form.get('button') == '4':
            check = db.execute("SELECT * FROM cart WHERE product_id = 4 AND customer_id = ? AND date = ? AND status IS NULL", user_id, today)
            if len(check) == 1:
                db.execute("UPDATE cart SET amount = amount + 1, total = total + 230.00 WHERE product_id = 4 AND customer_id = ? AND date = ?", user_id, today)
            else:
                db.execute("INSERT INTO cart (product_id, amount, total, customer_id, date) VALUES (4, 1, 230.00, ?, ?)", user_id, today)
            return redirect("/cart")

    else:
        if user_id == 2:
            customers_today = []
            get_orders = db.execute("SELECT products.product_name, cart.amount, cart.total, cart.customer_id, cart.date FROM cart LEFT JOIN products ON cart.product_id=products.id WHERE date LIKE ? AND cart.status = 'PENDING' ORDER BY customer_id", today)
            get_customers = db.execute("SELECT DISTINCT cart.customer_id, customers.first_name, customers.last_name, customers.address, customers.city, customers.mobile_number, cart.date FROM cart LEFT JOIN customers ON cart.customer_id=customers.id WHERE date LIKE ? AND cart.status = 'PENDING' ORDER BY customer_id", today)

            for id in get_customers:
                customers_today.append(id)

            return render_template("orders.html", orders=get_orders, customers=customers_today, customerinfo=get_customers)

        return render_template("index.html")


@app.route("/about", methods=["GET", "POST"])
@login_required
def about():
    return render_template("about.html")


@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():
    """Show history of transactions"""
    if request.method == "POST":
        user_id = session["user_id"]
        today = date.today()

        if request.form.get('button') == 'place_order':
            db.execute("UPDATE cart SET status = 'PENDING' WHERE customer_id = ? AND date = ?", user_id, today)
            return render_template("success.html")

        elif request.form.get('button') == 'clear':
            db.execute("DELETE FROM cart WHERE customer_id = ? AND date = ? AND status IS NULL", user_id, today)
            return render_template("cart.html")

        return render_template("success.html")

    else:
        user_id = session["user_id"]
        today = date.today()

        # ***** CHANGE DATE LIKE BACK *******
        rows = db.execute("SELECT products.product_name AS Product, cart.amount AS Amount, products.price AS Price, cart.total AS Total FROM cart LEFT JOIN products ON cart.product_id=products.id WHERE cart.customer_id = ? AND date LIKE ? AND cart.status IS NULL",
                            user_id, today)

        users = db.execute("SELECT customers.first_name, customers.last_name, customers.address, customers.city, customers.mobile_number FROM customers LEFT JOIN cart ON customers.id=cart.customer_id WHERE customers.id = ? AND date LIKE ? LIMIT 1;", user_id, today)

        get_total_cart = []
        for item in rows:
            total = item["Total"]
            get_total_cart.append(total)

        total_cart = sum(get_total_cart)

        return render_template("cart.html", rows=rows, total_cart=total_cart, users=users)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM customers WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        street_address = request.form.get("street_address")
        city_address = request.form.get("city_address")
        mobile_number = request.form.get("mobile")

        hash = generate_password_hash(password)

        if password != confirmation:
            return render_template("password_mismatch.html")

        db.execute("INSERT INTO customers (username, first_name, last_name, address, city, mobile_number, hash) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    username, first_name, last_name, street_address, city_address, mobile_number, hash)

        return render_template("login.html")

    else:

        return render_template("register.html")


@app.route("/success", methods=["GET"])
@login_required
def success():
    return render_template("success.html")



