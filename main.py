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
ap = network.WLAN(network.AP_IF)
ap.config(essid=SSID, password=PASSWORD)
ap.active(True)

# Wait until it is active
while ap.active == False:
    pass

print("Access point active")
# Print out IP information
print(ap.ifconfig())


# Setting up Neopixel object
numpix = 136
strip = Neopixel(numpix, 0, 22, "GRB")
red = (255, 0, 0)
off = (0,0,0)
green = (0,255,0)
blue = (0,0,255)
white = (255, 255, 255)
orange = (255, 50, 0)
strip.brightness(100)

# turn off all leds
def turnOff():
    for i in range(numpix):
        strip.set_pixel(i, off)
        time.sleep(0.1)
        print("Light ", i, " is off" )
        strip.show()

# Run through all leds
def turnOn():
    for i in range(len(led_matrix)):
        for j in range(len(led_matrix[i])):
            strip.set_pixel(led_matrix[i][j], white)
            time.sleep(0.005)
            print("Light ", i, " is on" )
            strip.show()
#turnOn()

place = [0, 0, 0, 0, 0, 0]

def increment_place(index):
    if place[index] < 15:
        place[index] += 1
    else:
        place[index] = 0
        increment_place(index - 1)

def displayHex():
    while place != [15, 15, 15, 15, 15, 15]:
        reverse_place = place[::-1]
        for i in range(136):
            strip.set_pixel(i, red)

        for i, p in enumerate(reverse_place):
            strip.set_pixel(led_matrix[i][p], white)

        strip.show()
        time.sleep(0.9)

        # Increment the place values starting from the last element
        increment_place(len(place) - 1)

#displayHex()

def getPlace(r,g,b):
    for i in range(96):
        strip.set_pixel(i, off)
    p1 = r // 16
    p2 = r % 16
    p3 = g // 16
    p4 = g % 16
    p5 = b // 16
    p6 = b % 16
    place[0] = p1
    place[1] = p2
    place[2] = p3
    place[3] = p4
    place[4] = p5
    place[5] = p6
    for i in range(96, 136):
        strip.set_pixel(i, (r,g,b))
    for i in range(p1):
        strip.set_pixel(led_matrix[5][i], red)
    for i in range(p2):
        strip.set_pixel(led_matrix[4][i], red)
    for i in range(p3):
        strip.set_pixel(led_matrix[3][i], green)
    for i in range(p4):
        strip.set_pixel(led_matrix[2][i], green)
    for i in range(p5):
        strip.set_pixel(led_matrix[1][i], blue)
    for i in range(p6):
        strip.set_pixel(led_matrix[0][i], blue)

    strip.set_pixel(led_matrix[0][place[5]], white)
    strip.set_pixel(led_matrix[1][place[4]], white)
    strip.set_pixel(led_matrix[2][place[3]], white)
    strip.set_pixel(led_matrix[3][place[2]], white)
    strip.set_pixel(led_matrix[4][place[1]], white)
    strip.set_pixel(led_matrix[5][place[0]], white)
    strip.show()

    print(place)

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
cycle_through_spectrum(1)

#Pause to allow program to be stopped before
time.sleep(2)


# Start up a tiny web server
app = tinyweb.webserver()

# Serve a simple Hello World! response when / is called
# and turn the LED on/off using toggle()
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
