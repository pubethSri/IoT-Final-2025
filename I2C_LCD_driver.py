import smbus2 as smbus
import time

# --- Global Constants ---
I2C_ADDR_DEFAULT = 0x27  # Default I2C Address
LCD_WIDTH_DEFAULT = 16   # Default characters per line

class I2C_LCD_driver:
    # Define some device constants
    LCD_CHR = 1 # Mode - Sending data
    LCD_CMD = 0 # Mode - Sending command

    LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
    LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
    LCD_LINE_3 = 0x94 # LCD RAM address for the 3rd line
    LCD_LINE_4 = 0xD4 # LCD RAM address for the 4th line

    LCD_BACKLIGHT_ON = 0x08  # On
    LCD_BACKLIGHT_OFF = 0x00 # Off

    ENABLE = 0b00000100 # Enable bit

    # Timing constants
    E_PULSE = 0.0005
    E_DELAY = 0.0005

    #Open I2C interface
    def __init__(self, i2c_addr=I2C_ADDR_DEFAULT, i2c_bus=1, width=LCD_WIDTH_DEFAULT):
        self.bus = smbus.SMBus(i2c_bus)
        self.addr = i2c_addr
        self.width = width
        # --- FIX WAS HERE ---
        self.backlight = self.LCD_BACKLIGHT_ON
        
        self.lcd_device_init()

    def lcd_device_init(self):
        # Initialise display
        # --- FIXES WERE HERE ---
        self.lcd_byte(0x33, self.LCD_CMD) # 110011 Initialise
        self.lcd_byte(0x32, self.LCD_CMD) # 110010 Initialise
        self.lcd_byte(0x06, self.LCD_CMD) # 000110 Cursor move direction
        self.lcd_byte(0x0C, self.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off 
        self.lcd_byte(0x28, self.LCD_CMD) # 101000 Data length, number of lines, font size
        self.lcd_byte(0x01, self.LCD_CMD) # 000001 Clear display
        time.sleep(self.E_DELAY)

    def lcd_byte(self, bits, mode):
        # Send byte to data pins
        bits_high = mode | (bits & 0xF0) | self.backlight
        bits_low = mode | ((bits<<4) & 0xF0) | self.backlight

        # High bits
        self.bus.write_byte(self.addr, bits_high)
        self.lcd_toggle_enable(bits_high)

        # Low bits
        self.bus.write_byte(self.addr, bits_low)
        self.lcd_toggle_enable(bits_low)

    def lcd_toggle_enable(self, bits):
        # Toggle enable
        time.sleep(self.E_DELAY)
        # --- FIXES WERE HERE ---
        self.bus.write_byte(self.addr, (bits | self.ENABLE))
        time.sleep(self.E_PULSE)
        self.bus.write_byte(self.addr,(bits & ~self.ENABLE))
        time.sleep(self.E_DELAY)

    def lcd_string(self, message, line):
        # Send string to display
        message = message.ljust(self.width," ")
        # --- FIXES WERE HERE ---
        self.lcd_byte(line, self.LCD_CMD)
        for i in range(self.width):
            self.lcd_byte(ord(message[i]), self.LCD_CHR)

    def lcd_clear(self):
        # Clear display
        # --- FIX WAS HERE ---
        self.lcd_byte(0x01, self.LCD_CMD)
        time.sleep(self.E_DELAY)

    def set_backlight(self, state):
        # state is True for on, False for off
        if state:
            # --- FIXES WERE HERE ---
            self.backlight = self.LCD_BACKLIGHT_ON
        else:
            self.backlight = self.LCD_BACKLIGHT_OFF
        # --- FIX WAS HERE ---
        self.lcd_byte(0x00, self.LCD_CMD) # Send a dummy command to update backlight

if __name__ == '__main__':
    # Test code
    try:
        # Use the global constant
        mylcd = I2C_LCD_driver(i2c_addr=I2C_ADDR_DEFAULT)
        print("Writing to display...")
        # --- FIXES WERE HERE (Use 'mylcd.' to access constants) ---
        mylcd.lcd_string("Hello World!", mylcd.LCD_LINE_1)
        mylcd.lcd_string("Raspberry Pi", mylcd.LCD_LINE_2)
        time.sleep(3)
        mylcd.lcd_clear()
        mylcd.lcd_string("I2C LCD Test", mylcd.LCD_LINE_1)
        mylcd.lcd_string("Success!", mylcd.LCD_LINE_2)
        print("Test complete.")
    except KeyboardInterrupt:
        print("Cleaning up!")
        if 'mylcd' in locals():
            mylcd.lcd_clear()
            mylcd.set_backlight(False)
    except IOError:
        print("Error: Could not find LCD at address 0x{0:X}.".format(I2C_ADDR_DEFAULT))
        print("Check wiring and run 'sudo i2cdetect -y 1'.")
        print("Or, edit I2C_ADDR_DEFAULT in this file.")