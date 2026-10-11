import os
import re
import html
import psycopg

from flask import Flask, request, redirect, session
from psycopg.rows import dict_row
from psycopg.errors import UniqueViolation
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.environ["FLASK_SECRET_KEY"],
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "false").lower() == "true",
    PERMANENT_SESSION_LIFETIME=1800
)


def get_db():
    return psycopg.connect(
        host=os.getenv("PGHOST", "db"),
        dbname=os.getenv("PGDATABASE", "loginapp"),
        user=os.getenv("PGUSER", "appuser"),
        password=os.environ["PGPASSWORD"],
        row_factory=dict_row,
        connect_timeout=5
    )


def page(message, status=200):
    return f"""
    <!DOCTYPE html>
    <html>
      <head><title>Login App</title></head>
      <body>
        <h2>{html.escape(message)}</h2>
        <a href="/">Login page</a>
      </body>
    </html>
    """, status


@app.get("/api/health")
def health():
    with get_db() as conn:
        conn.execute("SELECT 1")
    return {"status": "healthy"}


@app.post("/api/register")
def register():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not re.fullmatch(r"[A-Za-z0-9_.-]{3,50}", username):
        return page("Username must be 3-50 valid characters.", 400)

    if len(password) < 12 or len(password) > 128:
        return page("Password must contain 12-128 characters.", 400)

    password_hash = generate_password_hash(password)

    try:
        with get_db() as conn:
            conn.execute(
                """
                INSERT INTO users (username, password_hash)
                VALUES (%s, %s)
                """,
                (username, password_hash)
            )
    except UniqueViolation:
        return page("Username already exists. Please choose another.", 409)

    return page("Registration successful. You can now log in.")


@app.post("/api/login")
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    with get_db() as conn:
        user = conn.execute(
            """
            SELECT id, username, password_hash
            FROM users
            WHERE username = %s
            """,
            (username,)
        ).fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return page("Invalid username or password.", 401)

    session.clear()
    session.permanent = True
    session["user_id"] = user["id"]
    session["username"] = user["username"]

    return redirect("/api/dashboard", code=303)


@app.get("/api/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/", code=303)

    username = html.escape(session["username"])

    return f"""
    <!DOCTYPE html>
    <html>
      <head><title>Dashboard</title></head>
      <body>
        <h2>Welcome, {username}!</h2>
        <p>You have logged in successfully.</p>
        <form action="/api/logout" method="post">
          <button type="submit">Logout</button>
        </form>
      </body>
    </html>
    """


@app.post("/api/logout")
def logout():
    session.clear()
    return redirect("/", code=303)
