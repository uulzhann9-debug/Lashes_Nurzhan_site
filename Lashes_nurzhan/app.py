from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from datetime import datetime
import json
import requests

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['DATA_FILE'] = 'data.json'

# 🔹 Твой Telegram токен и ID (замени на свои)
BOT_TOKEN = "8418858503:AAFhK6EZxsDgfF4E839xlOgAkWaKiKKV27U"
ADMIN_CHAT_ID = "7541525471"  # твой Telegram ID

# 🔹 Начальные цены
prices = {
    "Классика": {"Топ мастер": 1500, "Мастер": 1300, "Стажёр": 1000, "Ученица": 800},
    "2D": {"Топ мастер": 1700, "Мастер": 1500, "Стажёр": 1200, "Ученица": 1000},
    "3D": {"Топ мастер": 1900, "Мастер": 1700, "Стажёр": 1300, "Ученица": 1100},
    "Лучики": {"Топ мастер": 1600, "Мастер": 1400, "Стажёр": 1100, "Ученица": 900},
    "Мокрый": {"Топ мастер": 1800, "Мастер": 1600, "Стажёр": 1300, "Ученица": 1100},
    "Лисий": {"Топ мастер": 1700, "Мастер": 1500, "Стажёр": 1200, "Ученица": 1000},
    "Кукольный": {"Топ мастер": 1800, "Мастер": 1600, "Стажёр": 1300, "Ученица": 1100}
}

# 🔹 Загружаем данные (если есть)
if os.path.exists(app.config['DATA_FILE']):
    with open(app.config['DATA_FILE'], 'r', encoding='utf-8') as f:
        records = json.load(f)
else:
    records = []


# 📩 Функция для уведомлений в Telegram
def send_telegram_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": ADMIN_CHAT_ID, "text": text}
        requests.post(url, json=payload)
    except Exception as e:
        print("Ошибка отправки Telegram:", e)


# 🏠 Главная страница
@app.route('/')
def index():
    return render_template('index.html', prices=prices)


# 🧾 Добавление записи
@app.route('/add', methods=['POST'])
def add_record():
    name = request.form['name']
    phone = request.form['phone']
    effect = request.form['effect']
    master = request.form['master']
    date = request.form['date']
    time = request.form['time']
    price = request.form.get('price', '—')

    # Фото (если загружено)
    photo = None
    if 'photo' in request.files and request.files['photo'].filename != '':
        file = request.files['photo']
        filename = datetime.now().strftime("%Y%m%d%H%M%S_") + file.filename
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        photo = filename

    new_record = {
        "id": len(records) + 1,
        "name": name,
        "phone": phone,
        "effect": effect,
        "master": master,
        "price": price,
        "date": date,
        "time": time,
        "photo": photo,
        "status": "Новая"
    }

    records.append(new_record)

    # Сохраняем
    with open(app.config['DATA_FILE'], 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    # Отправляем уведомление
    msg = f"💅 Новая запись!\n\nИмя: {name}\nТелефон: {phone}\nЭффект: {effect}\nМастер: {master}\nЦена: {price}\nДата: {date}\nВремя: {time}"
    send_telegram_message(msg)

    return redirect(url_for('index'))


# 🧍 Страница администратора
@app.route('/admin')
def admin_page():
    return render_template('admin.html', prices=prices)


# 📋 Список всех записей
@app.route('/assign')
def assign_page():
    return render_template('assign.html', records=records)


# ✏️ Обновление цены (только для администратора)
@app.route('/update_price', methods=['POST'])
def update_price():
    data = request.get_json()
    effect = data.get('effect')
    master = data.get('master')
    new_price = data.get('price')
    password = data.get('password')

    if password != "admin123":
        return jsonify({"status": "error", "message": "Неверный пароль!"})

    try:
        prices[effect][master] = int(new_price)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


# ✅ Подтвердить запись
@app.route('/confirm/<int:record_id>', methods=['POST'])
def confirm_record(record_id):
    for r in records:
        if r['id'] == record_id:
            r['status'] = 'Подтверждена'
            with open(app.config['DATA_FILE'], 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            send_telegram_message(f"✅ Подтверждена запись клиента: {r['name']} на {r['date']} {r['time']}")
            break
    return redirect(url_for('assign_page'))


# ❌ Отменить запись
@app.route('/cancel/<int:record_id>', methods=['POST'])
def cancel_record(record_id):
    for r in records:
        if r['id'] == record_id:
            r['status'] = 'Отменена'
            with open(app.config['DATA_FILE'], 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            send_telegram_message(f"❌ Отменена запись клиента: {r['name']} ({r['phone']})")
            break
    return redirect(url_for('assign_page'))


if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
