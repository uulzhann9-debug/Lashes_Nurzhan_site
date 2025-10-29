from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Папка для загрузки фото
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_FILE = "prices.db"

# ✅ Инициализация базы данных
def init_db():
    conn = sqlite3.connect(DB_FILE)
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
    conn.commit()
    conn.close()
    print("✅ База данных успешно создана или уже существует.")

init_db()

# ✅ Главная страница
@app.route('/')
def index():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT price, date, time, photo FROM prices ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()

    price, date, time, photo = ("—", "—", "—", None) if not row else row
    return render_template('index.html', price=price, date=date, time=time, photo=photo)

# ✅ Страница входа для админа
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    password = "nurzhan123"
    if request.method == "POST":
        entered_password = request.form.get("password")
        if entered_password == password:
            return redirect(url_for('edit'))
        else:
            flash("❌ Неверный пароль", "error")
    return render_template('admin.html')

# ✅ Страница изменения данных
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == "POST":
        price = request.form.get("price")
        date = request.form.get("date")
        time = request.form.get("time")
        photo = request.files.get("photo")

        filename = None
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(UPLOAD_FOLDER, filename))

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO prices (price, date, time, photo) VALUES (?, ?, ?, ?)",
                  (price, date, time, filename))
        conn.commit()
        conn.close()

        flash("✅ Данные успешно обновлены!", "success")
        return redirect(url_for('index'))

    return render_template('assign.html')

# ✅ Запуск приложения
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render использует порт 10000
    app.run(host="0.0.0.0", port=port)
