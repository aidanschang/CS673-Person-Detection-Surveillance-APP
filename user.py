# user.py

from flask import Blueprint, render_template, redirect, url_for, request, flash
import sqlite3
import os
import base64

user = Blueprint("user", __name__, template_folder="templates")

# current_user is current login user,it is user email.
current_user = ""


def get_db_connection():
    """Return connection to the database."""
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


# encrypt user informatiom and prevent sql injection
def encode_64(str):
    str_bytes = str.encode("ascii")
    base64_bytes = base64.b64encode(str_bytes)
    base64_str = base64_bytes.decode("ascii")
    return base64_str


# decrypt user_info
def decode_64(str):
    str_bytes = str.encode("ascii")
    base64_bytes = base64.b64decode(str_bytes)
    base64_str = base64_bytes.decode("ascii")
    return base64_str


@user.route("/")
def index():
    if len(current_user) == 0:
        return render_template("index.html")
    else:
        return render_template("home.html")
    


@user.route("/login")
def login():
    if len(current_user) == 0:
        return render_template("login.html")
    else:
        return render_template("home.html")


@user.route("/login", methods=["POST"])
def login_post():
    email = encode_64(request.form.get("email"))
    password = encode_64(request.form.get("password"))
    conn = get_db_connection()
    if len(email) == 0 or len(password) == 0:
        flash("please input Email and Password")
        return redirect(url_for("user.login"))
    checkemail = conn.execute(
        "SELECT email FROM users WHERE email = ?", (email,)
    ).fetchall()
    checkuser = conn.execute(
        "SELECT password FROM users WHERE email = ?", (email,)
    ).fetchone()
    if len(checkemail) == 0:
        conn.close()
        flash("user not exist.")
        # code to validate and add user to database goes here
        return redirect(url_for("user.login"))
    else:
        if checkuser[0] == password:
            global current_user
            current_user = email
            path = "static/uploads/" + current_user + "/"
            if os.path.exists(path) is False:
                os.mkdir(path)
            conn.commit()
            conn.close()
            return redirect(url_for("home"))
        else:
            conn.commit()
            conn.close()
            flash("Wrong password.")
            # code to validate and add user to database goes here
            return redirect(url_for("user.login"))


@user.route("/signup")
def signup():
    return render_template("signup.html")


@user.route("/signup", methods=["POST"])
def signup_post():
    email = encode_64(request.form.get("email"))
    name = encode_64(request.form.get("name"))
    password = encode_64(request.form.get("password"))
    if len(email) == 0 or len(password) == 0:
        flash("please input Email,Name and Password")
        return redirect(url_for("user.signup"))
    conn = get_db_connection()
    checkuser = conn.execute(
        "SELECT email FROM users WHERE email = ?", (email,)
    ).fetchall()
    if len(checkuser) == 0:
        conn.execute(
            "INSERT INTO users (email, name,password) VALUES (?, ?, ?)",
            (email, name, password),
        )
        conn.commit()
        conn.close()
        flash("Sign up success.")
        # code to validate and add user to database goes here
        return redirect(url_for("user.login"))
    else:
        flash("Email already registered")
    conn.commit()
    conn.close()
    # code to validate and add user to database goes here
    return redirect(url_for("user.signup"))


@user.route("/logout")
def logout():
    global current_user
    current_user = ""
    flash("You have been logged out.")
    return redirect(url_for("user.login"))
