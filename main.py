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
            time.sleep(0.05)
            print("Light ", i, " is on" )
            strip.show()
turnOn()

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
