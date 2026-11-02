# PARCELGUARD - IoT-Based Smart Parcel Weight Verification System

[![Live on Render](https://img.shields.io/badge/Render-Live%20Dashboard-brightgreen?style=for-the-badge&logo=render)](https://smartparcel-tcf5.onrender.com/)

> 🌐 **Live Web Application:** [https://smartparcel-tcf5.onrender.com/](https://smartparcel-tcf5.onrender.com/)

PARCELGUARD is an automated IoT parcel verification system that combines an ESP32 load cell weight station with a FastAPI cloud backend and an interactive real-time web dashboard.

## 🚀 Live Deployment
- **Cloud Dashboard:** [https://smartparcel-tcf5.onrender.com/](https://smartparcel-tcf5.onrender.com/)
- **ESP32 Ingestion Endpoint:** `https://smartparcel-tcf5.onrender.com/api/sensor`
- **Health Check:** [https://smartparcel-tcf5.onrender.com/api/health](https://smartparcel-tcf5.onrender.com/api/health)
- **API Documentation (Swagger):** [https://smartparcel-tcf5.onrender.com/docs](https://smartparcel-tcf5.onrender.com/docs)
- **Database:** Hosted PostgreSQL on Render

---

## 📦 Features
- **Accurate Real-Time Weight Sensing:** HX711 24-bit ADC and load cell interfaced with ESP32.
- **Dual Cloud & Local Support:**
  - **Render Cloud:** Uses PostgreSQL (`psycopg2` / `SQLAlchemy`) and secure HTTPS with TLS/SSL.
  - **Local Host:** Runs in Docker or Python with SQLite.
- **Audio & Voice Feedback:** In-browser speech synthesis and audio chime alerts for parcel verification (Match, Underweight, Overweight).
- **Interactive Chart & Measurement History:** Real-time dynamic weight line chart and paginated measurement table.
- **Configurable Settings:** Adjustable target parcel weight and tolerance with live verification.

---

## 🛠️ Hardware Setup
### Components
- ESP32 Development Board
- HX711 Load Cell Amplifier
- 1kg / 5kg / 10kg Load Cell & platform
- Jumper wires & USB cable

### Pin Connections
| HX711 Pin | ESP32 GPIO |
| :--- | :--- |
| **VCC** | `3V3` or `5V` |
| **GND** | `GND` |
| **DT (Data)** | `GPIO 4` |
| **SCK (Clock)** | `GPIO 5` |

---

## 💻 ESP32 Firmware Setup (Arduino IDE)
1. Install the **HX711** library by Bogdan Necula in Arduino IDE (`Sketch -> Include Library -> Manage Libraries`).
2. Open [`esp32/SmartParcel_ESP32.ino`](esp32/SmartParcel_ESP32.ino).
3. Verify your Wi-Fi credentials:
   ```cpp
   const char* WIFI_SSID = "your_wifi_or_hotspot_name";
   const char* WIFI_PASSWORD = "your_wifi_password";
   ```
4. For cloud deployment on Render:
   ```cpp
   const char* SERVER_URL = "https://smartparcel-tcf5.onrender.com/api/sensor";
   ```
   *(For local testing, use `http://<your-laptop-ip>:8000/api/sensor`)*.
5. Set your board to **ESP32 Dev Module** and baud rate to **115200**.
6. Upload the code and verify the Serial Monitor logs.

---

## 🐳 Local Docker Deployment
To run the backend and dashboard locally:
```bash
docker compose up -d --build
```
Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 📡 API Endpoints
- `POST /api/sensor`: Ingests live sensor readings (`actual_weight_g`, `source`).
- `GET /api/dashboard`: Fetches the latest reading, current verification settings, and measurement history.
- `GET /api/settings` & `PUT /api/settings`: Read and update target weight and allowed tolerance.
- `GET /api/history`: Returns historical weight readings.
- `GET /api/health`: Service health and active database type.
