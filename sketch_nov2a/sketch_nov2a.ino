#include "HX711.h"
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>

// ==========================================
// PARCELGUARD - SMART PARCEL WEIGHT SYSTEM
// ==========================================

// WIFI SETTINGS
const char* ssid = "moto edge 60 pro_1842";
const char* password = "12345678";

// RENDER CLOUD BACKEND
const char* serverURL =
"https://smartparcel-tcf5.onrender.com/api/sensor";

// HX711 PINS
#define DT 4
#define SCK 5

HX711 scale;

// CORRECTED CALIBRATION FACTOR
float calibration_factor = -432.04;

// ==========================================
// SETUP
// ==========================================

void setup() {

  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("================================");
  Serial.println("       PARCELGUARD SYSTEM");
  Serial.println("================================");

  // Initialize HX711
  scale.begin(DT, SCK);

  Serial.println("Initializing HX711...");

  while (!scale.is_ready()) {
    Serial.println("Waiting for HX711...");
    delay(1000);
  }

  Serial.println("HX711 READY!");

  // Apply calibration
  scale.set_scale(calibration_factor);

  // Zero the empty platform
  Serial.println("Taring scale...");
  scale.tare();

  Serial.println("Calibration completed!");

  // Connect WiFi
  Serial.println("Connecting to WiFi...");

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi Connected!");

  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());

  Serial.println("PARCELGUARD READY!");
}

// ==========================================
// MAIN LOOP
// ==========================================

void loop() {

  if (!scale.is_ready()) {
    Serial.println("HX711 NOT READY!");
    delay(1000);
    return;
  }

  // Read weight in grams
  float weightGrams = scale.get_units(10);

  // Prevent negative readings
  if (weightGrams < 0) {
    weightGrams = 0;
  }

  Serial.println("--------------------------------");

  Serial.print("LIVE WEIGHT: ");
  Serial.print(weightGrams, 2);
  Serial.println(" g");

  // Check WiFi
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi Disconnected!");
    WiFi.reconnect();
    delay(1000);
    return;
  }

  // Send data to Render backend over HTTPS
  WiFiClientSecure client;
  client.setInsecure(); // Required for HTTPS connection

  HTTPClient http;
  http.setTimeout(30000); // 30s timeout for Render free tier

  if (http.begin(client, serverURL)) {

    http.addHeader("Content-Type", "application/json");
    http.addHeader("Connection", "close");

    String jsonData = "{";
    jsonData += "\"actual_weight_g\":";
    jsonData += String(weightGrams, 2);
    jsonData += ",";
    jsonData += "\"source\":\"ESP32\"";
    jsonData += "}";

    Serial.println("Sending data to Render cloud...");

    int responseCode = http.POST(jsonData);

    Serial.print("HTTP Response Code: ");
    Serial.println(responseCode);

    if (responseCode > 0) {

      String response = http.getString();

      Serial.print("Server Response: ");
      Serial.println(response);

      if (responseCode == 200 || responseCode == 201) {
        Serial.println("DATA SENT TO RENDER SUCCESSFULLY!");
      }

    } else {

      Serial.println("SERVER CONNECTION FAILED!");
      Serial.println(http.errorToString(responseCode));

    }

    http.end();
    client.stop();

  } else {
    Serial.println("Unable to initiate connection to Render.");
  }

  delay(2000); // 2 second pause between cloud uploads
}