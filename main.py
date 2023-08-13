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

#Set intial option to off
OPTION = 0

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

# Set base global variable
BASE = 15

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
    STRIP.show()

# Run through all leds
def turnOn():
    global OPTION
    for i in range(len(led_matrix)):
        for j in range(len(led_matrix[i])):
            if OPTION == 1:
                STRIP.set_pixel(led_matrix[i][j], WHITE)
                time.sleep(0.005)
                print("Light ", i, " is on" )
                STRIP.show()
            else:
                break
    OPTION = 0

place = [0, 0, 0, 0, 0, 0]

def increment_place(index,base):
    if place[index] < base:
        place[index] += 1
    else:
        place[index] = 0
        increment_place(index - 1,base)

def displayHex():
    while True:
        global OPTION
        if OPTION == 3:
            reverse_place = place[::-1]
            for i in range(136):
                STRIP.set_pixel(i, RED)
            for i in range(6):
                for x in range(BASE+1, 16):
                    STRIP.set_pixel(led_matrix[i][x], OFF)

            for i, p in enumerate(reverse_place):
                STRIP.set_pixel(led_matrix[i][p], WHITE)

            STRIP.show()
            time.sleep(0.9)

            # Increment the place values starting from the last element
            increment_place(len(place) - 1,BASE)
            if place == [BASE, BASE, BASE, BASE, BASE, BASE]:
                for i in range(BASE):
                    STRIP.set_pixel(led_matrix[0][i],RED)
                STRIP.set_pixel(led_matrix[0][BASE], WHITE)
                STRIP.show()
                time.sleep(1)
                rainbow()
                turnOff()
                OPTION = 0
                break

        else:
            turnOff()
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
    global OPTION
    r, g, b = 255, 0, 0  # Starting RGB values (Red) 
    while True:
        if OPTION == 4:
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
        else:
            turnOff()
            break

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

def options():
    while True:
        time.sleep(1)
        if OPTION == 1:
            turnOn()
        elif OPTION == 2:
            turnOff()
        elif OPTION == 3:
            displayHex()
        elif OPTION == 4:
            cycle_through_spectrum(0.1)
        elif OPTION == 5:
            rainbow()
        else:
            pass
        print(OPTION)

        
# Start a new thread 
_thread.start_new_thread(options,())

# Start up a tiny web server
app = tinyweb.webserver()

# Routes
@app.route('/')
async def index(request, response):
    try:
        global OPTION
        global BASE
        file = open("html/index.html")
        html = file.read()
        file.close()
        # Start HTTP response with content-type text/html
        await response.start_html()
        # Send actual HTML page
        await response.send(html)

        query_string = request.query_string.decode('utf-8')
        if query_string == "":
            return
        else:
            key, value = query_string.split('=')
            if key == "base":
                BASE = int(value)
                print("Base set to: ", BASE)
                OPTION = 3

    except Exception as e:
        print("An error occurred:", e)
        await response.send("An error occurred: {}".format(e))

    print("Home page")

@app.route('/set-color')
async def index(request, response):
    try:
        global OPTION
        file = open("html/set-color.html")
        html = file.read()
        file.close()
        # Start HTTP response with content-type text/html
        await response.start_html()
        # Send actual HTML page
        await response.send(html)

        query_string = request.query_string.decode('utf-8')
        if query_string == "":
            return
        else:
            # Get the RGB values from the query string
            r, g, b = query_string.split('&')
            r = int(r.split('=')[1])
            g = int(g.split('=')[1])
            b = int(b.split('=')[1])
            OPTION = 0
            turnOff()
            find_colour(r, g, b)
    
    except Exception as e:
        print("An error occurred:", e)
        await response.send("An error occurred: {}".format(e))

    print("Set color page")
            

@app.route('/on')
async def index(request, response):
    try:
        global OPTION
        file = open("html/back.html")
        html = file.read()
        file.close()
        # Start HTTP response with content-type text/html
        await response.start_html()
        # Send actual HTML page
        await response.send(html)

    except Exception as e:
        print("An error occurred:", e)
        await response.send("An error occurred: {}".format(e))

    OPTION = 1
    print(OPTION)
    print("Display on")

@app.route('/off')
async def index(request, response):
    try:
        global OPTION
        file = open("html/back.html")
        html = file.read()
        file.close()
        # Start HTTP response with content-type text/html
        await response.start_html()
        # Send actual HTML page
        await response.send(html)

    except Exception as e:
        print("An error occurred:", e)
        await response.send("An error occurred: {}".format(e))

    OPTION = 2
    print(OPTION)
    print("Display off")

@app.route('/hex')
async def index(request, response):
    try:
        global OPTION
        file = open("html/hex.html")
        html = file.read()
        file.close()
        # Start HTTP response with content-type text/html
        await response.start_html()
        # Send actual HTML page
        await response.send(html)

    except Exception as e:
        print("An error occurred:", e)
        await response.send("An error occurred: {}".format(e))

    print("Display Number base options")


@app.route('/spectrum')
async def index(request, response):
    try:
        global OPTION
        file = open("html/back.html")
        html = file.read()
        file.close()
        # Start HTTP response with content-type text/html
        await response.start_html()
        # Send actual HTML page
        await response.send(html)

    except Exception as e:
        print("An error occurred:", e)
        await response.send("An error occurred: {}".format(e))

    OPTION = 4
    print(OPTION)
    print("Display Colour Spectrum")

@app.route('/rainbow')
async def index(request, response):
    try:
        global OPTION
        file = open("html/back.html")
        html = file.read()
        file.close()
        # Start HTTP response with content-type text/html
        await response.start_html()
        # Send actual HTML page
        await response.send(html)

    except Exception as e:
        print("An error occurred:", e)
        await response.send("An error occurred: {}".format(e))

    OPTION = 5
    print(OPTION)
    print("Display Rainbow")

# Run the web server as the sole process
app.run(host="0.0.0.0", port=80)
