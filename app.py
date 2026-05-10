from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

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
    c.execute('''CREATE TABLE IF NOT EXISTS notes
                (id INTEGER PRIMARY KEY,
                 trip_id INTEGER,
                 note TEXT)''')
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
@app.route('/notes/<int:trip_id>', methods=['GET', 'POST'])
def notes(trip_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('traveloop.db')
    c = conn.cursor()
    if request.method == 'POST':
        note = request.form['note']
        c.execute("INSERT INTO notes (trip_id, note) VALUES (?, ?)", (trip_id, note))
        conn.commit()
    c.execute("SELECT * FROM notes WHERE trip_id=? ORDER BY id DESC", (trip_id,))
    notes = c.fetchall()
    c.execute("SELECT * FROM trips WHERE id=?", (trip_id,))
    trip = c.fetchone()
    conn.close()
    return render_template('notes.html', notes=notes, trip=trip)

@app.route('/delete_note/<int:note_id>/<int:trip_id>')
def delete_note(note_id, trip_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('traveloop.db')
    c = conn.cursor()
    c.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('notes', trip_id=trip_id))
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect('traveloop.db')
    c = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        photo = request.files.get('photo')
        if photo and photo.filename != '':
            filename = secure_filename(photo.filename)
            photo.save(os.path.join('static', filename))
            session['photo'] = filename
        c.execute("UPDATE users SET name=?, email=? WHERE id=?",
                 (name, email, session['user_id']))
        conn.commit()
        session['user_name'] = name
    c.execute("SELECT * FROM users WHERE id=?", (session['user_id'],))
    user = c.fetchone()
    conn.close()
    return render_template('profile.html', user=user, photo=session.get('photo'))
@app.route('/city_search')
def city_search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    query = request.args.get('q', '').lower()
    cities = [
        {'name': 'Paris', 'country': 'France', 'cost': '₹80,000', 'popularity': '⭐⭐⭐⭐⭐', 'emoji': '🗼'},
        {'name': 'Tokyo', 'country': 'Japan', 'cost': '₹95,000', 'popularity': '⭐⭐⭐⭐⭐', 'emoji': '🏯'},
        {'name': 'New York', 'country': 'USA', 'cost': '₹1,20,000', 'popularity': '⭐⭐⭐⭐⭐', 'emoji': '🗽'},
        {'name': 'Bali', 'country': 'Indonesia', 'cost': '₹45,000', 'popularity': '⭐⭐⭐⭐', 'emoji': '🏝️'},
        {'name': 'London', 'country': 'UK', 'cost': '₹1,10,000', 'popularity': '⭐⭐⭐⭐⭐', 'emoji': '🎡'},
        {'name': 'Dubai', 'country': 'UAE', 'cost': '₹70,000', 'popularity': '⭐⭐⭐⭐', 'emoji': '🏙️'},
        {'name': 'Singapore', 'country': 'Singapore', 'cost': '₹85,000', 'popularity': '⭐⭐⭐⭐', 'emoji': '🦁'},
        {'name': 'Rome', 'country': 'Italy', 'cost': '₹75,000', 'popularity': '⭐⭐⭐⭐', 'emoji': '🏛️'},
        {'name': 'Bangkok', 'country': 'Thailand', 'cost': '₹35,000', 'popularity': '⭐⭐⭐⭐', 'emoji': '🛕'},
        {'name': 'Sydney', 'country': 'Australia', 'cost': '₹1,00,000', 'popularity': '⭐⭐⭐⭐', 'emoji': '🦘'},
        {'name': 'Goa', 'country': 'India', 'cost': '₹15,000', 'popularity': '⭐⭐⭐⭐', 'emoji': '🏖️'},
        {'name': 'Manali', 'country': 'India', 'cost': '₹12,000', 'popularity': '⭐⭐⭐⭐', 'emoji': '🏔️'},
    ]
    if query:
        cities = [c for c in cities if query in c['name'].lower() or query in c['country'].lower()]
    return render_template('city_search.html', cities=cities, query=query)
 
 
        
if __name__ == '__main__':
    init_db()
    app.run(debug=True)