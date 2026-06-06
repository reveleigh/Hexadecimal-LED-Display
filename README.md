# Hexadecimal LED Display

A Raspberry Pi Pico 2 W-powered hexadecimal LED matrix display.

## Hardware

- Raspberry Pi Pico 2 W
- 256-LED matrix (16x16) using WS2812B NeoPixel strips
- Custom PCB with level-shifting and power regulation

## Setup

### Firmware

I flashed the firmware using the Raspberry Pi Imager. I selected the "Raspberry Pi OS (other)" option and chose "Raspberry Pi OS Lite (64-bit)".

### Initial Setup

I opened the boot folder on the Pico and created an empty file called `ssh` to enable SSH access.

I created a file called `wpa_supplicant.conf` in the boot folder with my Wi-Fi details:

```
country=GB
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="MyWiFiSSID"
    psk="MyWiFiPassword"
}
```

I then navigated to my router to find the IP address assigned to the Pico.

### Connecting

I connected to the Pico using SSH:

```
ssh pi@<IP_ADDRESS>
```

The default password was `raspberry`.

### Initial Configuration

I ran `sudo raspi-config` to:

1. Change the default password
2. Enable SSH
3. Set the hostname to `hex-led-display`
4. Set the locale to `en_GB.UTF-8`

I also enabled the SPI interface to communicate with the LED matrix.

I ran the following commands to update the system:

```
sudo apt update
sudo apt full-upgrade
```

### Python Libraries

I installed the required Python libraries:

```
sudo apt install python3-pip
pip3 install rpi_ws281x adafruit-pureio spidev
```

## Running the Code

I copied the `led_matrix.py` and `main_v2.py` files to the Pico.

To run the code:

```
python3 main_v2.py
```

To run the code in the background and keep it running after I close the SSH connection, I used:

```
nohup python3 main_v2.py &
```

## Customisation

### Changing Characters

I modified the `led_matrix.py` file to define the hexadecimal characters (0-9, A-F). Each character is represented as a grid of 8x8 pixels.

### Adjusting Brightness

I adjusted the brightness in the `main_v2.py` file by changing the `brightness` parameter when creating the `Adafruit_NeoPixel` object.

### Updating Colours

I modified the `hex_colours` dictionary in `led_matrix.py` to change the colour scheme.

## Troubleshooting

### LEDs Not Lighting Up

I checked the wiring connections and made sure the data pin was connected to the correct GPIO pin.

I also verified that the ground connection was shared between the Pico and the LED strip.

### Flickering

If the LEDs flicker, I checked:

- Power supply: I made sure the power supply could provide enough current (5V 10A recommended)
- Level-shifting: I used a level-shifter to convert the 3.3V signal from the Pico to 5V for the LEDs
- Wiring: I checked for loose connections on the data line

## Credits

Based on the rpi_ws281x library by Jeremy Garff.