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
import pdb

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
    print("i=%s c=%s s=%s" % (str(i), str(c), str(s)))
    c = neopixel.Color(ord(c[0])/BRIGHT_DIV, ord(c[1])/BRIGHT_DIV, ord(c[2])/BRIGHT_DIV)
    #print("Setting pixel %d to %d" % (i, c))
    s.setPixelColor(i, c)

def blackout(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, 0)
    strip.show()

def do_nothing(*args):
    pass

# Yields every n elements in iterable as sub-list
def group(iterable, n):
    for i in xrange(0, len(iterable), n):
        yield iterable[i:i+n]

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

# Maintains the ember effect. Args are the neopixel strip object with # number of
# LEDs, an array of length # containing floats between -1 and 1 that marks the
# state of transition for each LED. c is a 2d array #x7 where each pixel gets a 7
# byte array. The first 3 are the rgb values of the respective pixel's start color.
# The next 3 are the rgb's of the end color. The last byte is the number of frames
# to transition between one color to another and back
def ember_ani(strip, states, c):
    #print "states: " + str(states)
    #print "c: " + str(c)
    new_states = states
    for n, s in enumerate(states):
        # Calculate new state
        s = (2.0 / c[n][6]) + s
        if (s >= 1): s = -1
        new_states[n] = s
        
        # Normalize to the [rgb1, rgb2] range, and convert to chars
        r = lineate(c[n][0], c[n][3], s)
        g = lineate(c[n][1], c[n][4], s)
        b = lineate(c[n][2], c[n][5], s)

        strip.setPixelColor(n, neopixel.Color(r, g, b))
        #print("Setting pixel %d to (%x, %x, %x)" % (n, r, g, b))

    strip.show()

    return new_states

# SOLID function. Sets pixels to solid static color. data is a byte array of the
# required RGB values. It's length should be a multiple of 3
def solid_fn(data, strip):
    if (not len(data) % 3 == 0):
        raise Exception("solid_fn: Incorrectly formatted data. len(data)=%d" % len(data))

    # Separate data into groups of 3 byte strings, and put each of those strings
    # into a numpy array. Copy and paste that data over and over again until the
    # array length matches the number of pixels
    pixels = np.empty(len(data)/3, dtype='|S3')
    for i, p in enumerate(group(data, 3)): pixels[i] = p
    m = strip.numPixels()
    n = len(pixels)
    pixels = np.array(np.append(np.tile(pixels, m / n), pixels[:(m % n)]))

    # Set each pixel color
    for i, p in enumerate(pixels):
        setPixel(i, p, strip)

    strip.show()

def mimic_fn(data, strip):
    pass

def music_fn(data, strip):
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
def ember_fn(data, strip):
    if (not len(data) % 7 == 0):
        raise Exception("ember_fn: Incorrectly formatted data. len(data)=%d" % len(data))

    # Group data in chunks of 7, The first 3 bytes represent the rgb of the start
    # color. The next 3 are the end color, and the last byte represents the number
    # of frames it should take to transition from one color to the other and back
    pixels = np.empty((len(data)/7, 7), dtype=np.int8)
    for i, p in enumerate(group(data, 7)):
        # Start color
        pixels[i][0] = ord(p[0])/BRIGHT_DIV
        pixels[i][1] = ord(p[1])/BRIGHT_DIV
        pixels[i][2] = ord(p[2])/BRIGHT_DIV

        # End color
        pixels[i][3] = ord(p[3])/BRIGHT_DIV
        pixels[i][4] = ord(p[4])/BRIGHT_DIV
        pixels[i][5] = ord(p[5])/BRIGHT_DIV

        # Transition speed
        pixels[i][6] = ord(p[6])

    # If the number of pixels given in data are less than strip.numPixels(),
    # then copy paste what was given until it's equal. If the total pixels isn't
    # a perfect multiple, then crop off the overflow
    m = strip.numPixels()
    n = len(pixels)
    pixels = np.concatenate((np.tile(pixels, (m / n, 1)), pixels[:(m % n)]))

    # Populate the initial state between rgb1 and rgb2 and direction of change.
    # Will be a random number in range [-1,1)
    states = np.random.ranf(m) * 2 - 1

    t = Animator(0.02, ember_ani, strip, states, pixels)
    t.start()

# TWINKLE fn. Each pixel behave independently. After a given period of time, the
# pixel will suddenly change color. The random numbers that determine the time
# periods and the new colors are determined on a gaussian curve
def twinkle_fn(data, strip):
    pass

def config_fn(data, strip):
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

strip = neopixel.Adafruit_NeoPixel(92, 18, 800000, 5, False)
strip.begin()

print("Started strip")

u = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
if not u.is_open:
    print("Port failed to open")
    exit()

print("Opened port")

t = Animator(0.5, do_nothing, strip, 0)
                                # t is global timer object, it'll get redefined
                                # and restarted by any command fn that requires
                                # continued animation after returning
t.start()

try:
    while True:
        cmd = u.read(1)
        if cmd != b'':
            print("Got %s" % cmd)
            
            # Stop any animations
            t.stop()
           
            try:
                #TODO: Handle timeout exceptions
                # Get the size of the data
                n = u.read(1)
                data = u.read(ord(n))
    
                if (not len(data) == ord(n)):
                    raise Exception("Incorrectly sized data packet. Expected %x, got %x" % (ord(n), len(data)))
    
                # Command received, use to code to call the corresponding fn, which will
                # hanndle the rest of the serial communication and edit the strip
                commands[cmd[0]](data, strip)
            except Exception as err:
                print(err)
                raise

except KeyboardInterrupt:
    t.stop()
    u.close()
    blackout(strip)
