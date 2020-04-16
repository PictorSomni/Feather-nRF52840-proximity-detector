"""
Feather nRF52840 Express promity emitter
You can use this code on a Feather nRF52840 Express to advertise a color.
The buttons change the color when advertising.

The code for the Feather nRF52840 Express receiver is available at https://gist.github.com/PictorSomni
"""
### Original code https://learn.adafruit.com/hide-n-seek-bluefruit-ornament/code-with-circuitpython
### Forked from David Glaude https://gist.github.com/dglaude/58581f6e4ac4088e8b1be86d4156fad0


# -*- coding: utf-8 -*-
#############################################################
#                          IMPORTS                          #
#############################################################
import time
import board
from digitalio import DigitalInOut, Direction, Pull
import neopixel
from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor

#############################################################
#                          CONTENT                          #
#############################################################
# The button of the Feather nRF52840
switch = DigitalInOut(board.SWITCH)
switch.direction = Direction.INPUT
switch.pull = Pull.UP

# On-board neopixel
onboard = neopixel.NeoPixel(board.NEOPIXEL, 1)
onboard.brightness = 0.1
onboard[0] = (0, 0, 0)

ble = BLERadio()
advertisement = AdafruitColor()

# The color pickers will cycle through this list with buttons A and B.
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

#############################################################
#                         MAIN LOOP                         #
#############################################################
while True:
# If the color has change, or if this is the first time, start advertising the color and set the RGB as feedback indicator.
    if last_i != i:
        last_i = i
        color = color_options[i]
        onboard[0] = ( (color>>16)&0xFF , (color>>8)&0xFF , color&0xFF )
        print("New color {:06x}".format(color))
        advertisement.color = color
        ble.stop_advertising()
        ble.start_advertising(advertisement)
        time.sleep(0.5)

# Verify if the user press the button (false if pressed) and change color.
    if not switch.value:
        i += 1
        i %= len(color_options)

# We should never reach this point because of the infinit loop.
ble.stop_advertising()