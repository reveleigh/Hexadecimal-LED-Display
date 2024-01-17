# Hexadecimal LED Display

A Raspberry Pi Pico W project that uses Micropython and Neopixels to highlight the place value of the hexadecimal numbering system.

Full project write can be found here: [https://russelleveleigh.medium.com/exploring-different-number-bases-with-a-hexadecimal-display-d1d2c726263b](https://medium.com/@russelleveleigh/exploring-different-number-bases-with-a-hexadecimal-display-d1d2c726263b?sk=2f96e7c51a4c88aef35aaff2d7647830)

Makes use of the following sources:

Neopixel library: https://github.com/blaz-r/pi_pico_neopixel

Pico W Access Point: https://github.com/recantha/PicoWAccessPoint

## Functionality Overview

The project offers the following key functionalities:

1. **Turn On**: Instantly illuminates all LEDs on the RGB matrix, creating a vibrant display.

2. **Turn Off**: Swiftly turns off all LEDs, ensuring a clean and crisp matrix appearance.

3. **Display Hexadecimal Numbers**: The controller can exhibit hexadecimal numbers on the matrix, counting upwards from 0 to a predefined base value. The base value can be set to your preferred number (default is 15), allowing you to explore various number bases and patterns.

4. **Cycle Through Spectrum**: This feature introduces a mesmerizing color spectrum effect. The matrix cycles through a captivating range of colors, producing a dynamic and visually appealing outcome.

5. **Rainbow Effect**: With this option, the matrix transforms into a vivid rainbow display. The LEDs dance through an array of colors, showcasing a delightful rainbow pattern.
