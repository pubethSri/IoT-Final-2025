#include <WiFiS3.h>
#include <Wire.h>
#include "Adafruit_SHT31.h"
#include <coap-simple.h> // The CoAP library

// --- WiFi Credentials ---
char ssid[] = "IoTCruz";
char pass[] = "123456789";
int status = WL_IDLE_STATUS;

// --- Raspberry Pi Server Info ---
const char* pi_ip = "10.42.112.251"; // Your Pi's IP
const int coap_port = 5683;          // Default CoAP port

// --- CoAP Client Setup ---
WiFiUDP udp;
Coap coap(udp); // [cite: 18]

// --- Sensor Setup ---
Adafruit_SHT31 sht31 = Adafruit_SHT31();

// --- Non-blocking Timer (from your professor's code) ---
unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL_MS = 3000; // 10 seconds

//
// [NEW] This function handles replies from the server
// It's based on your professor's 'onClientResponse' 
//
void onResponse(CoapPacket &packet, IPAddress ip, int port) {
  Serial.print("[Server Response] from "); Serial.print(ip);
  Serial.print(", code="); Serial.print(packet.code);
  Serial.print(", len="); Serial.println(packet.payloadlen);

  // Print the payload (e.g., "Data Received")
  String payload;
  payload.reserve(packet.payloadlen);
  for (int i = 0; i < packet.payloadlen; i++) {
    payload += (char)packet.payload[i];
  }
  Serial.print("Payload: "); Serial.println(payload);
}

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

  //
  // [NEW] Add the response handler and start CoAP
  // Based on your professor's setup() 
  //
  coap.response(onResponse); // Tell CoAP which function to call on reply
  coap.start();            // Start the CoAP client

  Serial.println("CoAP client started.");
}


void loop() {
  //
  // [NEW] You MUST call coap.loop() every time
  // This checks for incoming response packets 
  //
  coap.loop();

  //
  // [NEW] Non-blocking timer
  // Checks if 10 seconds have passed 
  //
  if (millis() - lastSend >= SEND_INTERVAL_MS) {
    lastSend = millis(); // Reset the timer

    // --- This is your original sensor code ---
    float t = sht31.readTemperature();
    float h = sht31.readHumidity();

    if (isnan(t) || isnan(h)) {
      Serial.println("Failed to read from SHT31");
      return; // Skip this send attempt
    }

    Serial.print("Temp: "); Serial.print(t);
    Serial.print(" *C, ");
    Serial.print("Humid: "); Serial.println(h);

    char payload[100];
    sprintf(payload, "{\"temp\":%.1f, \"hum\":%.1f}", t, h);
    
    Serial.print("Sending PUT to /sensor-data with payload: ");
    Serial.println(payload);

    // Send the data using PUT (like coap.put in prof's code [cite: 26])
    coap.put(pi_ip, coap_port, "sensor-data", payload);
  }
}

//
// This is your original WiFi connection function, it's perfect.
//
void connectToWiFi() {
  if (WiFi.status() == WL_NO_MODULE) {
    Serial.println("Communication with WiFi module failed!");
    while (true);
  }

  while (status != WL_CONNECTED) {
    Serial.print("Attempting to connect to SSID: ");
    Serial.println(ssid);
    status = WiFi.begin(ssid, pass);
    delay(10000); // This delay is OK, it's only in setup()
  }
  
  Serial.println("Connected to WiFi!");
  Serial.print("My IP address: ");
  Serial.println(WiFi.localIP());
}