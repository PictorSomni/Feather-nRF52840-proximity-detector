"""
Feather nRF52840 Express promity receiver
You can use this code on a Feather nRF52840 Express to interact to e received color.
The buttons change the color to look for.

The code for the Feather nRF52840 Express receiver is available at https://gist.github.com/PictorSomni
"""
### Original code https://learn.adafruit.com/hide-n-seek-bluefruit-ornament/code-with-circuitpython


# -*- coding: utf-8 -*-
#############################################################
#                          IMPORTS                          #
#############################################################
import board
import neopixel
import time
import digitalio 
import simpleio
import pulseio
from adafruit_motor import servo
from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor

#############################################################
#                          CONTENT                          #
#############################################################
# The minimum required signal strength for this receiver to start interacting
TRESHOLD = -70

# The minimum signal strength mesured
LIMIT = -120

# Hack to change the clossest distance the emitter is from the receiver
MINIMUM = 0.5

# How many loop iteration required to refresh the data.
# It's a hack to smooth the received signal
WAIT_TIME = 1
last_wait = 0

# On-board neopixel
onboard = neopixel.NeoPixel(board.NEOPIXEL, 1)
onboard[0] = (0, 0, 0)
onboard.brightness = 0.1

# The button of the Feather nRF52840
switch = digitalio.DigitalInOut(board.SWITCH)
switch.direction = digitalio.Direction.INPUT
switch.pull = digitalio.Pull.UP

# Setup BLE connection
ble = BLERadio()

# The color pickers will cycle through this list
color_options = [0x110000,
                 0x111100,
                 0x001100,
                 0x001111,
                 0x000011,
                 0x110011,
                 0x111111]

i = 0
# Trick to force a first color "change"
last_i = -1

advertisement = AdafruitColor()

# a simple SG90 micro servo is used as meter
pwm = pulseio.PWMOut(board.D5, duty_cycle=2 ** 15, frequency=50)
servo1 = servo.Servo(pwm, min_pulse = 500, max_pulse = 2100)
servo1.angle = 180

# Uncomment if you use a real 3.3V meter
# meter = pulseio.PWMOut(board.A0, frequency=5000, duty_cycle=0)

# Piezo buzzer
buzzer = pulseio.PWMOut(board.A2, variable_frequency=True)
buzzer.duty_cycle = 0

# 6 LEDs are used in the receiver. The order is important
led_pins = [board.A3, board.D12, board.D11, board.D10, board.D9, board.D6]
leds = []
for pin in led_pins:
    led = digitalio.DigitalInOut(pin)
    led.direction = digitalio.Direction.OUTPUT
    led.value = False
    leds.append(led)

#############################################################
#                         FUNCTION                          #
#############################################################
# Normalize a value from any range to the desired range
def normalize(value, min, max, new_min, new_max):
    if value > max:
        value = max

    if value < min:
        value = min

    newvalue = int((new_max - new_min) / (max - min) * (value-max) + new_max)
    return newvalue

#############################################################
#                         MAIN LOOP                         #
#############################################################
while True:
    closest = None
    closest_rssi = -80
    closest_last_time = 0

    # Change the onboard LED color 
    if last_i != i:
        last_i = i
        color = color_options[i]
        onboard[0] = ( (color>>16)&0xFF , (color>>8)&0xFF , color&0xFF )

    # Change the onboard LED color each time the board button is pressed
    if not switch.value:
        i += 1
        i %= len(color_options)
        for led in leds:
            led.value = False
        buzzer.duty_cycle = 0
        servo.angle = 0
        # meter.duty_cycle = 0

    # Looking for color broadcast
    for entry in ble.start_scan(AdafruitColor, minimum_rssi= LIMIT, timeout=1):
        new = False
        if entry.address == closest:
            pass
        elif entry.rssi > closest_rssi:
            closest = entry.address
        else:
            continue
        closest_rssi = entry.rssi

        # Only interact if the received color is the same as the on-board LED color
        if entry.color == color_options[i]:

            # If the signal strength is not powerful enough, reset everything
            if closest_rssi < TRESHOLD:
                for led in leds:
                    led.value = False
                buzzer.duty_cycle = 0
                servo.angle = 180
                # meter.duty_cycle = 0
            else:
                # Check the wait time to refresh the data or not
                if last_wait >= WAIT_TIME:
                    servo1.angle = normalize(closest_rssi, TRESHOLD, TRESHOLD * MINIMUM, 180, 0)
                    buzzer.duty_cycle = 2**15
                    # meter.duty_cycle = normalize(closest_rssi, TRESHOLD, TRESHOLD * MINIMUM, 0, 65535)
                    buzzer.frequency = normalize(closest_rssi, TRESHOLD, TRESHOLD * MINIMUM, 400, 2000)
                    leds_state = normalize(closest_rssi , TRESHOLD, TRESHOLD * MINIMUM, 0, len(leds))
                    for led in range(leds_state):
                        leds[led].value = True
                    for led in range(leds_state, len(leds)):
                        leds[led].value = False
                    last_wait = 0
            last_wait += 1
        else :
            # Reset everything if the received color is different than the on-board LED color
            for led in leds:
                led.value = False
            buzzer.duty_cycle = 0
            servo.angle = 180
            # meter.duty_cycle = 0
    ble.stop_scan()