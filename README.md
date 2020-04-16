# Feather-nRF52840-proximity-detector
For table RPG or escape room

This is basically the Bluefruit Playground Hide and Seek from Adafruit
https://learn.adafruit.com/hide-n-seek-bluefruit-ornament/code-with-circuitpython

With a small twist, the receiver only interacts if the received color correspond to the on-board LED color.
This way, you can choose which object your players will look for, in case you have several around.

The emitter needs to be with the object you wants your players to find.
The code of the emitter is almost copy/pasted from David Glaude's version of Hide & Seek
https://gist.github.com/dglaude/58581f6e4ac4088e8b1be86d4156fad0

The receiver idea is the ghost detector from the Supernatural TV show.
It uses a piezo buzzer, 6 LEDs and a SG90 micro servo to act as a meter
(there is code for a real 3.3v meter in the file but the only one i could buy is too big for this project).
