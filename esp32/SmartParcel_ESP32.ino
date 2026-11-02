
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

// Calibration factor from your calibrated load cell
float calibration_factor = -432.04;

unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL_MS = 2000;

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to Wi-Fi '");
  Serial.print(WIFI_SSID);
  Serial.print("'");

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nWi-Fi connected!");
    Serial.print("ESP32 IP: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
  } else {
    Serial.println("\nWi-Fi connection FAILED!");
    Serial.println("IMPORTANT: Ensure hotspot is 2.4 GHz (ESP32 does NOT support 5 GHz).");
  }
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
    if (!scale.is_ready()) {
      Serial.println("HX711 not ready. No reading sent.");
      lastSend = millis();
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

    if (WiFi.status() == WL_CONNECTED) {
      // HTTPS connection to Render
      WiFiClientSecure client;
      client.setInsecure(); // Bypass cert chain validation on ESP32

      HTTPClient http;
      http.setTimeout(30000); // 30s timeout for Render free-tier cold starts

      if (http.begin(client, SERVER_URL)) {
        http.setUserAgent("ESP32-ParcelGuard/1.0");
        http.addHeader("Content-Type", "application/json");
        http.addHeader("Connection", "close");

        String body =
          "{\"actual_weight_g\":" + String(weightGrams, 2) +
          ",\"source\":\"ESP32\"}";

        Serial.println("Sending data to PARCELGUARD on Render...");

        int httpCode = http.POST(body);

        Serial.print("HTTP RESPONSE: ");
        Serial.println(httpCode);

        if (httpCode > 0) {
          Serial.println("SERVER RESPONSE:");
          Serial.println(http.getString());

          if (httpCode == 200 || httpCode == 201) {
            Serial.println(">> DATA SENT SUCCESSFULLY! <<");
          }
        } else {
          Serial.print("HTTPS ERROR: ");
          Serial.println(http.errorToString(httpCode));
          if (httpCode == -1) {
            Serial.println("Hint: If Render was sleeping, it takes ~30-50s to wake up on free tier.");
          }
        }

        http.end();
      } else {
        Serial.println("Unable to connect to Render server.");
      }

      client.stop();
    } else {
      Serial.println("Skipping send: Wi-Fi not connected.");
    }

    Serial.print("Free Heap: ");
    Serial.print(ESP.getFreeHeap());
    Serial.println(" bytes");
    Serial.println("--------------------------------");

    lastSend = millis();
  }
}
