import os
import sqlite3
import requests
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "secret_key"

# === НАСТРОЙКИ ===
UPLOAD_FOLDER = os.path.join("static", "uploads")
DB_FILE = "prices.db"

# Твой Telegram Bot Token и ID
BOT_TOKEN = "8433998136:AAGw7DHJTXfuRsHIozU-Cf8PimJVFtiECC8"
CHAT_ID = "7541525471"

# Создаём нужные папки, если их нет
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Создаём базу, если нет
if not os.path.exists(DB_FILE):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            price TEXT,
            date TEXT,
            time TEXT,
            photo TEXT
        )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS records (
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
    print("✅ База данных успешно создана!")


# === ГЛАВНАЯ СТРАНИЦА ===
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


# === АДМИН-ПАНЕЛЬ ===
@app.route("/admin")
def admin():
    return render_template("admin.html", prices={})


# === ОБНОВЛЕНИЕ ЦЕН ===
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


# === ЗАПИСЬ КЛИЕНТА ===
@app.route("/record", methods=["GET", "POST"])
def record():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        effect = request.form["effect"]
        master = request.form["master"]
        date = request.form["date"]
        time = request.form["time"]

        # Сохраняем запись в БД
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            INSERT INTO records (name, phone, effect, master, date, time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, phone, effect, master, date, time))
        conn.commit()
        conn.close()

        # Отправляем уведомление в Telegram
        message = (
            f"📅 Новая запись!\n\n"
            f"👩 Имя: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"✨ Эффект: {effect}\n"
            f"💅 Мастер: {master}\n"
            f"🗓 Дата: {date}\n"
            f"⏰ Время: {time}"
        )

        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={"chat_id": CHAT_ID, "text": message}
            )
        except Exception as e:
            print("Ошибка при отправке уведомления в Telegram:", e)

        flash("✅ Вы успешно записались! Мы свяжемся с вами.", "success")
        return redirect(url_for("index"))

    return render_template("record.html")


# === ЗАПУСК ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

