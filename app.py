from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, get_db
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Inicializa la base de datos
init_db()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']
            return redirect(url_for('index'))
        return 'Invalid username or password'
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = request.form.get('is_admin') == 'on'
        db = get_db()
        db.execute('INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)',
                   (username, generate_password_hash(password), is_admin))
        db.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/search_rooms', methods=['POST'])
def search_rooms():
    check_in = request.form.get('check_in')
    check_out = request.form.get('check_out')
    
    db = get_db()
    
    # Buscar habitaciones no disponibles en el rango de fechas
    query = '''
    SELECT * FROM rooms WHERE id NOT IN (
        SELECT room_id FROM reservations 
        WHERE NOT (check_out <= ? OR check_in >= ?)
    )
    '''
    cursor = db.execute(query, (check_in, check_out))
    rooms = cursor.fetchall()

    return jsonify([dict(room) for room in rooms])


@app.route('/make_reservation', methods=['POST'])
def make_reservation():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    room_id = request.form['room_id']
    check_in = request.form['check_in']
    check_out = request.form['check_out']
    db = get_db()

    room = db.execute('SELECT * FROM rooms WHERE id = ?', (room_id,)).fetchone()

    # Cálculo de costo con impuestos
    days = (datetime.strptime(check_out, '%Y-%m-%d') - datetime.strptime(check_in, '%Y-%m-%d')).days
    total_cost = room['price'] * days
    tax = total_cost * 0.1
    total_cost_with_tax = total_cost + tax

    # Crear una nueva reserva
    db.execute('INSERT INTO reservations (user_id, room_id, check_in, check_out, total_cost) VALUES (?, ?, ?, ?, ?)',
               (session['user_id'], room_id, check_in, check_out, total_cost_with_tax))
    db.commit()

    return jsonify({'success': True, 'total_cost': total_cost_with_tax})


if __name__ == '__main__':
    app.run(debug=True)
