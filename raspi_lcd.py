import I2C_LCD_driver
import time

LCD_ADDRESS = 0x27 

mylcd = I2C_LCD_driver.I2C_LCD_driver(i2c_addr=LCD_ADDRESS, width=16)

print("Starting display test...")
print("Press Ctrl+C to stop.")

try:
    while True:
        temp_data = 25.4
        humid_data = 60.1
        
        line1_str = "Temp: {:.1f} C".format(temp_data)
        line2_str = "Humid: {:.1f} %".format(humid_data)

        mylcd.lcd_string(line1_str, mylcd.LCD_LINE_1)
        mylcd.lcd_string(line2_str, mylcd.LCD_LINE_2)
        
        time.sleep(2)

        mylcd.lcd_string("Waiting for", mylcd.LCD_LINE_1)
        mylcd.lcd_string("CoAP data...", mylcd.LCD_LINE_2)
        
        time.sleep(2)

except KeyboardInterrupt:
    print("Cleaning up!")
    mylcd.lcd_clear()
    mylcd.set_backlight(False)