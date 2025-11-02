import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "secret_key"

# === Папка для загрузки фото ===
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# === База с ценами ===
DB_FILE = "prices.db"
if not os.path.exists(DB_FILE):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price TEXT,
            date TEXT,
            time TEXT,
            photo TEXT
        )
        """)
        conn.commit()
    print("✅ База цен создана!")

# === База с клиентами ===
CLIENTS_DB = "clients.db"
if not os.path.exists(CLIENTS_DB):
    with sqlite3.connect(CLIENTS_DB) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            effect TEXT,
            master TEXT,
            date TEXT,
            time TEXT
        )
        """)
        conn.commit()
    print("✅ База клиентов создана!")


# === Главная страница ===
@app.route("/")
def index():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT price, date, time, photo FROM prices ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()

    if row:
        price, date, time, photo = row
    else:
        price, date, time, photo = "Нет данных", "-", "-", None

    return render_template("index.html", price=price, date=date, time=time, photo=photo)


# === Админ ===
@app.route("/admin")
def admin():
    conn = sqlite3.connect(CLIENTS_DB)
    c = conn.cursor()
    c.execute("SELECT name, phone, effect, master, date, time FROM clients ORDER BY id DESC")
    clients = c.fetchall()
    conn.close()
    return render_template("admin.html", clients=clients)


# === Страница обновления цен ===
@app.route("/assign", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        price = request.form["price"]
        date = request.form["date"]
        time = request.form["time"]
        photo = request.files["photo"]

        filename = None
        if photo and photo.filename != "":
            filename = photo.filename
            upload_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            photo.save(upload_path)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO prices (price, date, time, photo) VALUES (?, ?, ?, ?)",
                  (price, date, time, filename))
        conn.commit()
        conn.close()

        flash("✅ Данные успешно обновлены!", "success")
        return redirect(url_for("index"))

    return render_template("assign.html")


# === Страница записи клиентов ===
@app.route("/record", methods=["GET", "POST"])
def record():
    effects = ["Классика", "2D", "3D", "Wet Look", "Fox", "L Doll"]
    masters = ["Нуржан", "Айгерим", "Мадина"]

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        effect = request.form["effect"]
        master = request.form["master"]
        date = request.form["date"]
        time = request.form["time"]

        conn = sqlite3.connect(CLIENTS_DB)
        c = conn.cursor()
        c.execute(
            "INSERT INTO clients (name, phone, effect, master, date, time) VALUES (?, ?, ?, ?, ?, ?)",
            (name, phone, effect, master, date, time)
        )
        conn.commit()
        conn.close()

        flash("✅ Вы успешно записались!", "success")
        return redirect(url_for("index"))

    return render_template("record.html", effects=effects, masters=masters)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

