import time

def getPlace(r, g, b):
    print(f"R: {r}, G: {g}, B: {b}")

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
cycle_through_spectrum(0.1)