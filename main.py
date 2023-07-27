#import the libraries
from machine import Pin
from neopixel import Neopixel
from led_matrix import led_matrix
import utime
import time
import socket
import network
import _thread
import tinyweb
import ujson


# Define SSID and password for the access point
SSID = "Hexadecimal Clock"
PASSWORD = "123456789"

# Define an access point, name it and then make it active
AP = network.WLAN(network.AP_IF)
AP.config(essid=SSID, password=PASSWORD)
AP.active(True)

# Wait until it is active
while AP.active == False:
    pass

print("Access point active")
# Print out IP information
print(AP.ifconfig())


# Setting up Neopixel object
NUMPIX = 136
STRIP = Neopixel(NUMPIX, 0, 22, "GRB")
OFF = (0,0,0)
WHITE = (255, 255, 255)

# Spectrum colours
RED = (255, 0, 0)
ORANGE = (255, 50, 0)
YELLOW = (255, 100, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
INDIGO = (100, 0, 90)
VIOLET = (200, 0, 100)
STRIP.brightness(100)

def rainbow():
    colors_rgb = [RED, ORANGE, YELLOW, GREEN, BLUE, INDIGO, VIOLET]
    step = round(NUMPIX / len(colors_rgb))
    current_pixel = 0

    for color1, color2 in zip(colors_rgb, colors_rgb[1:]):
        STRIP.set_pixel_line_gradient(current_pixel, current_pixel + step, color1, color2)
        current_pixel += step

    STRIP.set_pixel_line_gradient(current_pixel, NUMPIX - 1, VIOLET, RED)
    
    start_time = time.time()  # record the start time
    total_time = 30  # set the total time allowed in seconds

    while (time.time() - start_time) < total_time:
        STRIP.rotate_right(1)
        time.sleep(0.042)
        STRIP.show()

    for i in range(NUMPIX):
        STRIP.set_pixel(i, OFF)       
    STRIP.show()

# turn off all leds
def turnOff():
    for i in range(NUMPIX):
        STRIP.set_pixel(i, OFF)
        time.sleep(0.1)
        print("Light ", i, " is off" )
        STRIP.show()

# Run through all leds
def turnOn():
    for i in range(len(led_matrix)):
        for j in range(len(led_matrix[i])):
            STRIP.set_pixel(led_matrix[i][j], WHITE)
            time.sleep(0.005)
            print("Light ", i, " is on" )
            STRIP.show()

place = [15, 15, 15, 0, 0, 0]

def increment_place(index,base):
    if place[index] < base:
        place[index] += 1
    else:
        place[index] = 0
        increment_place(index - 1,base)

def displayHex(base):
    while True:
        reverse_place = place[::-1]
        for i in range(136):
            STRIP.set_pixel(i, RED)
        for i in range(6):
            for x in range(base+1, 16):
                STRIP.set_pixel(led_matrix[i][x], OFF)

        for i, p in enumerate(reverse_place):
            STRIP.set_pixel(led_matrix[i][p], WHITE)

        STRIP.show()
        time.sleep(0.9)

        # Increment the place values starting from the last element
        increment_place(len(place) - 1,base)
        if place == [base, base, base, base, base, base]:
            for i in range(base):
                STRIP.set_pixel(led_matrix[0][i],RED)
            STRIP.set_pixel(led_matrix[0][base], WHITE)
            STRIP.show()
            print("Got here")
            time.sleep(1)
            rainbow()
            break

# Function to get the place of the RGB value
def getPlace(r, g, b):
    for i in range(96):
        STRIP.set_pixel(i, OFF)

    place = [r // 16, r % 16, g // 16, g % 16, b // 16, b % 16]

    for i in range(96, 136):
        STRIP.set_pixel(i, (r, g, b))

    for idx, color in enumerate([RED, RED, GREEN, GREEN, BLUE, BLUE]):
        for i in range(place[idx]):
            STRIP.set_pixel(led_matrix[5 - idx][i], color)

    for idx, color in enumerate([WHITE, WHITE, WHITE, WHITE, WHITE, WHITE]):
        STRIP.set_pixel(led_matrix[idx][place[5 - idx]], color)

    STRIP.show()
    print(place)

# Function to cycle through the spectrum
def cycle_through_spectrum(interval):
    r, g, b = 255, 0, 0  # Starting RGB values (Red) 
    while True:
        getPlace(r, g, b)
        if r == 255 and g !=255 and b == 0:
            g += 1
        elif r != 0 and g == 255 and b == 0:
            r -= 1
        elif g == 255 and b != 255 and r == 0:
            b += 1
        elif g != 0 and b == 255 and r == 0:
            g -= 1
        elif b == 255 and r != 255 and g == 0:
            r += 1
        elif b != 0 and r == 255 and g == 0:
            b -= 1  
        time.sleep(interval)

# Function to display colour for given RGB values
# Starts with a global to retain the last color set

COLOR = [0, 0, 0]
def find_colour(r, g, b):
    global COLOR

    while COLOR != [r, g, b]:
        for i in range(3):
            if COLOR[i] != [r, g, b][i]:
                COLOR[i] += 1 if [r, g, b][i] > COLOR[i] else -1
        getPlace(*COLOR)

# Pause for 2 seconds
time.sleep(2)

# Start up a tiny web server
app = tinyweb.webserver()

# Routes
@app.route('/')
async def index(request, response):
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send('''
        <!DOCTYPE html>
        <html>
            <head>
                <title>Hexadecimal Display</title>
            </head>
            <body>
                        Hello
            </body>
        </html>
    ''')
    print("home")


# Run the web server as the sole process
app.run(host="0.0.0.0", port=80)




