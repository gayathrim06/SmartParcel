#include <WiFi.h>
#include <HTTPClient.h>
#include "HX711.h"

// Enter the same Wi-Fi network used by your laptop.
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";

// Replace with your laptop Wi-Fi IPv4 address from ipconfig.
// Do not use localhost or 127.0.0.1.
const char* SERVER_URL = "http://192.168.1.100:8000/api/sensor";

#define DT_PIN 4
#define SCK_PIN 5
HX711 scale;

// Preserve your calibrated factor: 400 g test previously read about 0.400 kg.
float calibration_factor = -138138.0;
unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL_MS = 1000;

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("\nWi-Fi connected");
  Serial.print("ESP32 IP: "); Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\nSMART PARCEL - LIVE SENSOR");
  Serial.println("Keep platform EMPTY during startup tare.");
  scale.begin(DT_PIN, SCK_PIN);
  delay(1500);
  if (!scale.is_ready()) {
    Serial.println("ERROR: HX711 not detected. Check wiring.");
    while (true) delay(1000);
  }
  scale.set_scale(calibration_factor);
  scale.tare(20);
  Serial.println("HX711 ready. Zero calibration complete.");
  connectWiFi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) connectWiFi();

  if (millis() - lastSend >= SEND_INTERVAL_MS) {
    lastSend = millis();
    if (!scale.is_ready()) { Serial.println("HX711 not ready; no reading sent."); return; }

    // Existing factor returns kg; API expects grams.
    float weightKg = scale.get_units(5);
    float weightGrams = weightKg * 1000.0;
    if (weightGrams > -2.0 && weightGrams < 2.0) weightGrams = 0.0;

    Serial.print("Live weight: "); Serial.print(weightGrams, 1); Serial.println(" g");

    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(3000);
    String body = "{\"actual_weight_g\":" + String(weightGrams, 2) +
                  ",\"source\":\"ESP32\"}";
    int code = http.POST(body);
    Serial.print("Dashboard API response: "); Serial.println(code);
    if (code > 0) Serial.println(http.getString());
    else Serial.println("API unreachable: check laptop IP, Docker, Wi-Fi and firewall.");
    http.end();
  }
}
