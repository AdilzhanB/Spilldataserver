# Spilldataserver - Environmental Sensor Data Collection Server

A Flask-based REST API server for collecting and managing environmental sensor data, specifically designed for oil spill monitoring systems. The server supports both PostgreSQL database storage (for production) and local file system storage (for development).

## 🎯 Overview

The Spilldataserver is designed to:
- Collect sensor data from multiple IoT devices
- Store environmental monitoring data (temperature, humidity, flow rate, GPS coordinates)
- Provide RESTful API access to sensor data
- Support both cloud database and local file storage
- Enable real-time monitoring of environmental conditions

## 🚀 Features

### Data Collection
- **Multi-device Support**: Handle data from multiple sensor devices
- **Environmental Monitoring**: Temperature, humidity, water flow measurements
- **GPS Tracking**: Latitude and longitude positioning
- **Timestamping**: Automatic timestamp recording for all data points

### Storage Options
- **PostgreSQL Database**: Production-ready database storage
- **File System Fallback**: Local JSON file storage for development
- **Automatic Failover**: Falls back to file storage if database unavailable

### API Capabilities
- **RESTful Design**: Standard HTTP methods and status codes
- **JSON Data Format**: Easy integration with various client systems
- **CORS Support**: Cross-origin requests enabled
- **Health Monitoring**: Built-in health check endpoint

## 📋 Requirements

- Python 3.7+
- Flask for web framework
- PostgreSQL for production database
- psycopg2 for PostgreSQL connectivity

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/AdilzhanB/Spilldataserver.git
   cd Spilldataserver
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up database (Production)**
   ```bash
   # Set PostgreSQL connection URL
   export DATABASE_URL="postgresql://username:password@hostname:port/database"
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | No | None (uses file storage) |
| `PORT` | Server port | No | `5000` |

### Database Schema

The server automatically creates the following table structure:

```sql
CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) NOT NULL,
    temperature FLOAT,
    humidity FLOAT,
    flow_rate FLOAT,
    flow_direction VARCHAR(50) NOT NULL,
    latitude FLOAT,
    longitude FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Directory Structure
```
Spilldataserver/
├── app.py                 # Main application file
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── data/                 # Auto-created directory for local file storage
    └── {device_id}_{timestamp}.json
```

## 📡 API Documentation

### Data Collection

#### `POST /api/sensor-data`
Submit sensor data from IoT devices

**Request Body:**
```json
{
  "device_id": "sensor_001",
  "temperature": 23.5,
  "humidity": 65.2,
  "flow_rate": 12.8,
  "flow_direction": "north",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

**Required Fields:**
- `device_id`: Unique identifier for the sensor device
- `temperature`: Temperature reading (°C)
- `humidity`: Humidity percentage
- `flow_rate`: Water flow rate (units depend on sensor)

**Optional Fields:**
- `flow_direction`: Direction of water flow
- `latitude`: GPS latitude coordinate
- `longitude`: GPS longitude coordinate

**Response (Success):**
```json
{
  "message": "Data received successfully",
  "timestamp": "2023-06-22T16:39:11.123456",
  "data": {
    "device_id": "sensor_001",
    "temperature": 23.5,
    "humidity": 65.2,
    "flow_rate": 12.8,
    "flow_direction": "north",
    "latitude": 40.7128,
    "longitude": -74.0060
  }
}
```

**Response (Error):**
```json
{
  "error": "Missing required fields"
}
```

### Data Retrieval

#### `GET /api/sensor-data/{device_id}`
Get the latest sensor data for a specific device

**Parameters:**
- `device_id`: The unique identifier of the sensor device

**Response (Success):**
```json
{
  "device_id": "sensor_001",
  "temperature": 23.5,
  "humidity": 65.2,
  "flow_rate": 12.8,
  "flow_direction": "north",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "timestamp": "2023-06-22T16:39:11.123456"
}
```

**Response (Not Found):**
```json
{
  "error": "No data found for device"
}
```

### System Health

#### `GET /health`
Check server health and status

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-06-22T16:39:11.123456"
}
```

## 🔍 Usage Examples

### Submitting Sensor Data
```python
import requests
import json

# Sensor data
data = {
    "device_id": "marine_sensor_01",
    "temperature": 18.5,
    "humidity": 78.3,
    "flow_rate": 15.2,
    "flow_direction": "southeast",
    "latitude": 59.3293,
    "longitude": 18.0686
}

# Submit data
response = requests.post(
    'http://localhost:5000/api/sensor-data',
    json=data,
    headers={'Content-Type': 'application/json'}
)

if response.status_code == 200:
    print("Data submitted successfully")
    print(response.json())
else:
    print(f"Error: {response.status_code}")
    print(response.json())
```

### Retrieving Latest Data
```python
import requests

device_id = "marine_sensor_01"
response = requests.get(f'http://localhost:5000/api/sensor-data/{device_id}')

if response.status_code == 200:
    data = response.json()
    print(f"Latest data for {device_id}:")
    print(f"Temperature: {data['temperature']}°C")
    print(f"Humidity: {data['humidity']}%")
    print(f"Flow Rate: {data['flow_rate']}")
    print(f"Recorded: {data['timestamp']}")
else:
    print(f"Error retrieving data: {response.json()}")
```

### Health Check
```python
import requests

response = requests.get('http://localhost:5000/health')
health_status = response.json()
print(f"Server status: {health_status['status']}")
```

## 🗄️ Storage Modes

### PostgreSQL Database (Production)
- **Advantages**: Scalable, ACID compliant, concurrent access
- **Configuration**: Set `DATABASE_URL` environment variable
- **Use Case**: Production deployments, multiple clients

### File System Storage (Development)
- **Advantages**: No database setup required, easy debugging
- **Configuration**: No `DATABASE_URL` set
- **Use Case**: Local development, testing, single-device scenarios

### Automatic Failover
The server automatically detects database availability and falls back to file storage if needed.

## 🚀 Deployment

### Local Development
```bash
# Without database (file storage)
python app.py

# With PostgreSQL
export DATABASE_URL="postgresql://user:pass@localhost/spilldata"
python app.py
```

### Heroku Deployment
```bash
# Create Heroku app
heroku create your-spilldata-server

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p data

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "app.py"]
```

### Production with Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔧 Integration Examples

### Arduino/ESP32 Integration
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

void sendSensorData() {
    HTTPClient http;
    http.begin("http://your-server.com/api/sensor-data");
    http.addHeader("Content-Type", "application/json");
    
    // Create JSON payload
    DynamicJsonDocument doc(1024);
    doc["device_id"] = "esp32_001";
    doc["temperature"] = 25.3;
    doc["humidity"] = 60.5;
    doc["flow_rate"] = 10.2;
    doc["latitude"] = 59.3293;
    doc["longitude"] = 18.0686;
    
    String payload;
    serializeJson(doc, payload);
    
    int httpResponseCode = http.POST(payload);
    
    if (httpResponseCode == 200) {
        Serial.println("Data sent successfully");
    } else {
        Serial.printf("Error: %d\n", httpResponseCode);
    }
    
    http.end();
}
```

### Raspberry Pi Integration
```python
import requests
import time
import random

def simulate_sensor_reading():
    return {
        "device_id": "rpi_sensor_02",
        "temperature": round(random.uniform(15.0, 30.0), 2),
        "humidity": round(random.uniform(40.0, 90.0), 2),
        "flow_rate": round(random.uniform(5.0, 20.0), 2),
        "flow_direction": "north",
        "latitude": 59.3293,
        "longitude": 18.0686
    }

def send_data():
    data = simulate_sensor_reading()
    response = requests.post(
        'http://localhost:5000/api/sensor-data',
        json=data
    )
    return response.status_code == 200

# Send data every 30 seconds
while True:
    if send_data():
        print("Data sent successfully")
    else:
        print("Failed to send data")
    time.sleep(30)
```

## 📊 Monitoring and Maintenance

### Database Monitoring
```sql
-- Check recent data entries
SELECT device_id, temperature, humidity, timestamp 
FROM sensor_data 
ORDER BY timestamp DESC 
LIMIT 10;

-- Count entries per device
SELECT device_id, COUNT(*) as entry_count 
FROM sensor_data 
GROUP BY device_id;

-- Average readings by device
SELECT 
    device_id,
    AVG(temperature) as avg_temp,
    AVG(humidity) as avg_humidity,
    AVG(flow_rate) as avg_flow
FROM sensor_data 
GROUP BY device_id;
```

### File System Monitoring
```bash
# Check stored files
ls -la data/

# Count files per device
ls data/ | cut -d'_' -f1 | sort | uniq -c

# Check disk usage
du -sh data/
```

## 🔧 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check `DATABASE_URL` format
   - Verify database server is running
   - Server automatically falls back to file storage

2. **Missing Required Fields (400)**
   - Ensure all required fields are included in request
   - Check JSON format and field names

3. **No Data Found (404)**
   - Verify device_id exists in system
   - Check if data has been submitted for the device

4. **File Permission Errors**
   - Ensure write permissions for `data/` directory
   - Check disk space availability

### Debug Mode
```bash
# Enable Flask debug mode for development
export FLASK_DEBUG=1
python app.py
```

## 🛡️ Security Considerations

### Recommendations
- Use HTTPS in production environments
- Implement API authentication for sensitive deployments
- Validate and sanitize input data
- Monitor for unusual data patterns
- Implement rate limiting for high-traffic scenarios

### Database Security
- Use strong database passwords
- Enable SSL connections for database
- Regularly backup sensor data
- Implement proper user access controls

## 🚀 Performance Optimization

### Database Optimization
```sql
-- Add indexes for better query performance
CREATE INDEX idx_sensor_device_timestamp ON sensor_data(device_id, timestamp DESC);
CREATE INDEX idx_sensor_timestamp ON sensor_data(timestamp DESC);
```

### Application Optimization
- Use connection pooling for database connections
- Implement caching for frequently accessed data
- Consider data archiving for old entries
- Monitor memory usage with large datasets

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/new-feature`)
7. Create a Pull Request

## 📄 License

This project is open source. Please add an appropriate license file.

## 📞 Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review the API documentation

---

**Note**: This server is designed to work with the Videostream application and other components of the oil spill monitoring system. Ensure proper network connectivity and data flow between all system components.
