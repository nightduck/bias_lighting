#from sklearn.cluster import KMeans
#import numpy as np
#import mss
#from PIL import Image
import serial
import neopixel
import threading
from array import array
from time import sleep
import numpy as np
import time

SOLID = b'\x00'
MIMIC = b'\x01'
MUSIC = b'\x02'
EMBER = b'\x03'
CONFIG = b'\x04'

# Any variables that could permanently damage the setup don't go in config file
BRIGHT_DIV = 8  #Any brightness received is divided by this number to save power

##Take screenshot
#with mss.mss() as sct:
#    monitor = {'top':0,'left':0,'width':53,'height':91}
#
#    img = np.array(sct.grab(monitor))
#
##Get average pixel from image
#init_centers = np.array([[64, 64, 64],[64, 64, 192],[64,192,64],[64,192,192],[192,64,64],[192, 64, 192],[192,192,64],[192,192,192]],np.int8)
#avg = KMeans(n_clusters=8, init=init_centers, n_init=1, max_inter=100, tol=1, algorithm='elkan')
#

# Sets pixel i on strip s to color c, where color is a 3 byte binary string
def setPixel(i, c, s):
    c = neopixel.Color(ord(c[0])/BRIGHT_DIV, ord(c[1])/BRIGHT_DIV, ord(c[2])/BRIGHT_DIV)
    #print("Setting pixel %d to %d" % (i, c))
    s.setPixelColor(i, c)

def blackout(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, 0)
    strip.show()

def do_nothing():
    pass


### Command functions. These are called immediately after receiving a command
### from the COM

### Automation functions. These are called repeatedly after a command is called to handle
### pi-driven animations. Functions should take at least 2 arguments, first being the strip
### object, and the second being a piece of peristant data (type is whatever you
### it to be. This can be ignored if your fn calls are independent
# TODO: Write some functions, and then a common class to bring it all together

# Thread that handles animations. Pass the interval between fn calls, the
# function it should execute as target, and any extra arguments will be passed
# to the animation fn. kwargs are ignored
class Animator(threading.Thread):
    def __init__(self, interval=0.04, target=do_nothing, strip=None, persist_data=None, *args, **kwargs):
        threading.Thread.__init__(self, target=target)
        self.daemon = True
        self.kill = False
        self.interval = interval
        self.target = target
        self.strip = strip
        self.persist_data = persist_data
        self.fn_args = args

    def run(self):
        while not self.kill:
            t = time.time()
            self.persist_data = self.target(self.strip, self.persist_data, *self.fn_args)
            print "Time to animate: %f" % (time.time() - t)
            sleep(self.interval)

    def stop(self):
        self.kill = True
        self.join()


# Lights a single pixel that moves down the strip.
# persist_data is the pixel number, and color is a 3byte RGB value.
def pong_ani(strip, persist_data, color):
    strip.setPixelColor(persist_data, color)
    strip.show()
    return persist_data + 1 if (persist_data + 1 < strip.numPixels()) else 0

# Utility fn for ember_ani. For 2 numbers a and b, this returns a value between
# the two given the weighting factor c, which is between 0 and 1 (actually might
# be negative, but that's an aside). If c=0, then it returns b. If c=1, it
# returns a. All other return values lie on the line formed by the points (c, b)
# and (c, a)
def lineate(a, b, c):
    return int(b + (a - b) * abs(c))

# Extract individual 8bit colors from 24bit rgb value
def red(c):
    return (c & 0xFF0000) >> 16
def green(c):
    return (c & 0xFF00) >> 8
def blue(c):
    return c & 0xFF

# Maintains the ember effect
def ember_ani(strip, states, c):
    #print "states: " + str(states)
    #print "c: " + str(c)
    # TODO: c contains triplets of int, int, and float. Can't use c[n][3], have to extract first byte from c[n][1]
    new_states = states
    for n, s in enumerate(states):
        # Calculate new state
        s = (2.0 / c[n][2]) + s
        if (s >= 1): s = -1
        new_states[n] = s
        
        # Normalize to the [rgb1, rgb2] range, and convert to chars
        r = lineate(red(c[n][0]), red(c[n][1]), s)
        g = lineate(green(c[n][0]), green(c[n][1]), s)
        b = lineate(blue(c[n][0]), blue(c[n][1]), s)

        strip.setPixelColor(n, neopixel.Color(r, g, b))
        #print("Setting pixel %d to (%x, %x, %x)" % (n, r, g, b))

    strip.show()

    return new_states

# SOLID function
def solid_fn(com, strip):
    for i in range(strip.numPixels()):
        rgb = com.read(3)
        setPixel(i, rgb, strip)

    strip.show()

def mimic_fn(com, strip):
    pass

def music_fn(com, strip):
    pass

# EMBER fn. This animation makes each pixel transition between two given colors
# Each pixel is independent of each other.
#
# Data is sent with 7 bytes corresponding to a single pixel. The first byte sent
# is the number of pixels. If this number is less than the total number of
# pixels, the data received will be copied to the remaing pixels. This allows
# to define an entire strip to behave the same way by sending only 8 total bytes
#
# The 7 bytes are [ red1, green1, blue1, red2, green2, blue2, speed ]
# where speed is the number of frames to transition from rgb1 to rgb2 and back
# Each pixel is initialized to a value between rgb1 and rgb2. Persitent data is
# a float between -1 and 1. Where the magnitude determines which direction the
# color is transitioning, (negative towards rgb1 and positive towards rgb2), and
# the magnitude shows the total progress (0 and 1 being the start and end points
# for rgb1>rgb2, whereas -1 and 0 are the start and end points for rgb2>rgb1)
def ember_fn(com, strip):
    n = ord(com.read(1))
    data = []
    for i in range(n):
        # Read in the start color, end color, and speed
        c = com.read(3)
        start = neopixel.Color(ord(c[0])/BRIGHT_DIV, ord(c[1])/BRIGHT_DIV, ord(c[2])/BRIGHT_DIV)
        c = com.read(3)
        end = neopixel.Color(ord(c[0])/BRIGHT_DIV, ord(c[1])/BRIGHT_DIV, ord(c[2])/BRIGHT_DIV)
        speed = ord(com.read(1))

        # Put it into data as a tuple
        data.append((start, end, speed))

    # If n != strip.numPixels, autofill the rest of data to match the right size
    # Then convert to np matrix of floats. This means that extracting rgb values
    # requires converting them to ints
    m = strip.numPixels()
    data = np.array(data * (m / n) + data[:(m % n)])

    # Populate the initial state between rgb1 and rgb2 and direction of change.
    # Will be a random number in range [-1,1)
    states = np.random.ranf(m) * 2 - 1

    t = Animator(0.02, ember_ani, strip, states, data)
    t.start()

# TWINKLE fn. Each pixel behave independently. After a given period of time, the
# pixel will suddenly change color. The random numbers that determine the time
# periods and the new colors are determined on a gaussian curve
def twinkle_fn(com, strip):
    pass

def config_fn(com, strip):
    pass

# Dictionary mapping command codes to their corresponding functions
commands = {
        SOLID : solid_fn,
        MIMIC : mimic_fn,
        MUSIC : music_fn,
        EMBER : ember_fn,
        CONFIG : config_fn
        }

### Main loop here
# TODO: Read config file

strip = neopixel.Adafruit_NeoPixel(36, 18, 800000, 5, False)
strip.begin()

print("Started strip")

u = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
if not u.is_open:
    print("Port failed to open")
    exit()

print("Opened port")

t = Animator(0.5, pong_ani, strip, 0, neopixel.Color(255, 0, 127))
                                # t is global timer object, it'll get redefined
                                # and restarted by any command fn that requires
                                # continued animation after returning
t.start()

try:
    while True:
        cmd = u.read(1)
        if cmd != b'':
            print("Got " + str(cmd))
            
            # Stop any animations
            t.stop()

            # Command received, use to code to call the corresponding fn, which will
            # hanndle the rest of the serial communication and edit the strip
            commands[cmd[0]](u, strip)
except KeyboardInterrupt:
    t.stop()
    u.close()
    blackout(strip)
