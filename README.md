# Portable BART Annoucement System

## Requirements
* [Raspberry Pi Pico W](https://www.raspberrypi.com/products/raspberry-pi-pico/) x 1
* Breadboard x 1
* Male-to-male jump wires x 4
* 128x64 Pixel OLED Display x 1
* Micro-USB  cable x 1
* Power adaptor or power bank x 1

## Instructions
* Connect the OLED display to the Raspberry Pi Pico W on a breadboard
* Download and flash the [MicroPython firmware](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
* Copy everything inthe repository to the Raspberry Pi Pico W
* Connect the Raspberry Pi Pico W to a power source

## References
* BART API provided by [bart.gov](https://www.bart.gov/schedules/developers/api)
* writer and font scripts by [micropython-font-to-py](https://github.com/peterhinch/micropython-font-to-py)
* http get function adapted from [urequests](https://github.com/micropython/micropython-lib/blob/master/python-ecosys/urequests/urequests.py)
