from flask import Flask, render_template, request, redirect
import sqlite3
import random
import string
import validators

app = Flask(__name__)

DATABASE = "database.db"


# Create database table
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS urls(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        original_url TEXT NOT NULL,
        short_code TEXT UNIQUE NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# Generate unique short code
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits

    while True:
        short_code = ''.join(random.choice(characters)
                             for _ in range(length))

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM urls WHERE short_code=?",
            (short_code,)
        )

        existing = cursor.fetchone()

        conn.close()

        if not existing:
            return short_code


@app.route("/", methods=["GET", "POST"])
def home():

    short_url = None

    if request.method == "POST":

        original_url = request.form["url"]

        if not validators.url(original_url):
            return render_template(
                "error.html",
                message="Please enter a valid URL."
            )

        short_code = generate_short_code()

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO urls(original_url, short_code) VALUES(?, ?)",
            (original_url, short_code)
        )

        conn.commit()
        conn.close()

        short_url = request.host_url + short_code

    return render_template(
        "index.html",
        short_url=short_url
    )


@app.route("/<short_code>")
def redirect_to_url(short_code):

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT original_url FROM urls WHERE short_code=?",
        (short_code,)
    )

    result = cursor.fetchone()

    conn.close()

    if result:
        return redirect(result[0])

    return render_template(
        "error.html",
        message="Short URL does not exist."
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)