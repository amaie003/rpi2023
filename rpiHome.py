#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import time
from rpi_ws281x import *
import argparse
import math
import json
import socketserver
from http.server import BaseHTTPRequestHandler
from threading import Thread
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering

# LED strip configuration:
LED_COUNT      = 150      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
#LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
strip = None
stop_threads = False

def solidLightWipe(strip,color,wait_ms=50):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i,color)
        strip.show()
        time.sleep(wait_ms/1000)
 

def breath(strip,color,speed,wait_s=50):
    increment = 1
    initialColor = list(color)
    print("start "+str(color[0])+","+str(color[1])+","+str(color[2]))
    while True:
        for i in range(strip.numPixels()):
            if i % 5 == 0:
                print("set "+str(color[0])+","+str(color[1])+","+str(color[2]))
            
            #print("increase?"+str(increment))
            strip.setPixelColor(i,Color(math.floor(color[0]),math.floor(color[1]),math.floor(color[2])))
        strip.show()

        if increment == 1:
            color[0] = min(255, color[0]*(1+speed))
            color[1] = min(255, color[1]*(1+speed))
            color[2] = min(255, color[2]*(1+speed))
        elif increment == -1:
            color[0] = max(0, color[0]*(1-speed))
            color[1] = max(0, color[1]*(1-speed))
            color[2] = max(0, color[2]*(1-speed))
        
        if (color[0] >= initialColor[0] or color[1] >= initialColor[1] or color[2] >= initialColor[2]):
            color[0] = initialColor[0]
            color[1] = initialColor[1]
            color[2] = initialColor[2]
            print("Already Max Color. Sleep")
            if sleepShouldBreak(wait_s):
                print("ending thread")
                return
            increment = -1
        
        if(color[0]<= 2 or color[1]<= 2 or color[2]<= 2):
            increment = 1
        time.sleep(50/1000.0)
        
def sleepShouldBreak(sleepTime):
    global stop_threads
    if stop_threads:
        return True
    time.sleep(sleepTime/6.0)
    if stop_threads:
        return True
    time.sleep(sleepTime/6.0)
    if stop_threads:
        return True
    time.sleep(sleepTime/6.0)
    if stop_threads:
        return True
    time.sleep(sleepTime/6.0)
    if stop_threads:
        return True
    time.sleep(sleepTime/6.0)
    if stop_threads:
        return True
    time.sleep(sleepTime/6.0)
    if stop_threads:
        return True

def make_histogram(cluster):
    """
    Count the number of pixels in each cluster
    :param: KMeans cluster
    :return: numpy histogram
    """
    numLabels = np.arange(0, len(np.unique(cluster.labels_)) + 1)
    hist, _ = np.histogram(cluster.labels_, bins=numLabels)
    hist = hist.astype('float32')
    hist /= hist.sum()
    return hist

def make_bar(color):
    """
    Create an image of a given color
    :param: height of the image
    :param: width of the image
    :param: BGR pixel values of the color
    :return: tuple of bar, rgb values, and hsv values
    """
   
    red, green, blue = int(color[2]), int(color[1]), int(color[0])

    return (red, green, blue)


class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/red':
            startBreath(255,25,25,0.1,10)
        elif self.path == '/blue':
            startBreath(25,25,255,0.1,10)
        elif self.path == '/green':
            startBreath(25,255,25,0.1,10)
            
        self.send_response(200)

        
def startBreath(red,green,blue,speed,wait):
    solidLightWipe(strip, Color(int(red),int(green),int(blue)), 10)
    breath(strip,[int(red),int(green),int(blue)],float(speed),wait)

def handlebutton(mode):
    if mode == 0:
        startBreath(255,25,25,0.1,10)
    elif mode == 1:
        startBreath(25,255,25,0.1,10)
    elif mode == 2:
        startBreath(25,25,255,0.1,10)
    elif mode == 3:
        solidLightWipe(strip, Color(int(0),int(0),int(0)), 10)


# Main program logic follows:

def main():
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()

    # Create NeoPixel object with appropriate configuration.
    global strip
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    GPIO.setwarnings(False) # Ignore warning for now
    GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
    GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
    mode = 0
    Threthread = None
    while True: # Run forever
        if GPIO.input(10) == GPIO.LOW:
            print("Button was pushed!")
            time.sleep(2)
          
            mode = (mode + 1) % 4
            print("Current new mode: "+ str(mode) + "!")
            
            if Threthread != None:
                print("Killing Old Thread")
                global stop_threads
                stop_threads = True
                Threthread.join()
        
            stop_threads = False
            Threthread = Thread(target=handlebutton, args=(mode,))
            Threthread.start()


main()


# In[1]:





# In[ ]:




