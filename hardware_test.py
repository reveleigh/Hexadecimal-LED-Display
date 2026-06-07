# Standalone Hardware Test for Hexadecimal LED Display
# This script does NOT initialize Wi-Fi, Microdot, or asyncio.
# It runs a continuous loop testing the 3 main visual modes:
# 1. Hexadecimal counting (10 seconds, 1 count/sec, with fade)
# 2. Random hex colour breakdown (10 seconds, 5 colours, with fade)
# 3. Rolling rainbow loop (10 seconds)

import time
import urandom
from neopixel import Neopixel
from led_matrix import led_matrix

# Configuration
NUMPIX = 136
GPIO_PIN = 22
STATE_MACHINE = 0
BRIGHTNESS = 100
BASE = 15

print("Initializing NeoPixel Strip on Pin {} ({} LEDs)...".format(GPIO_PIN, NUMPIX))
STRIP = Neopixel(NUMPIX, STATE_MACHINE, GPIO_PIN, "GRB")
STRIP.brightness(BRIGHTNESS)

# Spectrum colours
OFF = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 50, 0)
YELLOW = (255, 100, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
INDIGO = (100, 0, 90)
VIOLET = (200, 0, 100)

# Track current colors on the strip to allow smooth fading
current_colors = [OFF] * NUMPIX

def update_display(target_colors, fade=True, duration=0.06):
    """
    Updates the LED strip from current_colors to target_colors.
    If fade is True, transitions smoothly over `duration` seconds.
    """
    global current_colors
    if fade:
        steps = 6
        step_delay = duration / steps
        for step in range(1, steps + 1):
            ratio = step / steps
            for idx in range(NUMPIX):
                c1 = current_colors[idx]
                c2 = target_colors[idx]
                curr_r = int(c1[0] + (c2[0] - c1[0]) * ratio)
                curr_g = int(c1[1] + (c2[1] - c1[1]) * ratio)
                curr_b = int(c1[2] + (c2[2] - c1[2]) * ratio)
                STRIP.set_pixel(idx, (curr_r, curr_g, curr_b))
            STRIP.show()
            time.sleep(step_delay)
    else:
        for idx in range(NUMPIX):
            STRIP.set_pixel(idx, target_colors[idx])
        STRIP.show()
    current_colors = list(target_colors)

# Hex counting state
place = [urandom.randint(0, 15) for _ in range(6)]

def increment_place(index, base=15):
    if index < 0:
        return
    if place[index] < base:
        place[index] += 1
    else:
        place[index] = 0
        increment_place(index - 1, base)

def run_hex_counting():
    """
    Counts up in Hexadecimal (Base 15) for 10 seconds.
    Increments once per second, representing the place value on the front grid,
    and the corresponding 24-bit RGB color on the back/bottom row.
    """
    global place
    print("Mode 1: Hexadecimal Counting (10 seconds)...")
    
    for count_step in range(10):
        # Calculate RGB color equivalent of the 6-digit hex place count
        r = place[0] * 16 + place[1]
        g = place[2] * 16 + place[3]
        b = place[4] * 16 + place[5]
        
        # Build target color buffer
        target_colors = [OFF] * NUMPIX
        
        # Red place backdrop on the front grid (first 96 pixels)
        for i in range(96):
            target_colors[i] = RED
            
        # Back/bottom row (LEDs 96-135) shows the 24-bit RGB color
        for i in range(96, 136):
            target_colors[i] = (r, g, b)
            
        # Clear out unused matrix segments above BASE
        for i in range(6):
            for x in range(BASE + 1, 16):
                target_colors[led_matrix[i][x]] = OFF

        # Highlight active digit values in WHITE
        reverse_place = place[::-1]
        for i, p in enumerate(reverse_place):
            target_colors[led_matrix[i][p]] = WHITE
            
        print("  Count Step {}: Hex Value = {}, RGB = ({}, {}, {})".format(
            count_step + 1, "".join(["{:X}".format(val) for val in place]), r, g, b
        ))
        
        # Transition with a quick 60ms fade
        update_display(target_colors, fade=True, duration=0.06)
        
        # Sleep for the remainder of the 1-second interval
        time.sleep(0.94)
        
        # Increment place count for next step
        increment_place(len(place) - 1, BASE)

def run_random_colours():
    """
    Displays random hex colours for 10 seconds.
    Changes colour every 2 seconds (5 colours total) with a slight fade between changes.
    """
    print("Mode 2: Random Hex Colours (10 seconds)...")
    
    for color_step in range(5):
        r = urandom.randint(0, 255)
        g = urandom.randint(0, 255)
        b = urandom.randint(0, 255)
        
        place_vals = [r // 16, r % 16, g // 16, g % 16, b // 16, b % 16]
        print("  Colour Step {}: RGB = ({}, {}, {}), Breakdown = {}".format(
            color_step + 1, r, g, b, place_vals
        ))
        
        # Build target color buffer using the getPlace color breakdown logic
        target_colors = [OFF] * NUMPIX
        
        # Back/bottom row (LEDs 96-135) shows the solid RGB color
        for i in range(96, 136):
            target_colors[i] = (r, g, b)
            
        # Red/Green/Blue color code backdrops on the front grid (0-95)
        for idx, color in enumerate([RED, RED, GREEN, GREEN, BLUE, BLUE]):
            row = 5 - idx
            for i in range(place_vals[idx]):
                target_colors[led_matrix[row][i]] = color
                
        # White active digit indicators
        for idx in range(6):
            val = place_vals[5 - idx]
            target_colors[led_matrix[idx][val]] = WHITE
            
        # Transition with a smooth 0.3-second fade
        update_display(target_colors, fade=True, duration=0.3)
        
        # Sleep for the remainder of the 2-second interval
        time.sleep(1.7)

def run_rainbow():
    """
    Displays a rolling rainbow loop for 10 seconds.
    Rotates the gradient right by 1 pixel every 42ms.
    """
    global current_colors
    print("Mode 3: Rainbow Loop (10 seconds)...")
    
    # 1. Set the initial rainbow gradient using the Neopixel built-in method
    colors_rgb = [RED, ORANGE, YELLOW, GREEN, BLUE, INDIGO, VIOLET]
    step = round(NUMPIX / len(colors_rgb))
    current_pixel = 0

    for color1, color2 in zip(colors_rgb, colors_rgb[1:]):
        STRIP.set_pixel_line_gradient(current_pixel, current_pixel + step, color1, color2)
        current_pixel += step

    STRIP.set_pixel_line_gradient(current_pixel, NUMPIX - 1, VIOLET, RED)
    
    # Read the generated rainbow colors from the strip buffer
    rainbow_colors = [STRIP.get_pixel(i) for i in range(NUMPIX)]
    
    # Restore STRIP state back to previous current_colors to allow smooth fade into the rainbow
    for i in range(NUMPIX):
        STRIP.set_pixel(i, current_colors[i])
        
    # Fade into the starting rainbow frame over 0.5 seconds
    update_display(rainbow_colors, fade=True, duration=0.5)
    
    # 2. Run the rotation animation loop for 10 seconds
    start_time = time.time()
    frame_count = 0
    while (time.time() - start_time) < 10.0:
        STRIP.rotate_right(1)
        current_colors = current_colors[-1:] + current_colors[:-1]
        STRIP.show()
        time.sleep(0.042)
        frame_count += 1
        
    print("  Rainbow complete (ran {} frames)".format(frame_count))

# Main Loop
try:
    print("Starting continuous Hardware Test loop. Press Ctrl+C in Thonny to stop.")
    while True:
        run_hex_counting()
        run_random_colours()
        run_rainbow()
except KeyboardInterrupt:
    print("\nTest stopped by user. Turning off LEDs...")
    for i in range(NUMPIX):
        STRIP.set_pixel(i, OFF)
    STRIP.show()
    print("Done.")
