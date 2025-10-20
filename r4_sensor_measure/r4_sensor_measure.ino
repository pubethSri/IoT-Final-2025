// code edited from test file
#include <WiFiS3.h>
#include <Wire.h>
#include "Adafruit_SHT31.h"
#include <coap-simple.h> // The CoAP library

// --- WiFi Credentials ---
char ssid[] = "cruzinternet_2.4G";
char pass[] = "0000099999cruz";
int status = WL_IDLE_STATUS;

// --- Raspberry Pi Server Info ---
// !!! IMPORTANT: Set your Pi's IP Address here !!!
const char* pi_ip = "192.168.1.55"; // Example: Your Pi's IP
const int coap_port = 5683;          // Default CoAP port

// --- CoAP Client Setup ---
WiFiUDP udp;
Coap coap(udp);

// --- Sensor Setup ---
Adafruit_SHT31 sht31 = Adafruit_SHT31();

void setup() {
  Serial.begin(9600);
  while (!Serial);

  Serial.println("Starting IoT Lab Client...");

  // 1. Initialize SHT31 Sensor
  if (!sht31.begin(0x44)) {
    Serial.println("Couldn't find SHT31 sensor!");
    while (1) delay(1);
  }

  // 2. Connect to WiFi
  connectToWiFi();
}

void loop() {
  // 1. Read sensor data
  float t = sht31.readTemperature();
  float h = sht31.readHumidity();

  if (isnan(t) || isnan(h)) {
    Serial.println("Failed to read from SHT31");
    delay(2000);
    return; // Skip this loop
  }

  Serial.print("Temp: "); Serial.print(t);
  Serial.print(" *C, ");
  Serial.print("Humid: "); Serial.println(h);


  char payload[100];
  sprintf(payload, "{\"temp\":%.1f, \"hum\":%.1f}", t, h);
  Serial.print("Sending payload: ");
  Serial.println(payload);

  int msgid = coap.put(pi_ip, coap_port, "sensor-data", payload);

  Serial.print("Sent CoAP message ID: ");
  Serial.println(msgid);

  // Wait 10 seconds before sending again
  delay(10000);
}

void connectToWiFi() {
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    while (true);
  }

  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    delay(10000);
  }
  
  Serial.println("Connected to WiFi!");
  Serial.print("My IP address: ");
  Serial.println(WiFi.localIP());
}