from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'traveloop123'

def init_db():
    conn = sqlite3.connect('traveloop.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                (id INTEGER PRIMARY KEY, 
                 name TEXT, 
                 email TEXT UNIQUE, 
                 password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS trips
                (id INTEGER PRIMARY KEY,
                 user_id INTEGER,
                 name TEXT,
                 start_date TEXT,
                 end_date TEXT,
                 description TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('traveloop.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid email or password!')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('traveloop.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                     (name, email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except:
            conn.close()
            return render_template('signup.html', error='Email already exists!')
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('traveloop.db')
    c = conn.cursor()
    c.execute("SELECT * FROM trips WHERE user_id=?", (session['user_id'],))
    trips = c.fetchall()
    conn.close()
    return render_template('dashboard.html', trips=trips, name=session['user_name'])

@app.route('/create_trip', methods=['GET', 'POST'])
def create_trip():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        description = request.form['description']
        conn = sqlite3.connect('traveloop.db')
        c = conn.cursor()
        c.execute("INSERT INTO trips (user_id, name, start_date, end_date, description) VALUES (?, ?, ?, ?, ?)",
                 (session['user_id'], name, start_date, end_date, description))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('create_trip.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)