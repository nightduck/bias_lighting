#!/usr/bin/env python2
import serial
import neopixel
import threading
from array import array
import numpy as np
import time
import json
import struct
from binascii import hexlify
import pdb

print("Finished imports")

SOLID = 0
CONFIG = 1
MUSIC = 2
EMBER = 3
MIMIC = 4

# These are the default constants unless overridden by the config file.
MAX_BRIGHTNESS = 64     # Max is 255, though capping is reccomended because current draw
NUM_LEDS = 10
NEOPIXEL_PIN = 18
NEOPIXEL_HZ = 800000


# Sets pixel i on strip s to color c, where color is a 3 byte numpy array
def set_pixel_from_bytes(i, c, s):
    c = (c[0] << 16) + (c[1] << 8) + c[2]
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


######################################################################################


# Automation functions. These are called repeatedly after a command is called to handle
# pi-driven animations. Functions should take at least 2 arguments, first being the strip
# object, and the second being a piece of persistent data (type is whatever you
# it to be. This can be ignored if your fn calls are independent

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
        self.threadWait = threading.Event()     # This event is used to tell the thread to pause
        self.threadWait.set()
        self.threadPaused = threading.Event()   # This event is used by the thread to indicate it is paused
        self.threadPaused.clear()

    def run(self):
        while not self.kill:
            if self.threadWait.is_set():    # Continue until signaled to stop
                t = time.time()
                try:
                    # Run the specified animation function, using it's return value as the new
                    # persistent data
                    self.persist_data = self.target(self.strip, self.persist_data, *self.fn_args)
                except Exception as err:
                    # If the animation crashes set threadPaused event so config_fn doesn't hang
                    self.threadPaused.set()
                    raise
                #print "Time to animate: %f" % (time.time() - t)
                time.sleep(self.interval)
            else:                           # When signaled to pause, 
                self.threadPaused.set()     # indicate that it is actually paused,
                self.threadWait.wait()      # wait for the signal to resume,
                self.threadPaused.clear()   # and then indicate it is no longer paused

    def stop(self):
        self.kill = True
        self.threadWait.set()  # If event is paused, it'll never join, so unpause it
        self.join()

    def pause(self):
        self.threadWait.clear()     # Set this event to signal the thread to block
        self.threadPaused.wait()    # Wait on the thread to actually stop        

    def resume(self):
        self.threadWait.set()       # Allow the thread to proceed

    def change_ani(self, interval=0.04, target=do_nothing, persist_data=None, *args):
        self.pause()    # Blocks until animation is paused

        self.interval = interval
        self.target = target
        self.persist_data = persist_data
        self.fn_args = args

        self.resume()   # Resume the animation


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
    # a-b should span -255 to 255, so convert a and b to 16bit signed ints
    return np.uint8(a + (np.int16(b) - np.int16(a)) * abs(c))

# Maintains the ember effect. Args are the neopixel strip object with # number of
# LEDs, an array of length # containing floats between -1 and 1 that marks the
# state of transition for each LED. c is a 2d array #x7 where each pixel gets a 7
# byte array. The first 3 are the rgb values of the respective pixel's start color.
# The next 3 are the rgb's of the end color. The last byte is the number of frames
# to transition between one color to another and back
def ember_ani(strip, states, c):
    #print "states: " + str(states)
    #print "c: " + str(c[0])
    new_states = states
    for n, s in enumerate(states):
        # Calculate new state
        s = (2.0 / c[n][6]) + s
        if s >= 1: s = -1
        new_states[n] = s

        # Normalize to the [rgb1, rgb2] range, and convert to chars
        r = lineate(c[n][0], c[n][3], s)
        g = lineate(c[n][1], c[n][4], s)
        b = lineate(c[n][2], c[n][5], s)
        strip.setPixelColor(n, neopixel.Color(r, g, b))
        #print("Setting pixel %d to (%x, %x, %x)" % (n, r, g, b))

    strip.show()

    return new_states


#############################################################################


# Command functions. These are called immediately after receiving a command
# from the COM. Their args are all the same: a numpy array (who's contents vary
# depending on the command), and the global animator object

# SOLID function. Sets pixels to solid static color. data is a numpy int8 array of
# the required RGB values. It's length should be a multiple of 3
def solid_fn(data, t):
    print("Solid: %s" % hexlify(data))

    if not len(data) % 3 == 0:
        raise Exception("solid_fn: Incorrectly formatted data. len(data)=%d" % len(data))

    # Separate data into groups of 3 byte strings, and put each of those strings
    # into a numpy array. Copy and paste that data over and over again until the
    # array length matches the number of pixels
    pixels = np.empty((len(data)/3, 3), dtype=np.uint8)
    for i, p in enumerate(group(data, 3)): pixels[i] = p
    m = t.strip.numPixels()
    n = len(pixels)
    pixels = np.reshape(np.append(np.tile(pixels, m / n), pixels[:(m % n)]), (-1, 3))

    # Set each pixel color
    for i, p in enumerate(pixels):
        set_pixel_from_bytes(i, p, t.strip)

    t.pause()
    t.strip.show()

def mimic_fn(data, t):
    pass

def music_fn(data, t):
    pass


# EMBER fn. This animation makes each pixel transition between two given colors
# Each pixel is independent of each other.
#
# Data is sent with 7 bytes corresponding to a single pixel. The first byte sent
# is the number of pixels. If this number is less than the total number of
# pixels, the data received will be copied to the remaining pixels. This allows
# you to define an entire strip to behave the same way by sending only 7 total
# bytes
#
# The 7 bytes are [ red1, green1, blue1, red2, green2, blue2, speed ]
# where speed is the number of frames to transition from rgb1 to rgb2 and back
# Each pixel is initialized to a value between rgb1 and rgb2. Persistent data is
# a float between -1 and 1. Where the magnitude determines which direction the
# color is transitioning, (negative towards rgb1 and positive towards rgb2), and
# the magnitude shows the total progress (0 and 1 being the start and end points
# for rgb1>rgb2, whereas -1 and 0 are the start and end points for rgb2>rgb1)
def ember_fn(data, t):
    print("Ember: %s" % hexlify(data))

    if not len(data) % 7 == 0:
        raise Exception("ember_fn: Incorrectly formatted data. len(data)=%d" % len(data))

    # Group data in chunks of 7, The first 3 bytes represent the rgb of the start
    # color. The next 3 are the end color, and the last byte represents the number
    # of frames it should take to transition from one color to the other and back
    pixels = np.reshape(data, (-1, 7))

    # If the number of pixels given in data are less than strip.numPixels(),
    # then copy paste what was given until it's equal. If the total pixels isn't
    # a perfect multiple, then crop off the overflow
    m = t.strip.numPixels()
    n = len(pixels)
    pixels = np.concatenate((np.tile(pixels, (m / n, 1)), pixels[:(m % n)]))

    # Populate the initial state between rgb1 and rgb2 and direction of change.
    # Will be a random number in range [-1,1)
    states = np.random.ranf(m) * 2 - 1

    ember_ani(t.strip, states, pixels)
    t.change_ani(0.1, ember_ani, states, pixels)


# TWINKLE fn. Each pixel behave independently. After a given period of time, the
# pixel will suddenly change color. The random numbers that determine the time
# periods and the new colors are determined on a gaussian curve
def twinkle_fn(data, t):
    pass


# CONFIG fn. It is followed by 2 bytes which determine the number of LEDs on the
# strip. It is then followed by an arbitrary number of bytes the indicate the
# default command to run on startup. This doesn't affect the LEDs until the
# program restarts
def config_fn(data, t):
    print("Config: %s" % hexlify(data))

    d = {}
    d["numleds"] = (data[0] << 8) + data[1]
    init_cmd = data[2:]

    fout = open("settings.cfg", 'wb')
    fout.write(json.dumps(d) + "\n")
    fout.write(init_cmd)
    fout.close()

    # Pause the animator and update the strip with the new number of LEDs.
    t.pause()
    t.strip = neopixel.Adafruit_NeoPixel(d["numleds"], NEOPIXEL_PIN, NEOPIXEL_HZ,
                                         5, False, strip_type=neopixel.ws.WS2811_STRIP_GRB)
    t.strip.setBrightness(MAX_BRIGHTNESS)
    t.strip.begin()

    # Call the new default animation fn (which will resume the animator if it wishes)
    cmd = init_cmd[0]
    n = (init_cmd[1] << 8) + init_cmd[2]

    if len(init_cmd[3:]) != n:
        raise Exception("Incorrectly sized data packet. Expected %x, got %x" % (n, len(init_cmd[3:])))

    commands[cmd](init_cmd[3:], t)


# Dictionary mapping command codes to their corresponding functions
commands = {
        SOLID: solid_fn,
        MIMIC: mimic_fn,
        MUSIC: music_fn,
        EMBER: ember_fn,
        CONFIG: config_fn
        }


# Main loop here
print("Finished function and constants processing")


# t is global timer object, it'll get redefined and restarted by any command
# fn that requires continued animation after returning
t = Animator(0.5, do_nothing, None, 0)
t.start()

print("Made animator object")

# TODO: Restructure this a an if exists(setting.cfg) load setting, else load defaults
try:
    # The first line in settings.cfg is a json encoded dictionary that contains
    # arbitrary variables to set. The rest of the file is raw binary that
    # represents the default command to use on startup
    config = open("settings.cfg", 'rb')
    settings = json.loads(config.readline())
    init_cmd = np.frombuffer(config.read(), dtype=np.uint8)
    config.close()

    print("Read config file")

    NUM_LEDS = settings["numleds"]

    # TODO: When an install script is written, give the user the option to select between GRB and RGB strip types.
    #       RGB should be the default, but sometimes China will accidentally ship GRB variants
    t.strip = neopixel.Adafruit_NeoPixel(NUM_LEDS, NEOPIXEL_PIN, NEOPIXEL_HZ, 5, False,
                                       strip_type=neopixel.ws.WS2811_STRIP_GRB)
    t.strip.setBrightness(MAX_BRIGHTNESS)
    t.strip.begin()

    print("Started strip")

    # TODO: Use struct unpacking here so constants can be ints. (init_cmd[0] will return a byte because python2)
    cmd = init_cmd[0]
    n = (init_cmd[1] << 8) + init_cmd[2]
    data = init_cmd[3:]

    if len(data) != n:
        raise Exception("Incorrectly sized data packet. Expected %x, got %x" % (n, len(data)))

    commands[cmd](data, t) 
    print("Ran init command")
    
except Exception as err:
    if not t.strip:
        t.strip = neopixel.Adafruit_NeoPixel(NUM_LEDS, NEOPIXEL_PIN, NEOPIXEL_HZ, 5, False,
                                           strip_type=neopixel.ws.WS2811_STRIP_GRB)
        t.strip.setBrightness(MAX_BRIGHTNESS)
        t.strip.begin()
    else:
        print (err)


u = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
if not u.is_open:
    print("Port failed to open")
    exit()

print("Opened port")


try:
    while True:
        cmd = u.read(1)
        if cmd != b'':
            print("Got %s" % hexlify(cmd))
            
            try:
                # TODO: Handle timeout exceptions
                # Get the size of the data
                m = u.read(2)
                n = (ord(m[0]) << 8) + ord(m[1])
                data = np.frombuffer(u.read(n), dtype=np.uint8)

                print("Cmd: %s, len=%d, data=%s" % (hexlify(cmd), n, hexlify(data)))

                if not len(data) == n:
                    raise Exception("Incorrectly sized data packet. Expected %x, got %x" % (n, len(data)))
    
                # Command received, use to code to call the corresponding fn, which will
                # handle the rest of the serial communication and edit the strip
                commands[ord(cmd)](data, t)
            except Exception as err:
                print(err)
                raise

except KeyboardInterrupt:
    t.stop()
    u.close()
    blackout(t.strip)
except Exception as Err:
    t.stop()
    u.close()
    blackout(t.strip)
    raise
