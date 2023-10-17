from config import *
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import framebuf
import network
import urequests as requests
import urequests2 as requests2
import ucollections as collections
from time import sleep, time
import courier20
import font10
import font6
import writer


# ===== helper functions =====
# connect to wifi
def connect_wifi():
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print("Waiting for connection...")
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f"Connected on {ip}")
    return ip

# disconnect wifi
def disconnect_wifi():
    wlan.disconnect()
    wlan.active(False)
    wlan.deinit()

# set initial time based on worldtimeapi.org
def set_time():
    try:
        response = requests.get("https://worldtimeapi.org/api/timezone/America/Los_Angeles")
        if response.status_code == 200:
            now = [int(float(x)) for x in response.json()["datetime"].replace("T", "-").replace(":", "-").split("-")]
            weekday = int(response.json()["day_of_week"])
            # initialize rtc (year, month, day, weekday, hours, minutes, seconds, subseconds)
            rtc.datetime((now[0], now[1], now[2], weekday, now[3], now[4], now[5], 0))
        response.close()
    except:
        print("Error!")

# convert bytearray to image
def process_frame(image_bytearray):
    image = bytearray(image_bytearray)
    fb = framebuf.FrameBuffer(image, 64, 64, framebuf.MONO_HLSB)
    return fb

# query BART legacy API
def get_bart_schedule():
    response = requests2.request("GET", api_endpoint, timeout=10.0, headers={"User-Agent": "python-requests/2.28.1\r\n", "Accept-Encoding": "gzip, deflate, br", "Accept": "*/*"})
    
    # loop over all available roots and trains on a platform at a station
    schedule = {}
    
    if "etd" not in response["root"]["station"][0]:
        # no more trains available
        return None
    else:
        # loop over all routes at the station
        for route in response["root"]["station"][0]["etd"]:
            # loop over all trains of the route
            for train in route["estimate"]:
                if train["cancelflag"] == "0":
                    schedule[0 if train["minutes"] == "Leaving" else int(train["minutes"])] = f"{route['destination']}@{train['length']}@{color_encoder.get(train['color'].upper())}"
        return(collections.OrderedDict(sorted(schedule.items())))

# flash the screen
def flash():
    oled.fill(0)
    oled.show()
    sleep(0.2)

# display the time screen
def show_time():
    current_time = rtc.datetime()
    courier20_writer.set_textpos(32, 20)
    courier20_writer.printstring(f"{current_time[4]:02}:{current_time[5]:02}")
    oled.show()

# display the leaving train screen
def show_leaving_train():
    # destination
    text = schedule.get(0).split("@")[0].upper()
    if "/" in text:
        # break long names to 2 rows
        text_line1, text_line2 = text.split("/")
        text_line1 = f"{text_line1} /"
        font10_writer.set_textpos(max(round((128 - len(text_line1) * 9) / 2), 0), 5)
        font10_writer.printstring(text_line1)
        font10_writer.set_textpos(max(round((128 - len(text_line2) * 10.5) / 2), 0), 25)
        font10_writer.printstring(text_line2)
    else:
        font10_writer.set_textpos(max(round((128 - len(text) * 10.5) / 2), 0), 20)
        font10_writer.printstring(text)
    oled.show()
    
    # how many cars and line color
    text = f"{schedule.get(0).split('@')[1]}-car, {schedule.get(0).split('@')[2]} line".upper()
    font6_writer.set_textpos(max(round((128 - len(text) * 7) / 2), 0), 50)
    font6_writer.printstring(text)
    oled.show()

# display the schedule screen
def show_schedule(top):
    if top:
        y = 0
    else:
        y = 34
    # line name and estimated time
    font6_writer.set_textpos(0, y)
    font6_writer.printstring(f"{train[1].split('@')[0][0:12]} {train[0]} min".upper())
    # how many cars and line color
    font6_writer.set_textpos(0, y + 14)
    font6_writer.printstring(f"{train[1].split('@')[1]}-car, {train[1].split('@')[2]} line".upper())
    oled.show()


# ===== various devices =====
i2c = I2C(0, sda=Pin(sda_pin), scl=Pin(scl_pin))
oled = SSD1306_I2C(128, 64, i2c)
wlan = network.WLAN(network.STA_IF)
led = Pin("LED", Pin.OUT)
rtc = machine.RTC()


# ===== main =====
# flash led to indicate power on
led.on()
sleep(0.1)
led.off()
sleep(1)

# connect to wifi
connect_wifi()

# set rtc time based on api
set_time()

# flash led twice to indicate wifi is connected
led.on()
sleep(0.1)
led.off()
sleep(0.1)
led.on()
sleep(0.1)
led.off()

# convert bytearry to images
fb_logo = process_frame(logo)

# startup icon
oled.fill(0)
oled.blit(fb_logo, 32, 0)
oled.show()
sleep(2)

# various fonts
font6_writer = writer.Writer(oled, font6, verbose=False)
font10_writer = writer.Writer(oled, font10, verbose=False)
courier20_writer = writer.Writer(oled, courier20, verbose=False)

# query BART API and display train info
schedule = None
while True:
    try:
        # this step takes ~5 seconds
        schedule = get_bart_schedule()
    except:
        print("Error!")

    if schedule is None:
        # no more trains available
        # show time
        flash()
        show_time()
        sleep(2)
    
    elif schedule.get(0) is not None:
        # if a train is entering the platform        
        flash()
        show_leaving_train()
        sleep(2)
    else:
        # if no trains are leaving the platform
        i = 0
        for train in schedule.items():            
            if (i % 2) == 0:
                flash()
                # top half of the schedule screen
                show_schedule(top=True)
                
                if (i + 1) == len(schedule):
                    # already at the last record
                    sleep(5)
            else:
                # bottom half the schedule screen
                show_schedule(top=False)
                sleep(5)
            
            # show 2 screens of info at most (4 trains)
            i = i + 1
            if i > 3:
                break
        
        # show time
        flash()
        show_time()
        sleep(1)
