from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3, os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# ---------------------- БАЗА ДАЯРДОО ----------------------
def init_db():
    conn = sqlite3.connect('prices.db')
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, phone TEXT,
            effect TEXT, master TEXT,
            price TEXT,
            date TEXT, time TEXT,
            photo TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            effect TEXT,
            master TEXT,
            price INTEGER
        )
    """)
    # Эгер баа таблицасы бош болсо — демейки маалымат кошобуз
    c.execute("SELECT COUNT(*) FROM prices")
    if c.fetchone()[0] == 0:
        effects = ["Классика", "2D", "3D", "Мега Volume", "L-изгиб"]
        masters = ["Топ мастер", "Мастер", "Стажёр", "Ученица"]
        base_prices = [1800, 1500, 1200, 900]
        for e in effects:
            for i, m in enumerate(masters):
                c.execute("INSERT INTO prices (effect, master, price) VALUES (?, ?, ?)",
                          (e, m, base_prices[i] + (effects.index(e) * 200)))
    conn.commit()
    conn.close()

init_db()

# ---------------------- БАШКЫ БЕТ ----------------------
@app.route('/')
def index():
    conn = sqlite3.connect('prices.db')
    c = conn.cursor()
    clients = c.execute("SELECT * FROM clients ORDER BY id DESC").fetchall()
    prices = c.execute("SELECT effect, master, price FROM prices").fetchall()
    conn.close()
    # prices => { "Классика": {"Топ мастер": 1800, ...}, ... }
    price_dict = {}
    for e, m, p in prices:
        price_dict.setdefault(e, {})[m] = p
    return render_template('index.html', clients=clients, prices=price_dict)

# ---------------------- ЖАЗУУ КОШУУ ----------------------
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    phone = request.form['phone']
    effect = request.form['effect']
    master = request.form['master']
    price = request.form['price']
    date = request.form['date']
    time = request.form['time']

    photo = request.files['photo']
    filename = ""
    if photo and photo.filename != "":
        filename = photo.filename
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    conn = sqlite3.connect('prices.db')
    c = conn.cursor()
    c.execute("""
        INSERT INTO clients (name, phone, effect, master, price, date, time, photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, phone, effect, master, price, date, time, filename))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# ---------------------- ӨЧҮРҮҮ ----------------------
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('prices.db')
    c = conn.cursor()
    c.execute("DELETE FROM clients WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# ---------------------- БАҢЫ ЖАҢЫРТУУ (AJAX аркылуу) ----------------------
@app.route('/update_price', methods=['POST'])
def update_price():
    data = request.get_json()
    password = data.get('password')
    if password != 'admin123':
        return jsonify({'status': 'error', 'message': 'Неверный пароль!'}), 403

    effect = data['effect']
    master = data['master']
    new_price = data['price']

    conn = sqlite3.connect('prices.db')
    c = conn.cursor()
    c.execute("UPDATE prices SET price=? WHERE effect=? AND master=?", (new_price, effect, master))
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Цена обновлена!'})
    
if __name__ == '__main__':
    app.run(debug=True)