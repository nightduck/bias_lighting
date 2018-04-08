# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

import sys
import serial
import struct
from client_ui import QtWidgets
from client_ui import QtCore
from client_ui import QtGui
from client_ui import Ui_Form
import constants

# TODO: Put constants in module, so they're synchronized between client and server


class Client(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.cmd_str = b''      # This will change size depending on which tab is selected
        self.cmd = 0            # This is the command byte prepended to the cmd_str. Changes based on selected tab
        #self.com = serial.Serial('/dev/ttyUSB0', baudrate=115200, timeout=1)    # TODO: File checking if device doesn't exist

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.show()

    def send_cmd(self):
        # Build a command using the structure:
        #   +----------------+---------------+---------------+----------------+--------....--------+----------------+
        #   |  command byte  |     string length (2 bytes)   |  Command string (arbitrary length, structure varies) |
        #   +----------------+---------------+---------------+----------------+--------....--------+----------------+
        #
        sout = b''.join([struct.pack('>B', self.cmd), struct.pack('>H',len(self.cmd_str)), self.cmd_str])

        # Send command
        #self.com.send(sout)
        print("Sent: " + str(sout))

        # If the "set as default" checkbox is checked, send a config command. The structure is as follows
        #   +----------------+---------------+---------------+----------------+----------------+-----....-----+
        #   |   config cmd   |     string length (2 bytes)   |     Number of LEDs (2 bytes)    | Copy of sout |
        #   +----------------+---------------+---------------+----------------+----------------+----....------+
        if self.ui.cb_default.isChecked():
            sout = b''.join([struct.pack('>B', constants.CMD_CONFIG), struct.pack('>H', len(sout) + 2),
                             struct.pack('>H', self.ui.sb_num_leds.value()), sout])

            #self.com.send(sout)
            print("Sent: " + str(sout))

        pass

    def select_ani(self, ani):
        # Argument passed in is the tab number selected
        if ani == constants.TAB_SOLID:
            self.cmd = constants.CMD_SOLID
            self.cmd_str = bytearray(3)
        elif ani == constants.TAB_EMBER:
            self.cmd = constants.CMD_EMBER
            self.cmd_str = bytearray(7)

    # Function for solid "animation". command string structure is simple, just 3 bytes for RGB.
    # This will be used as the variable sout (see above)
    #   +-------+-------+-------+
    #   |  Red  |  Blue | Green |
    #   +-------+-------+-------+
    def solid_set_color(self):
        # Open a color dialog and fetch a color
        color = QtWidgets.QColorDialog.getColor()

        # Set the background color for the button
        self.ui.btn_solid_color.setStyleSheet("background-color:" + color.name() + ";")

        # Convert the color to a 3 byte array (ignoring alpha channel) and save that into the command string
        self.cmd_str = struct.pack('>I', color.rgb())[1:]

    # Functions for ember animation. command string structure is 3 bytes for
    # start color, 3 bytes for end color, and 1 byte for the number of frames
    # to transition from to the the other and back
    #   |      Start color      |       End color       |
    #   +-------+-------+-------+-------+-------+-------+----------------------+
    #   |  Red  |  Blue | Green |  Red  |  Blue | Green | Frames to transition |
    #   +-------+-------+-------+-------+-------+-------+----------------------+
    def ember_set_start_color(self):
        # Open a color dialog get a color
        color = QtWidgets.QColorDialog.getColor()

        # Set the background color for the button
        self.ui.btn_ember_start_color.setStyleSheet("background-color:" + color.name() + ";")

        # and make a 3 byte array for the RGB value (ignore the alpha channel)
        color = struct.pack('>I', color.rgb())[1:]

        # Insert the color into the command string as bytes 0-2, inclusive
        self.cmd_str = b''.join([color, self.cmd_str[3:]])

    def ember_set_end_color(self):
        # Open a color dialog and get a color
        color = QtWidgets.QColorDialog.getColor()

        # Set the background color for the button
        self.ui.btn_ember_end_color.setStyleSheet("background-color:" + color.name() + ";")

        # Convert the color to a 3 byte array for the RGB value (ignore the alpha channel)
        color = struct.pack('>I', color.rgb())[1:]

        # Insert the color into the command string as bytes 3-5, inclusive
        self.cmd_str = b''.join([self.cmd_str[0:3], color, struct.pack('>B', self.cmd_str[6])])

    def ember_set_frames(self, frames):
        # Save the number of frames
        self.cmd_str = b''.join([self.cmd_str[:6], struct.pack('>B', frames)])


app = QtWidgets.QApplication(sys.argv)
window = Client()
sys.exit(app.exec_())