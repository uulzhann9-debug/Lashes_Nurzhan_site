from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "super_secret_key"


app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


DB_FILE = "prices.db"


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

init_db()


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



@app.route('/admin', methods=['GET', 'POST'])
def admin():
    password = "nurzhan123"  
    
    if request.method == "POST" and "login" in request.form:
        entered_password = request.form.get("password")
        if entered_password == password:
            flash("Вы вошли как админ!", "success")
            return redirect(url_for('edit'))
        else:
            flash("Неверный пароль!", "error")

    return render_template('admin.html')



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
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

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
