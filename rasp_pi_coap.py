import asyncio
import json
import logging

# --- Import our LCD driver ---
import I2C_LCD_driver
from time import sleep

# --- Import CoAP libraries ---
from aiocoap import *
from aiocoap.resource import Resource, Site

# --- Initialize the LCD ---
# !!! IMPORTANT: Set your LCD's I2C Address here !!!
LCD_ADDRESS = 0x27 
mylcd = I2C_LCD_driver.I2C_LCD_driver(i2c_addr=LCD_ADDRESS)

print("LCD Initialized.")
mylcd.lcd_string("CoAP Server", mylcd.LCD_LINE_1)
mylcd.lcd_string("Waiting for data...", mylcd.LCD_LINE_2)
print("Waiting for data...")

# --- This class is our CoAP resource ---
# It defines what happens when we get a request
class SensorDataResource(Resource):

    def __init__(self):
        super().__init__()
        self.content = b"Ready" # Default content

    async def render_get(self, request):
        # Handle GET requests (Pi sends data)
        return Message(payload=self.content)

    async def render_post(self, request):
        # --- This is the important part! ---
        # It runs when the Arduino 'POSTS' data to us
        
        payload_str = request.payload.decode('utf-8')
        print(f"Received POST request with payload: {payload_str}")

        try:
            # 1. Parse the JSON data from the payload
            data = json.loads(payload_str)
            temp = data['temp']
            humid = data['hum']
            
            # 2. Create strings for the LCD
            line1_str = f"Temp: {temp:.1f} C"
            line2_str = f"Humid: {humid:.1f} %"

            # 3. Update the LCD
            mylcd.lcd_string(line1_str, mylcd.LCD_LINE_1)
            mylcd.lcd_string(line2_str, mylcd.LCD_LINE_2)
            
            # 4. Send a success response back to the Arduino
            return Message(code=Code.CHANGED, payload=b"Data Received")

        except Exception as e:
            print(f"Error parsing payload: {e}")
            # Send an error response
            return Message(code=Code.BAD_REQUEST, payload=b"Bad JSON")

# --- Main function to start the server ---
async def main():
    # Create a root resource and add our sensor resource to it
    root = Site()
    root.add_resource(['sensor-data'], SensorDataResource())

    print("Starting CoAP server...")
    
    # Bind the server to all IP addresses on the default CoAP port (5683)
    await Context.create_server_context(root, bind=('::', 5683))

    # Keep the server running
    await asyncio.get_running_loop().create_future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopping server...")
        mylcd.lcd_clear()
        mylcd.set_backlight(False)
        print("Goodbye!")