from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Папка для загрузки фото
app.config["UPLOAD_FOLDER"] = "static/uploads"

# Имя файла базы данных
DB_FILE = "prices.db"

# ✅ Пересоздание базы данных при запуске
def init_db():
    # Если база уже есть — удалить, чтобы создать заново
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print("🧹 Старый файл базы данных удалён")

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
    print("✅ Новая база данных успешно создана!")

# Создаём базу
init_db()

# Главная страница
@app.route('/')
def index():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT price, date, time, photo FROM prices ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()

    if row:
        price, date, time, photo = row
    else:
        price, date, time, photo = "—", "—", "—", None

    return render_template('index.html', price=price, date=date, time=time, photo=photo)

# Страница входа администратора
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    password = "nurzhan123"  # Пароль администратора
    
    if request.method == "POST" and "login" in request.form:
        entered_password = request.form.get("password")
        if entered_password == password:
            flash("Вы вошли как админ!", "success")
            return redirect(url_for('edit'))
        else:
            flash("Неверный пароль!", "error")

    return render_template('admin.html')

# Страница редактирования данных
@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if request.method == "POST":
        price = request.form.get("price")
        date = request.form.get("date")
        time = request.form.get("time")
        photo = request.files.get("photo")

        filename = None
        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            upload_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

            # Создаём папку, если нет
            if not os.path.exists(app.config["UPLOAD_FOLDER"]):
                os.makedirs(app.config["UPLOAD_FOLDER"])
            photo.save(upload_path)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO prices (price, date, time, photo) VALUES (?, ?, ?, ?)",
                  (price, date, time, filename))
        conn.commit()
        conn.close()

        flash("Данные успешно обновлены!", "success")
        return redirect(url_for('index'))

    return render_template('assign.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
