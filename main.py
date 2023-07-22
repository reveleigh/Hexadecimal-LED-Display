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
white = (255, 255, 255)
blue = (0,0,50)
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

place = [0,0,0,0,0,0]

def displayHex():
    while place != [15,15,15,15,15,15]:
        if place[0] < 15:
            place[0] += 1
        elif place[0] == 15:
            place[0] = 0
            if place[1] < 15:
                place[1] += 1
            elif place[1] == 15:
                place[1] = 0
                if place[2] < 15:
                    place[2] += 1
                elif place[2] == 15:
                    place[2] = 0
                    if place[3] < 15:
                        place[3] += 1
                    elif place[3] == 15:
                        place[3] = 0
                        if place[4] < 15:
                            place[4] += 1
                        elif place[4] == 15:
                            place[4] = 0
                            if place[5] < 15:
                                place[5] += 1
                            elif place[5] == 15:
                                place[5] = 0
        for i in range(136):
            strip.set_pixel(i, red)
        
        strip.set_pixel(led_matrix[0][place[0]], white)
        strip.set_pixel(led_matrix[1][place[1]], white)
        strip.set_pixel(led_matrix[2][place[2]], white)
        strip.set_pixel(led_matrix[3][place[3]], white)
        strip.set_pixel(led_matrix[4][place[4]], white)
        strip.set_pixel(led_matrix[5][place[5]], white)
        strip.show()
        time.sleep(0.9)


displayHex()
           

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
