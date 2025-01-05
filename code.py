import board
import busio
import adafruit_sht31d
import digitalio
import time
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)

def convertCtoF(celcius):
    return celcius * (9/5) + 32

dir(board)

button = digitalio.DigitalInOut(board.D12)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP
button_previous_state = button.value

while True:
    button_current_state = button.value
    if button_current_state != button_previous_state:
        if not button.value:
            print('Humidity: {0}%'.format(sensor.relative_humidity))
            celcius = sensor.temperature
            fahrenheit = convertCtoF(celcius)
            print('Temperature: {0}F'.format(fahrenheit))
        else:
            print("Button UP")
    button_previous_state = button_current_state
    time.sleep(.1)