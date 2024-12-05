import flask
from flask import *
import re
import sqlite3
from datetime import datetime
import os
from sqlite3 import Error
import threading
import paho.mqtt.client as mqtt

app = flask.Flask(__name__)
app.config["DEBUG"] = True

app.secret_key = 'cheesylasagna'

# MQTT settings
BROKER = "192.168.143.12"  # Use "localhost" or the IP of your MQTT broker
PORT = 1883
TOPIC = "iot/sensor_data"

HISTORICAL_DATA_DIR = 'historical_data'

# Global variable for live sensor data
sensor_data = {'temperature': 'N/A', 'humidity': 'N/A'}


# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(TOPIC)


def on_message(client, userdata, msg):
    global sensor_data
    try:
        data = msg.payload.decode().split(',')
        # Remove unwanted characters like brackets
        sensor_data['temperature'] = data[0].strip("[]")
        sensor_data['humidity'] = data[1].strip("[]")
        print(f"Received data - Temperature: {sensor_data['temperature']}, Humidity: {sensor_data['humidity']}")

        # Save data to a daily historical data file
        date_str = datetime.now().strftime('%Y-%m-%d')
        filename = os.path.join(HISTORICAL_DATA_DIR, f"{date_str}.txt")
        with open(filename, "a") as file:
            file.write(f"{sensor_data['temperature']},{sensor_data['humidity']}\n")
    except Exception as e:
        print(f"Error processing MQTT message: {e}")




# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, PORT, keepalive=60)


# Run MQTT client in a separate thread
def start_mqtt_client():
    mqtt_client.loop_forever()


mqtt_thread = threading.Thread(target=start_mqtt_client)
mqtt_thread.daemon = True
mqtt_thread.start()


# SQLite database connection function
def create_connection(db_file):
    """Create a database connection to a SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn


def create_user_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS user (
                    userid INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL
                )
            ''')
        conn.commit()
    except Error as e:
        print(e)


# Flask routes
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = create_connection(r"TempDataHumidMoist.db")
    create_user_table(conn)
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user[0]
            session['name'] = user[1]
            session['email'] = user[2]
            message = 'Logged in successfully!'
            return render_template('index.html', message=message)
        else:
            message = 'Please enter correct email / password!'
    if conn:
        conn.close()
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    conn = create_connection(r"TempDataHumidMoist.db")
    create_user_table(conn)
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE email = ?', (email,))
        account = cursor.fetchone()
        if account:
            message = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not userName or not password or not email:
            message = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO user (name, email, password) VALUES (?, ?, ?)', (userName, email, password))
            conn.commit()
            message = 'You have successfully registered!'
    elif request.method == 'POST':
        message = 'Please fill out the form!'
    if conn:
        conn.close()
    return render_template('register.html', message=message)


@app.route('/home', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/historical_data')
def historical_data():
    files = os.listdir(HISTORICAL_DATA_DIR)
    files.sort(reverse=True)  # Sort files by date (newest first)
    return render_template('historical_data.html', files=files)


@app.route('/view_historical/<filename>')
def view_historical(filename):
    filepath = os.path.join(HISTORICAL_DATA_DIR, filename)
    data = []
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            for line in file:
                temperature, humidity = line.strip().split(',')
                data.append({'temperature': temperature, 'humidity': humidity})
    return render_template('view_historical.html', data=data, filename=filename)

# Route to serve the live_data.html page
@app.route('/live_data')
def live_data_page():
    return render_template('live_data.html')

# API route to provide live data as JSON
@app.route('/live_data_api')
def live_data_api():
    # Return the live data (ensure this is your sensor data structure)
    return jsonify(sensor_data)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
