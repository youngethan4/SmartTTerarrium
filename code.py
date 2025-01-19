import board
import busio
import adafruit_sht31d
import digitalio
import adafruit_ssd1306
import time

WIDTH = 128
HEIGHT = 64
TIME_TO_PUMP = 10 # The amount of time in seconds to pump for
CHECK_HUMIDITY_PERIOD = 20 # Amount of time in seconds to check the humidity at.

i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)
display = adafruit_ssd1306.SSD1306_I2C(WIDTH, HEIGHT, i2c)

def convertCtoF(celcius):
    return celcius * (9/5) + 32

def getHumidity():
    humidity = sensor.relative_humidity
    return round(humidity, 1)

def getTemp():
    celcius = sensor.temperature
    fahrenheit = convertCtoF(celcius)
    return round(fahrenheit, 1)

dir(board)

button = digitalio.DigitalInOut(board.D12)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
button_previous_state = button.value

pump = digitalio.DigitalInOut(board.D8)
pump.direction = digitalio.Direction.OUTPUT
pump.value = False
set_pumping = False
pump_start_time = 0

next_humidity_check = time.time() + CHECK_HUMIDITY_PERIOD

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
    print("THERE WAS AN ERROR!!!")
    print(e)
finally:
    pump.value = False
