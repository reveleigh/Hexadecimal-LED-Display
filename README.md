# Hexadecimal LED Display

A Raspberry Pi Pico W / Pico 2 W project that uses MicroPython and NeoPixels to highlight the place value of the hexadecimal numbering system.

Full project write-up can be found here: [Exploring different number bases with a Hexadecimal Display](https://medium.com/@russelleveleigh/exploring-different-number-bases-with-a-hexadecimal-display-d1d2c726263b?sk=2f96e7c51a4c88aef35aaff2d7647830)

---

## Major Update: 24 May 2026

I have completely modernised the web server architecture and visual design system to run seamlessly and with rock-solid stability on the **Pico 2 W**:

### 1. Transition to Microdot & asyncio
* **The Problem:** The previous `tinyweb` server relied on older, low-level internal hacks in MicroPython's `uasyncio` library that are incompatible with modern firmware versions, resulting in `AttributeError` crashes and hangs. Additionally, the old `_thread` model caused concurrent memory allocation collisions on the Pico's dual-cores.
* **The Solution:** I migrated the web server to the modern, actively-maintained **Microdot** framework and transitioned the entire multitasking system to cooperative, single-threaded **`asyncio`**.
* **The Result:** All NeoPixel drawing and background tasks now yield cooperatively to the event loop, keeping the web server 100% active and responsive even during heavy animation loops. 

### 2. Serialised Thread-Safe Architecture
To completely eliminate visual overlapping and glitches, all NeoPixel hardware writes are now serialised through a single background task (`led_runner`). Web routes purely update global configuration variables, preventing concurrent write collisions.

### 3. Debounced Colour Pickers
The colour range sliders inside the web UI now feature a smart client-side debouncing layer. Visual indicators update instantly on the screen for a butter-smooth feel, but HTTP requests to the Pico are throttled to once per 120ms, protecting the microcontroller from network packet flooding.

### 4. Dynamic 24-bit Hex Clock Backlight
At boot, the Pico 2 W generates a completely random starting hexadecimal value and immediately begins counting up. As it counts, it automatically converts the 6 active place-value digits into a 24-bit RGB colour (Red, Green, Blue nibbles) and projects it onto the 40-pixel back/bottom row (LEDs 96-135) in real-time, functioning as a beautiful, slowly morphing **Hexadecimal Colour Clock**.

### 5. High-End Glassmorphism Web UI
All HTML control templates have been completely redesigned with a gorgeous frosted glass card style, elegant circular colour swatches, styled range tracks, animated spinners, and touch-tactile CSS active states. The UI scales beautifully from mobile phones to desktops.

---

## Credits & Libraries Used

This project makes use of the following excellent open-source libraries:

* **Microdot Web Server (v2.x):** [https://github.com/miguelgrinberg/microdot](https://github.com/miguelgrinberg/microdot) — Minimalistic, async-native web framework for MicroPython.
* **Neopixel Library:** [https://github.com/blaz-r/pi_pico_neopixel](https://github.com/blaz-r/pi_pico_neopixel) — High-performance WS2812 PIO state-machine driver.
* **Pico W Access Point:** [https://github.com/recantha/PicoWAccessPoint](https://github.com/recantha/PicoWAccessPoint) — Reference implementation for Wi-Fi Access Point configuration.

---

## Functionality Overview

1. **Turn On:** Instantly illuminates all place-value LEDs to pure white.
2. **Turn Off:** Swiftly turns off all LEDs.
3. **Display Hexadecimal Numbers:** Symmetrical grid to choose bases 2 through 16. It counts upwards representing positional base places with red indicator backdrops and white active digit highlights.
4. **Cycle Through Spectrum:** Cycles through the RGB spectrum, showing the numeric breakdown of colours on the places in real-time.
5. **Rainbow Effect:** Displays a beautiful, rolling colour-wheel spectrum loop.
