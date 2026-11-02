SMARTPARCEL LIVE IOT SYSTEM

LIVE RENDER CLOUD URL:
https://smartparcel-tcf5.onrender.com/

WHAT IT DOES
- ESP32 + HX711 sends actual measured weight to FastAPI every second over Wi-Fi.
- Dashboard updates automatically, plots a graph, and shows recent samples.
- You enter only expected parcel weight and tolerance; never actual weight.
- Status: NO PARCEL, UNDERWEIGHT, MATCH, or OVERWEIGHT.
- Browser voice + beep alert on transition into UNDERWEIGHT or OVERWEIGHT.
- SQLite database is created automatically by main.py; do not create it manually.

DEFAULT RULE
Expected 400 g, tolerance 5 g:
<= 5 g: NO PARCEL
below 395 g: UNDERWEIGHT
395–405 g inclusive: MATCH
above 405 g: OVERWEIGHT

INSTALL
1. Back up your current SmartParcel folder.
2. Replace project main.py with this package's main.py.
3. Replace static/index.html with this package's static/index.html.
4. Keep your current Dockerfile and docker-compose.yml for now.
5. Make sure docker-compose maps host port 8000 to container port 8000.
6. Run from the project folder: docker compose up -d --build
7. Open http://localhost:8000 and press Ctrl+F5.

ESP32
1. Keep wiring: HX711 VCC->3V3, GND->GND, DT->GPIO4/D4, SCK->GPIO5/D5.
2. Keep calibration factor -138138.0; do not change it without recalibrating.
3. Keep the weighing platform empty when ESP32 starts; code runs tare().
4. Connect laptop and ESP32 to the SAME Wi-Fi network.
5. In PowerShell run: ipconfig. Find Wi-Fi adapter's IPv4 Address.
6. In esp32/SmartParcel_ESP32.ino replace 192.168.1.100 with that IPv4 address.
7. Replace YOUR_WIFI_NAME and YOUR_WIFI_PASSWORD.
8. Upload to ESP32. Open Serial Monitor at 115200 baud.
9. Expect HTTP response 200 in Serial Monitor when the laptop API receives data.

IMPORTANT: ESP32 MUST NOT use localhost. Use laptop's LAN IPv4 address.
If Windows Firewall asks, allow communication on your Private network.

DATABASE PERSISTENCE IN DOCKER
Database auto-creates at data/parcel.db inside the app by default. To preserve it
when the container is recreated, merge the following into the existing app service
in docker-compose.yml (assuming Dockerfile WORKDIR is /app):

environment:
  DB_PATH: /app/data/parcel.db
volumes:
  - ./data:/app/data

Keep the existing port mapping 8000:8000. Do not replace the whole compose file
without checking its current contents.

VOICE ALERTS
Open dashboard, click "Enable voice and alarm" once, keep tab open, and keep laptop
volume audible. Browser speech requires a user click; closed tab/sleeping laptop
cannot reliably announce alerts. Alert is spoken when status changes into under/
overweight, not every one-second sample.

TEST
Set expected 400 g and tolerance 5 g. Place the known 400 g test object and confirm
dashboard shows approximately 400 g and MATCH. Then test a lighter/heavier object.
The physical scale's accuracy depends on stable mounting and calibration.
