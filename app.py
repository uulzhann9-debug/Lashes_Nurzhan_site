import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "secret_key"

# Папка для загрузки фото
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Проверяем — если нет папки, создаём
if not os.path.exists(app.config["UPLOAD_FOLDER"]):
    os.makedirs(app.config["UPLOAD_FOLDER"])

# Имя базы данных
DB_FILE = "prices.db"

# Если базы нет — создаём
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
    print("✅ Новая база данных успешно создана!")

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

@app.route("/admin")
def admin():
    # Исправлено: добавляем пустой словарь, чтобы не было ошибки
    return render_template('admin.html', prices={})


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
        c.execute(
            "INSERT INTO prices (price, date, time, photo) VALUES (?, ?, ?, ?)",
            (price, date, time, filename)
        )
        conn.commit()
        conn.close()

        flash("✅ Данные успешно обновлены!", "success")
        return redirect(url_for("index"))

    return render_template("assign.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
