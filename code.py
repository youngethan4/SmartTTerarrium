import board
import busio
import adafruit_sht31d
import digitalio
import adafruit_ssd1306
import time
import adafruit_sdcard
import storage
import os

WIDTH: int = 128
HEIGHT: int = 64
TIME_TO_PUMP: int = 30 # The amount of time in seconds to pump for
CHECK_HUMIDITY_PERIOD: int = 3600 # Amount of time in seconds to check the humidity at.

# Connect peripherals
i2c = busio.I2C(board.SCL, board.SDA)
SD_CS = board.SD_CS

humidity_sensor_connected: bool = True
display_connected: bool = True

cs = digitalio.DigitalInOut(SD_CS)
sdcard = adafruit_sdcard.SDCard(board.SPI(), cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

def log(text):
    print(text)
    with open("/sd/log.txt", "a") as f:
        f.write(f"{text}\n")

try:
    sensor = adafruit_sht31d.SHT31D(i2c)
except Exception as e:
    humidity_sensor_connected = False
    log(e)

try:
    display = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)
except Exception as e: 
    display_connected = False
    log(e)


# Temp and Humidity functions
def convertCtoF(celcius: int) -> float:
    return celcius * (9/5) + 32

def getHumidity() -> float:
    humidity = sensor.relative_humidity
    return round(humidity, 1)

def getTemp() -> float:
    celcius = sensor.temperature
    fahrenheit = convertCtoF(celcius)
    return round(fahrenheit, 1)

# Setup io
button = digitalio.DigitalInOut(board.D12)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
button_previous_state = button.value

pump = digitalio.DigitalInOut(board.D8)
pump.direction = digitalio.Direction.OUTPUT
pump.value = False
set_pumping: bool = False
pump_start_time: float = 0.0

next_humidity_check = time.time() + CHECK_HUMIDITY_PERIOD

# If humidity sensor not available, let us know
if (not humidity_sensor_connected and display_connected):
    display.fill(0)
    display.text(f'Error connecting', 0, 20, 1)
    display.text(f'humidity sensor.', 0, 35, 1)
    display.show()

# If humidity sensor and display are ready, good to go
if (humidity_sensor_connected and display_connected):
    try:
        while True:
            # Get humidity and temp
            humidity = getHumidity()
            temp = getTemp()

            # If enough time has passed, check if the humidity if less than 50% and start pumping or reset the checking period
            if next_humidity_check <= time.time():
                if humidity < 50 and not pump.value:
                    set_pumping = True
                else:
                    next_humidity_check = time.time() + CHECK_HUMIDITY_PERIOD

            # Check if the button was pressed and start pumping if so
            if button.value != button_previous_state and not button.value and not pump.value:
                set_pumping = True
            button_previous_state = button.value

            # Configure display texts based on if we are pumping
            # Stop pumping if time is up
            pump_text = "Not pumping"
            humidity_check_display = f'Next run: {int(int(next_humidity_check - time.time()) / 60)}m {int(int(next_humidity_check - time.time()) % 60)}s'
            if set_pumping and not pump.value:
                pump.value = True
                pump_start_time = time.time()
                set_pumping = False
            if pump.value:
                if pump_start_time + TIME_TO_PUMP > time.time():
                    pump_text = f"Pumping for {pump_start_time + TIME_TO_PUMP - time.time()}s."
                else:
                    pump.value = False
                    next_humidity_check = time.time() + CHECK_HUMIDITY_PERIOD
            
            # Configure the display
            display.fill(0)
            display.text(f'Humidity: {humidity}%', 0, 5, 1)
            display.text(f'Temperature: {temp}F', 0, 20, 1)
            display.text(pump_text, 0, 35, 1)
            if not pump.value:
                display.text(humidity_check_display, 0, 50, 1)
            display.show()
            
            # Sleep
            time_to_sleep = 0.1
            time.sleep(time_to_sleep)
    except Exception as e:
        pump.value = False
        log(e)
    finally:
        pump.value = False
