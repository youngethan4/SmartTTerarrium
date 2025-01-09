import board
import busio
import adafruit_sht31d
import digitalio
import adafruit_ssd1306
import time

WIDTH = 128
HEIGHT = 64

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

while True:
    display.fill(0)
    display.text('Humidity: {0}%'.format(getHumidity()), 0, 5, 1)
    display.text('Temperature: {0}F'.format(getTemp()), 0, 20, 1)
    button_current_state = button.value
    if button_current_state != button_previous_state:
        if not button.value:
            print('Humidity: {0}%'.format(getHumidity()))
            print('Temperature: {0}F'.format(getTemp()))
            pump.value = not pump.value
        else:
            print("Button UP")
    button_previous_state = button_current_state
    pump_text = "NOT PUMPING"
    if pump.value:
        pump_text = "PUMPING"
    display.text(pump_text, 0, 35, 1)
    display.show()
    time.sleep(.05)