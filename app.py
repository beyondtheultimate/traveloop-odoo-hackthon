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
    c.execute('''CREATE TABLE IF NOT EXISTS itinerary
                (id INTEGER PRIMARY KEY,
                 trip_id INTEGER,
                 city TEXT,
                 activity TEXT,
                 day TEXT,
                 cost REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS packing
                (id INTEGER PRIMARY KEY,
                 trip_id INTEGER,
                 item TEXT,
                 packed INTEGER DEFAULT 0)''')
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
@app.route('/trip/<int:trip_id>')
def trip_detail(trip_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('traveloop.db')
    c = conn.cursor()
    c.execute("SELECT * FROM trips WHERE id=?", (trip_id,))
    trip = c.fetchone()
    c.execute("SELECT * FROM itinerary WHERE trip_id=?", (trip_id,))
    itinerary = c.fetchall()
    c.execute("SELECT * FROM packing WHERE trip_id=?", (trip_id,))
    packing = c.fetchall()
    conn.close()
    return render_template('trip_detail.html', trip=trip, itinerary=itinerary, packing=packing)

@app.route('/add_itinerary/<int:trip_id>', methods=['POST'])
def add_itinerary(trip_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    city = request.form['city']
    activity = request.form['activity']
    day = request.form['day']
    cost = request.form['cost']
    conn = sqlite3.connect('traveloop.db')
    c = conn.cursor()
    c.execute("INSERT INTO itinerary (trip_id, city, activity, day, cost) VALUES (?, ?, ?, ?, ?)",
             (trip_id, city, activity, day, cost))
    conn.commit()
    conn.close()
    return redirect(url_for('trip_detail', trip_id=trip_id))

@app.route('/add_packing/<int:trip_id>', methods=['POST'])
def add_packing(trip_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    item = request.form['item']
    conn = sqlite3.connect('traveloop.db')
    c = conn.cursor()
    c.execute("INSERT INTO packing (trip_id, item) VALUES (?, ?)", (trip_id, item))
    conn.commit()
    conn.close()
    return redirect(url_for('trip_detail', trip_id=trip_id))

@app.route('/toggle_packing/<int:item_id>/<int:trip_id>')
def toggle_packing(item_id, trip_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('traveloop.db')
    c = conn.cursor()
    c.execute("SELECT packed FROM packing WHERE id=?", (item_id,))
    current = c.fetchone()[0]
    c.execute("UPDATE packing SET packed=? WHERE id=?", (1 - current, item_id))
    conn.commit()
    conn.close()
    return redirect(url_for('trip_detail', trip_id=trip_id))
@app.route('/delete_trip/<int:trip_id>')
def delete_trip(trip_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('traveloop.db')
    c = conn.cursor()
    c.execute("DELETE FROM trips WHERE id=? AND user_id=?", (trip_id, session['user_id']))
    c.execute("DELETE FROM itinerary WHERE trip_id=?", (trip_id,))
    c.execute("DELETE FROM packing WHERE trip_id=?", (trip_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))
if __name__ == '__main__':
    init_db()
    app.run(debug=True)