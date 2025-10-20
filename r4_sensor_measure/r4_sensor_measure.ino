// code edited from test file

#include <Arduino.h>
#include <Wire.h>
#include "WiFiS3.h"
#include "Adafruit_SHT31.h"

char ssid[] = "cruzinternet_2.4G";
char pass[] = "0000099999cruz";

Adafruit_SHT31 sht31 = Adafruit_SHT31();

int status = WL_IDLE_STATUS;

void setup() {
  Serial.begin(9600);

  while (!Serial)
    delay(10);     

  Serial.println("SHT31 Sensor");

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
  printCurrentNet();

  if (! sht31.begin(0x44)) { 
    Serial.println("Couldn't find SHT31 sensor!");
    Serial.println("Check your wiring!");
    while (1) delay(1);
  }
}


void loop() {

  float temperature = sht31.readTemperature();

  float humid = sht31.readHumidity();

  if (isnan(temperature) || isnan(humid)) {  
    Serial.println("Failed to read data from SHT31");
  } else { 
    Serial.print("Temperature = "); 
    Serial.print(temperature); 
    Serial.print(" *C \t\t");
    Serial.print("Humidity = "); 
    Serial.print(humid);
    Serial.println(" %");
  }
  
  delay(1000);
}


void printCurrentNet() {
  Serial.print("SSID: ");
  Serial.println(WiFi.SSID());

  IPAddress ip = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);
}