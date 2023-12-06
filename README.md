# BART Platform Sign Portable

![demo](https://github.com/shawenyao/bart-oled/blob/main/demo.gif)

## Requirements
* [Raspberry Pi Pico W](https://www.raspberrypi.com/products/raspberry-pi-pico/) x 1
* Breadboard x 1
* Male-to-male jump wires x 4
* 128x64 OLED Display x 1
* Micro-USB  cable x 1
* Power adapter or power bank x 1

## Instructions
* Connect the OLED display to the Raspberry Pi Pico W on a breadboard
* Download and flash the [MicroPython firmware](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
* Edit `config.py` with the correct Wi-Fi SSID and password
* Copy `*.py` in the repository onto the Raspberry Pi Pico W
* Connect the Raspberry Pi Pico W to a power source

## Example
* https://www.shawenyao.com/BART-Platform-Sign-Portable/

## References
* BART API provided by [bart.gov](https://www.bart.gov/schedules/developers/api)
* Writer and font scripts by [micropython-font-to-py](https://github.com/peterhinch/micropython-font-to-py)
* Implementation of the http request function adapted from [urequests](https://github.com/micropython/micropython-lib/blob/master/python-ecosys/urequests/urequests.py)
