from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from datetime import datetime
import psycopg2
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database setup (for Heroku PostgreSQL)
def get_db_connection():
    # Get DATABASE_URL from Heroku environment or use a default for local testing
    database_url = os.environ.get('DATABASE_URL', '')
    
    if database_url:
        # Parse the database URL
        result = urlparse(database_url)
        # Connect to the database
        conn = psycopg2.connect(
            dbname=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        return conn
    else:
        # For local development - use a file to store data
        return None

# Initialize database table if it doesn't exist
def init_db():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Create table for sensor data
            cur.execute('''
                CREATE TABLE IF NOT EXISTS sensor_data (
                    id SERIAL PRIMARY KEY,
                    device_id VARCHAR(50) NOT NULL,
                    temperature FLOAT,
                    humidity FLOAT,
                    flow_rate FLOAT,
                    flow_direction INT,
                    latitude FLOAT,
                    longitude FLOAT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            cur.close()
        except Exception as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()
    else:
        # For local development, ensure data directory exists
        if not os.path.exists('data'):
            os.makedirs('data')

# Save data to database or file system
def save_data(data):
    device_id = data.get('device_id', 'unknown')
    conn = get_db_connection()
    
    if conn:
        try:
            cur = conn.cursor()
            # Insert data into PostgreSQL
            cur.execute(
                '''INSERT INTO sensor_data 
                   (device_id, temperature, humidity, flow_rate, flow_direction, latitude, longitude) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                (device_id, 
                 data.get('temperature'), 
                 data.get('humidity'), 
                 data.get('flow_rate'), 
                 data.get('flow_direction'), 
                 data.get('latitude'), 
                 data.get('longitude'))
            )
            conn.commit()
            cur.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False
    else:
        # Store in file system (fallback for local development)
        timestamp = datetime.now().isoformat()
        filename = f"data/{device_id}_{timestamp.replace(':', '-')}.json"
        try:
            with open(filename, 'w') as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"File system error: {e}")
            return False

def before_first_request():
    init_db()

before_first_request()

# API endpoint to receive sensor data
@app.route('/api/sensor-data', methods=['POST'])
def receive_sensor_data():
    data = request.get_json()  # Get data in JSON format
    
    # Validate required fields
    required_fields = ['device_id', 'temperature', 'humidity', 'flow_rate']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Save data
    if save_data(data):
        return jsonify({
            "message": "Data received successfully",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }), 200
    else:
        return jsonify({"error": "Failed to save data"}), 500

# API endpoint to get the latest data for a specific device
@app.route('/api/sensor-data/<device_id>', methods=['GET'])
def get_latest_data(device_id):
    conn = get_db_connection()
    
    if conn:
        try:
            cur = conn.cursor()
            cur.execute(
                '''SELECT temperature, humidity, flow_rate, flow_direction, 
                   latitude, longitude, timestamp 
                   FROM sensor_data 
                   WHERE device_id = %s 
                   ORDER BY timestamp DESC 
                   LIMIT 1''', 
                (device_id,)
            )
            row = cur.fetchone()
            
            if row:
                data = {
                    "device_id": device_id,
                    "temperature": row[0],
                    "humidity": row[1],
                    "flow_rate": row[2],
                    "flow_direction": row[3],
                    "latitude": row[4],
                    "longitude": row[5],
                    "timestamp": row[6].isoformat()
                }
                return jsonify(data), 200
            else:
                return jsonify({"error": "No data found for device"}), 404
        except Exception as e:
            print(f"Database query error: {e}")
            return jsonify({"error": "Database error"}), 500
        finally:
            conn.close()
    else:
        # Fallback to file system for local development
        try:
            # List all files for this device and find the most recent
            device_files = [f for f in os.listdir('data') if f.startswith(f"{device_id}_")]
            if not device_files:
                return jsonify({"error": "No data found for device"}), 404
                
            latest_file = max(device_files)
            with open(f"data/{latest_file}", 'r') as f:
                data = json.load(f)
                return jsonify(data), 200
        except Exception as e:
            print(f"File system error: {e}")
            return jsonify({"error": "Error retrieving data"}), 500

# Basic health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

if __name__ == '__main__':
    # Use port provided by Heroku or default to 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)