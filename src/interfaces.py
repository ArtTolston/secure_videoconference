# -*- coding: utf-8 -*-

# Form implementation generated from reading src file 'client.src'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread
import pickle

# manual changes
import cv2
import qimage2ndarray

from src.p2p.peer import Peer
from src.handling.handler import  Handler
import json



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(582, 328)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.clientsListWidget = QtWidgets.QListWidget(self.centralwidget)
        self.clientsListWidget.setGeometry(QtCore.QRect(350, 31, 201, 191))
        self.clientsListWidget.setObjectName("clientsListWidget")
        self.updateButton = QtWidgets.QPushButton(self.centralwidget)
        self.updateButton.setGeometry(QtCore.QRect(350, 230, 101, 21))
        self.updateButton.setObjectName("updateButton")
        self.connectButton = QtWidgets.QPushButton(self.centralwidget)
        self.connectButton.setGeometry(QtCore.QRect(460, 230, 91, 21))
        self.connectButton.setObjectName("connectButton")
        self.cipherBox = QtWidgets.QComboBox(self.centralwidget)
        self.cipherBox.setGeometry(QtCore.QRect(460, 260, 91, 21))
        self.cipherBox.setObjectName("cipherBox")
        self.cipherBox.addItem("")
        self.cipherBox.addItem("")
        self.videoLabel = QtWidgets.QLabel(self.centralwidget)
        self.videoLabel.setGeometry(QtCore.QRect(34, 29, 271, 191))
        self.videoLabel.setText("")
        self.videoLabel.setObjectName("videoLabel")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 582, 18))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # manual changes

        self.handler = Handler()

        self.camera = cv2.VideoCapture(0)
        self.fps = 30
        self.timer = QtCore.QTimer()
        self.video_size = QtCore.QSize(self.videoLabel.geometry().width(), self.videoLabel.geometry().height())
        self.setup_camera(self.fps)

        self.choosed_address = None
        self.is_video_started = False

        self.updateButton.clicked.connect(self.update)
        self.clientsListWidget.itemClicked.connect(self.save_address)
        self.connectButton.clicked.connect(self.connect)

        # Create a QThread object
        self.peer = Peer(handler=self.handler)
        self.peer.start()

    def setup_camera(self, fps):
        self.camera.set(3, self.video_size.width())
        self.camera.set(4, self.video_size.height())

        #self.timer.timeout.connect(self.display_video_stream)
        self.timer.timeout.connect(self.send_video_stream)
        self.timer.start(int(1000 / self.fps))

    def display_video_stream(self):
        ret, frame = self.camera.read()

        if not ret:
            return False

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.flip(frame, 1)
        image = qimage2ndarray.array2qimage(frame)

        # frame = self.peer.udp_get_receive_queue()

        self.videoLabel.setPixmap(QtGui.QPixmap.fromImage(image))

    def send_video_stream(self):
        if self.is_video_started is False:
            return
        ret, frame = self.camera.read()

        if not ret:
            return False

        bframe = pickle.dumps(frame)
        self.handler.get_crypto()
        self.peer.udp_put_send_queue(bframe)

    def update(self):
        active_clients_addresses = self.peer.find()
        for active_client_address in active_clients_addresses:
            self.clientsListWidget.addItem(str(active_client_address))

    def connect(self):

        if self.is_video_started is True:
            return
        request = {}
        request["code"] = "START1"
        cipher = self.cipherBox.currentText()
        if cipher == "Diffie-Hellman":
            request["algorithm"] = "DH"
            pub_key = self.handler.get_crypto().gen_dh_pub_key()
            request["pub_key"] = pub_key
        elif cipher == "Public key exchange":
            request["algorithm"] = "PKI"
            pub_key = self.handler.get_crypto().rsa_get_pub_key()
            request["pub_key"] = pub_key
        else:
            pass

        try:
            self.peer.tcp_connect(self.choosed_address, json.dumps(request).encode(), self.handler.tcp_handler)
        except OSError:
            print("tcp connection error")
            return

        self.is_video_started = True


    def finish(self):
        self.peer.is_active = False


    def save_address(self, address):
        self.choosed_address = address.text()


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.updateButton.setText(_translate("MainWindow", "Update"))
        self.connectButton.setText(_translate("MainWindow", "Connect"))
        self.cipherBox.setItemText(0, _translate("MainWindow", "Public key exchange"))
        self.cipherBox.setItemText(1, _translate("MainWindow", "Diffie-Hellman"))
