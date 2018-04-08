
#Random dev notes

These are thoughts to myself while developing

* First byte tells PI what command is being sent. For example, if the command is the code for
MIMIC, the data being received is individual pixels, which the pi has to do kmeans clustering on
to get the desired rgb value for each neopixel. Before the bulk of the data is optional metadata
that depends on the command. The pi doesn't have to worry about the placement of neopixels
relative the the screen, it simply receives data in sequence, and uses that sequence to determine
a color for the respective neopixels in what it perceives as a 1-dimensional strip 

* If the raspberry pi seems unresponsive to the UART connection, go to /boot/cmdline.txt and get
rid of "console=serial0,115200". This is hogging the UART pins to be used as a remote login 

* Ideas for modes:
    * Solid color. The computer sends SOLID command followed by RGB data. Every 3 bytes determines
a neopixel. There's nothing special the pi does here

    * Mimic: The computer sends MIMIC command followed by a dimensions for a image size. Then it
sends a series of RGB values, with each collection corresponding to a portion of a screenshot. The
Pi performs a kmeans clustering algorithm to find the most popular color in each image and assigns
that to the neopixel corresponding to the portion of screen the screenshot is from. The only
problem is the large amounts of data required (91MB/s), which UART can't support.

    * Music: This one is unique in that the data doesn't determine color at all. The pi has a
progressing rainbow pattern that will speed up or brighten in beat to the music. The data is to
correspond to a music stream. As for that format, I'm unsure of. Tho there would have to be
metadata regarding the size of the music sample 

    * Ember: Given 2+ colors per pixel and a transition time, the pi will automate a slow
transition. If you pick the same 2 colors for every neopixel and assign random transition times,
it creates a nice ember glow effect. If all transition times are the same, you get a cool
breathing effect

	* Twinkle: Each pixel behaves individually and moves between 2 colors, like above, except the
transition is instant. Each pixel is given a range, and exactly where in that range it'll randomly
jump to is determined by a gaussian curve. The time to wait before switching to a new one might
also be determined by a gaussian curve. This will create a twinkling effect

    * Config: This means to save a configuration  The first two bytes of metadata determines the
size of the strip (for a generous maximum of 64K LEDs). The following command to a config file, so
it'll be started by default when the pi is powercycled. Not designed with MIMIC or MUSIC in mind.

* Have an automation thread running. For some modes, like music, the Pi should update the neopixel
effects even without imput from the host PC. This any effect that requires this should define an
automation function which the automation thread will run. Whenever a new command is received, a
check should be done to see if the automation thread should be shutdown

* Do some syncronization with corsair keyboards, depending on how easy that is

* Config file: Do json

Build notes:

To assemble the ui file, run

    pyuic5 -o client_ui.py client.ui

This'll convert the XML to runnable python code. (You still need to write a QWidget object that
implements the correct sockets).
