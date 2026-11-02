
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include "HX711.h"

// Wi-Fi hotspot details
const char* WIFI_SSID = "moto edge 60 pro_1842";
const char* WIFI_PASSWORD = "12345678";

// PARCELGUARD Render API
const char* SERVER_URL =
  "https://smartparcel-tcf5.onrender.com/api/sensor";

// HX711 connections
#define DT_PIN 4
#define SCK_PIN 5

HX711 scale;

// Calibration factor from your supplied Arduino sketch
float calibration_factor = -138138.0;

unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL_MS = 1000;

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to Wi-Fi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println("\n================================");
  Serial.println(" PARCELGUARD - LIVE SENSOR");
  Serial.println("================================");

  Serial.println("Keep platform EMPTY during startup tare.");

  scale.begin(DT_PIN, SCK_PIN);
  delay(1500);

  if (!scale.is_ready()) {
    Serial.println("ERROR: HX711 not detected. Check wiring.");

    while (true) {
      delay(1000);
    }
  }

  scale.set_scale(calibration_factor);
  scale.tare(20);

  Serial.println("HX711 ready!");
  Serial.println("Zero calibration complete.");

  connectWiFi();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  if (millis() - lastSend >= SEND_INTERVAL_MS) {
    lastSend = millis();

    if (!scale.is_ready()) {
      Serial.println("HX711 not ready. No reading sent.");
      return;
    }

    // Read weight in kg and convert to grams
    float weightKg = scale.get_units(5);
    float weightGrams = weightKg * 1000.0;

    // Remove small zero fluctuations
    if (weightGrams > -2.0 && weightGrams < 2.0) {
      weightGrams = 0.0;
    }

    if (weightGrams < 0) {
      weightGrams = 0.0;
    }

    Serial.print("LIVE WEIGHT: ");
    Serial.print(weightGrams, 2);
    Serial.println(" g");

    // HTTPS connection to Render
    WiFiClientSecure client;

    // Testing only: encrypted connection without
    // verifying the server certificate.
    client.setInsecure();

    HTTPClient http;
    http.setTimeout(15000);

    if (http.begin(client, SERVER_URL)) {
      http.addHeader("Content-Type", "application/json");

      String body =
        "{\"actual_weight_g\":" + String(weightGrams, 2) +
        ",\"source\":\"ESP32\"}";

      Serial.println("Sending data to PARCELGUARD...");

      int httpCode = http.POST(body);

      Serial.print("HTTP RESPONSE: ");
      Serial.println(httpCode);

      if (httpCode > 0) {
        Serial.println("SERVER RESPONSE:");
        Serial.println(http.getString());

        if (httpCode == 200 || httpCode == 201) {
          Serial.println("DATA SENT SUCCESSFULLY!");
        }
      } else {
        Serial.print("HTTPS ERROR: ");
        Serial.println(http.errorToString(httpCode));
      }

      http.end();
    } else {
      Serial.println("Unable to connect to Render server.");
    }

    Serial.println("--------------------------------");
  }
}
