# Import standard libraries
import asyncio
import network
import time
import urandom
import machine
import gc
from machine import Pin
from neopixel import Neopixel
from led_matrix import led_matrix

# Monkey-patch Neopixel.show to disable interrupts during hardware writes.
# This prevents Wi-Fi and system interrupts from starving the PIO FIFO buffer,
# which causes NeoPixel data signal glitching.
original_show = Neopixel.show
def safe_show(self):
    state = machine.disable_irq()
    try:
        original_show(self)
    finally:
        machine.enable_irq(state)
Neopixel.show = safe_show

# Try importing Microdot
try:
    from microdot import Microdot, send_file
except ImportError:
    # Fallback for older Microdot versions
    from microdot_asyncio import Microdot
    from microdot import send_file

# Boot with the hexadecimal counter mode (OPTION = 3) active
OPTION = 3
IS_BOOT_COUNT = True

# Define SSID and password for the access point
SSID = "Hexadecimal Clock"
PASSWORD = "123456789"

# Define an access point, name it and then make it active
AP = network.WLAN(network.AP_IF)
AP.config(essid=SSID, password=PASSWORD)
AP.active(True)

# Wait until it is active
while not AP.active():
    pass

print("Access point active")
print(AP.ifconfig())

# Setting up Neopixel object
NUMPIX = 136
STRIP = Neopixel(NUMPIX, 0, 22, "GRB")
OFF = (0, 0, 0)
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

# Set base global variable (default is 15 for Hexadecimal)
BASE = 15
# Boot up with a completely random 6-digit hexadecimal value
place = [urandom.randint(0, 15) for _ in range(6)]
COLOR = [0, 0, 0]
TARGET_COLOR = [0, 0, 0]

# Non-blocking turn off all leds
def turnOff():
    for i in range(NUMPIX):
        STRIP.set_pixel(i, OFF)
    STRIP.show()

# Non-blocking turn on all leds
async def turnOn_async():
    global OPTION
    for i in range(len(led_matrix)):
        for j in range(len(led_matrix[i])):
            if OPTION == 1:
                STRIP.set_pixel(led_matrix[i][j], WHITE)
                # Yield to the event loop so the server remains active
                await asyncio.sleep(0.005)
                STRIP.show()
            else:
                break
    if OPTION == 1:
        OPTION = 0

# Non-blocking rainbow animation
async def rainbow_async():
    global OPTION
    colors_rgb = [RED, ORANGE, YELLOW, GREEN, BLUE, INDIGO, VIOLET]
    step = round(NUMPIX / len(colors_rgb))
    current_pixel = 0

    for color1, color2 in zip(colors_rgb, colors_rgb[1:]):
        STRIP.set_pixel_line_gradient(current_pixel, current_pixel + step, color1, color2)
        current_pixel += step

    STRIP.set_pixel_line_gradient(current_pixel, NUMPIX - 1, VIOLET, RED)
    
    start_time = time.time()  # record the start time
    total_time = 30  # set the total time allowed in seconds
    interrupted = False

    while (time.time() - start_time) < total_time:
        if OPTION != 5:  # Check if option has changed (e.g. turned off)
            interrupted = True
            break
        STRIP.rotate_right(1)
        await asyncio.sleep(0.042)  # Non-blocking sleep!
        STRIP.show()

    if not interrupted:
        turnOff()
        OPTION = 0

# Base increment function
def increment_place(index, base):
    if place[index] < base:
        place[index] += 1
    else:
        place[index] = 0
        increment_place(index - 1, base)

# Non-blocking hexadecimal display runner
async def displayHex_async():
    global OPTION, BASE, place, IS_BOOT_COUNT
    current_colors = [(0, 0, 0)] * 136
    
    while OPTION == 3:
        # Calculate the RGB color equivalent to the current 6-digit place count
        # Red is place[0] & place[1]; Green is place[2] & place[3]; Blue is place[4] & place[5]
        r = (place[0] * 16 + place[1]) if BASE == 15 else int((place[0] / BASE) * 255)
        g = (place[2] * 16 + place[3]) if BASE == 15 else int((place[2] / BASE) * 255)
        b = (place[4] * 16 + place[5]) if BASE == 15 else int((place[4] / BASE) * 255)

        reverse_place = place[::-1]
        
        # Create target color buffer
        target_colors = [(0, 0, 0)] * 136
        for i in range(96):
            target_colors[i] = RED
            
        # Represent the current 24-bit Hexadecimal count color on the back/bottom (LEDs 96-135)
        for i in range(96, 136):
            target_colors[i] = (r, g, b)

        for i in range(6):
            for x in range(BASE + 1, 16):
                target_colors[led_matrix[i][x]] = OFF

        for i, p in enumerate(reverse_place):
            target_colors[led_matrix[i][p]] = WHITE

        # Apply transition
        if IS_BOOT_COUNT:
            # Smoothly fade from current colors to target colors over 6 steps (60ms total, extremely quick & smooth)
            steps = 6
            for step in range(1, steps + 1):
                if OPTION != 3:
                    break
                ratio = step / steps
                for idx in range(136):
                    c1 = current_colors[idx]
                    c2 = target_colors[idx]
                    curr_r = int(c1[0] + (c2[0] - c1[0]) * ratio)
                    curr_g = int(c1[1] + (c2[1] - c1[1]) * ratio)
                    curr_b = int(c1[2] + (c2[2] - c1[2]) * ratio)
                    STRIP.set_pixel(idx, (curr_r, curr_g, curr_b))
                STRIP.show()
                await asyncio.sleep(0.01)
        else:
            # Instant transition
            for idx in range(136):
                STRIP.set_pixel(idx, target_colors[idx])
            STRIP.show()
            
        current_colors = list(target_colors)

        # Non-blocking wait for 0.9 seconds (9 steps of 0.1s to check for option changes)
        for _ in range(9):
            if OPTION != 3:
                break
            await asyncio.sleep(0.1)

        if OPTION != 3:
            break

        # Increment the place values starting from the last element
        increment_place(len(place) - 1, BASE)
        
        if place == [BASE, BASE, BASE, BASE, BASE, BASE]:
            for i in range(BASE):
                STRIP.set_pixel(led_matrix[0][i], RED)
            STRIP.set_pixel(led_matrix[0][BASE], WHITE)
            STRIP.show()
            
            # Non-blocking wait for 1 second
            for _ in range(10):
                if OPTION != 3:
                    break
                await asyncio.sleep(0.1)
                
            if OPTION == 3:
                OPTION = 5  # Transition automatically to rainbow animation!
            break

# Function to get the place of the RGB value
def getPlace(r, g, b):
    for i in range(96):
        STRIP.set_pixel(i, OFF)

    place_vals = [r // 16, r % 16, g // 16, g % 16, b // 16, b % 16]

    for i in range(96, 136):
        STRIP.set_pixel(i, (r, g, b))

    for idx, color in enumerate([RED, RED, GREEN, GREEN, BLUE, BLUE]):
        for i in range(place_vals[idx]):
            STRIP.set_pixel(led_matrix[5 - idx][i], color)

    for idx, color in enumerate([WHITE, WHITE, WHITE, WHITE, WHITE, WHITE]):
        STRIP.set_pixel(led_matrix[idx][place_vals[5 - idx]], color)

    STRIP.show()
    print("RGB Breakdown:", place_vals)

# Non-blocking cycle through spectrum
async def cycle_through_spectrum_async(interval):
    global OPTION
    r, g, b = 255, 0, 0  # Starting RGB values (Red)
    while OPTION == 4:
        getPlace(r, g, b)
        if r == 255 and g != 255 and b == 0:
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
        await asyncio.sleep(interval)  # Non-blocking sleep!

# Setup Microdot Application
app = Microdot()

@app.route('/')
async def index(request):
    global BASE, OPTION, place, IS_BOOT_COUNT
    # Clear active option and turn off display when navigating back to menu
    OPTION = 2
    IS_BOOT_COUNT = False
    
    base_val = request.args.get('base')
    if base_val:
        place = [0, 0, 0, 0, 0, 0]
        BASE = int(base_val)
        print("Base set to:", BASE)
        OPTION = 3
    return send_file('html/index.html')

@app.route('/set-color')
async def set_color(request):
    global OPTION, TARGET_COLOR, IS_BOOT_COUNT
    IS_BOOT_COUNT = False
    
    r_val = request.args.get('r')
    g_val = request.args.get('g')
    b_val = request.args.get('b')
    
    if r_val is not None and g_val is not None and b_val is not None:
        TARGET_COLOR = [int(r_val), int(g_val), int(b_val)]
        OPTION = 6  # Static color mode
        
    return send_file('html/set-color.html')

@app.route('/on')
async def on(request):
    global OPTION, IS_BOOT_COUNT
    OPTION = 1
    IS_BOOT_COUNT = False
    return send_file('html/back.html')

@app.route('/off')
async def off(request):
    global OPTION, IS_BOOT_COUNT
    OPTION = 2
    IS_BOOT_COUNT = False
    return send_file('html/back.html')

@app.route('/hex')
async def hex(request):
    global IS_BOOT_COUNT
    IS_BOOT_COUNT = False
    return send_file('html/hex.html')

@app.route('/spectrum')
async def spectrum(request):
    global OPTION, IS_BOOT_COUNT
    OPTION = 4
    IS_BOOT_COUNT = False
    return send_file('html/back.html')

@app.route('/rainbow')
async def rainbow(request):
    global OPTION, IS_BOOT_COUNT
    OPTION = 5
    IS_BOOT_COUNT = False
    return send_file('html/back.html')

# Core LED state runner task
async def led_runner():
    global OPTION
    last_option = 0
    while True:
        if OPTION != last_option:
            # Clean up memory before transitioning to a new animation state
            gc.collect()
            # Clear display on option change for a clean slate
            turnOff()
            last_option = OPTION

        if OPTION == 1:
            await turnOn_async()
            last_option = OPTION
        elif OPTION == 2:
            turnOff()
            OPTION = 0
            last_option = 0
        elif OPTION == 3:
            await displayHex_async()
            last_option = OPTION
        elif OPTION == 4:
            await cycle_through_spectrum_async(0.1)
            last_option = OPTION
        elif OPTION == 5:
            await rainbow_async()
            last_option = OPTION
        elif OPTION == 6:
            # Static color mode with responsive slider changes
            last_color = None
            while OPTION == 6:
                if TARGET_COLOR != last_color:
                    getPlace(*TARGET_COLOR)
                    last_color = list(TARGET_COLOR)
                await asyncio.sleep(0.05)
            last_option = OPTION
            
        await asyncio.sleep(0.1)

# Main entry point to start event loop
async def main():
    # Initial garbage collection
    gc.collect()
    
    # Start the LED animation runner as a background task
    asyncio.create_task(led_runner())
    print("Background LED runner started")
    
    # Start the Microdot server (async method)
    print("Starting Microdot server on port 80...")
    await app.start_server(host="0.0.0.0", port=80)

# Run the system
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("System stopped manually")
except Exception as e:
    print("Fatal exception:", e)
