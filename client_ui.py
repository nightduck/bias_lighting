# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'client.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(341, 227)
        self.btn_display = QtWidgets.QPushButton(Form)
        self.btn_display.setGeometry(QtCore.QRect(250, 190, 84, 28))
        self.btn_display.setObjectName("btn_display")
        self.tabs_ani = QtWidgets.QTabWidget(Form)
        self.tabs_ani.setGeometry(QtCore.QRect(0, 0, 341, 151))
        self.tabs_ani.setAutoFillBackground(False)
        self.tabs_ani.setObjectName("tabs_ani")
        self.tab_solid = QtWidgets.QWidget()
        self.tab_solid.setObjectName("tab_solid")
        self.lbl_solid_color = QtWidgets.QLabel(self.tab_solid)
        self.lbl_solid_color.setGeometry(QtCore.QRect(10, 20, 71, 21))
        self.lbl_solid_color.setScaledContents(False)
        self.lbl_solid_color.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_solid_color.setObjectName("lbl_solid_color")
        self.btn_solid_color = QtWidgets.QPushButton(self.tab_solid)
        self.btn_solid_color.setGeometry(QtCore.QRect(90, 10, 60, 40))
        self.btn_solid_color.setAutoFillBackground(False)
        self.btn_solid_color.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 255));\n"
"background-color: rgb(0, 0, 0);")
        self.btn_solid_color.setText("")
        self.btn_solid_color.setProperty("color", QtGui.QColor(0, 0, 0))
        self.btn_solid_color.setObjectName("btn_solid_color")
        self.tabs_ani.addTab(self.tab_solid, "")
        self.tab_ember = QtWidgets.QWidget()
        self.tab_ember.setObjectName("tab_ember")
        self.btn_ember_start_color = QtWidgets.QPushButton(self.tab_ember)
        self.btn_ember_start_color.setGeometry(QtCore.QRect(90, 10, 60, 40))
        self.btn_ember_start_color.setAutoFillBackground(False)
        self.btn_ember_start_color.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 255));\n"
"background-color: rgb(0, 0, 0);")
        self.btn_ember_start_color.setText("")
        self.btn_ember_start_color.setProperty("color", QtGui.QColor(0, 0, 0))
        self.btn_ember_start_color.setObjectName("btn_ember_start_color")
        self.lbl_ember_start_color = QtWidgets.QLabel(self.tab_ember)
        self.lbl_ember_start_color.setGeometry(QtCore.QRect(0, 20, 81, 21))
        self.lbl_ember_start_color.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_ember_start_color.setWordWrap(True)
        self.lbl_ember_start_color.setObjectName("lbl_ember_start_color")
        self.btn_ember_end_color = QtWidgets.QPushButton(self.tab_ember)
        self.btn_ember_end_color.setGeometry(QtCore.QRect(260, 10, 60, 40))
        self.btn_ember_end_color.setAutoFillBackground(False)
        self.btn_ember_end_color.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 255, 255, 255));\n"
"background-color: rgb(0, 0, 0);")
        self.btn_ember_end_color.setText("")
        self.btn_ember_end_color.setProperty("color", QtGui.QColor(0, 0, 0))
        self.btn_ember_end_color.setObjectName("btn_ember_end_color")
        self.lbl_ember_end_color = QtWidgets.QLabel(self.tab_ember)
        self.lbl_ember_end_color.setGeometry(QtCore.QRect(170, 20, 81, 21))
        self.lbl_ember_end_color.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_ember_end_color.setWordWrap(True)
        self.lbl_ember_end_color.setObjectName("lbl_ember_end_color")
        self.sb_ember_frames = QtWidgets.QSpinBox(self.tab_ember)
        self.sb_ember_frames.setGeometry(QtCore.QRect(258, 70, 61, 29))
        self.sb_ember_frames.setMinimum(1)
        self.sb_ember_frames.setMaximum(999)
        self.sb_ember_frames.setObjectName("sb_ember_frames")
        self.lbl_ember_frames = QtWidgets.QLabel(self.tab_ember)
        self.lbl_ember_frames.setGeometry(QtCore.QRect(110, 70, 141, 25))
        self.lbl_ember_frames.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_ember_frames.setObjectName("lbl_ember_frames")
        self.tabs_ani.addTab(self.tab_ember, "")
        self.cb_default = QtWidgets.QCheckBox(Form)
        self.cb_default.setGeometry(QtCore.QRect(220, 160, 111, 26))
        self.cb_default.setObjectName("cb_default")
        self.sb_num_leds = QtWidgets.QSpinBox(Form)
        self.sb_num_leds.setGeometry(QtCore.QRect(110, 160, 49, 29))
        self.sb_num_leds.setVisible(False)
        self.sb_num_leds.setObjectName("sb_num_leds")
        self.lbl_num_leds = QtWidgets.QLabel(Form)
        self.lbl_num_leds.setGeometry(QtCore.QRect(10, 165, 91, 20))
        self.lbl_num_leds.setVisible(False)
        self.lbl_num_leds.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_num_leds.setObjectName("lbl_num_leds")
        self.lbl_fps = QtWidgets.QLabel(Form)
        self.lbl_fps.setGeometry(QtCore.QRect(10, 195, 91, 20))
        self.lbl_fps.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_fps.setObjectName("lbl_fps")
        self.sb_fps = QtWidgets.QSpinBox(Form)
        self.sb_fps.setGeometry(QtCore.QRect(110, 190, 49, 29))
        self.sb_fps.setMinimum(1)
        self.sb_fps.setMaximum(240)
        self.sb_fps.setProperty("value", 30)
        self.sb_fps.setObjectName("sb_fps")

        self.retranslateUi(Form)
        self.tabs_ani.setCurrentIndex(0)
        self.btn_display.clicked.connect(Form.send_cmd)
        self.btn_solid_color.clicked.connect(Form.solid_set_color)
        self.btn_ember_start_color.clicked.connect(Form.ember_set_start_color)
        self.btn_ember_end_color.clicked.connect(Form.ember_set_end_color)
        self.sb_ember_frames.valueChanged['int'].connect(Form.ember_set_frames)
        self.tabs_ani.tabBarClicked['int'].connect(Form.select_ani)
        self.cb_default.clicked['bool'].connect(self.sb_num_leds.setVisible)
        self.cb_default.clicked['bool'].connect(self.lbl_num_leds.setVisible)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.btn_display.setText(_translate("Form", "Display"))
        self.lbl_solid_color.setText(_translate("Form", "Color"))
        self.tabs_ani.setTabText(self.tabs_ani.indexOf(self.tab_solid), _translate("Form", "Solid"))
        self.lbl_ember_start_color.setText(_translate("Form", "Start Color"))
        self.lbl_ember_end_color.setText(_translate("Form", "End Color"))
        self.sb_ember_frames.setToolTip(_translate("Form", "This is the number of frames to transition between one color and back"))
        self.lbl_ember_frames.setText(_translate("Form", "Frames to Transition"))
        self.tabs_ani.setTabText(self.tabs_ani.indexOf(self.tab_ember), _translate("Form", "Ember"))
        self.cb_default.setText(_translate("Form", "Make default"))
        self.lbl_num_leds.setText(_translate("Form", "Num of LEDs"))
        self.lbl_fps.setText(_translate("Form", "FPS"))

