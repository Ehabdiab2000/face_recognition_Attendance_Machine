import sqlite3
import random
from twilio.rest import Client
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QTimer, QDate, Qt
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidgetItem ,QPushButton,QLineEdit,QGridLayout
import cv2
import face_recognition
import numpy as np
import datetime
import os
import csv
import time


class Ui_visitorDialog(QDialog):


    def __init__(self):
        super(Ui_visitorDialog, self).__init__()
        loadUi("./visitorwindow.ui", self)
        self.buttonHandle()
        self.otp = None
        self.timer1 =  QTimer(self)
        self.trials =0

    def buttonHandle(self):
        self.reqButton.clicked.connect(self.sendOTB)
        self.openButton.clicked.connect(self.openDoor)


    def sendOTB(self):
        self.reqButton.setEnabled(False)
        name= self.nameText.text()
        tel = self.telText.text()
        # Generate rendom OTP
        self.otp = random.randint(1000, 9999)
        print(self.otp)
        # send SMS
        # Your Account SID from twilio.com/console
        account_sid = "ACa3ff54b9b175d604fc6cec2dc454dd1c"
        # Your Auth Token from twilio.com/console
        auth_token = "131e144b2e9ede32940fb41bf68e4063"

        client = Client(account_sid, auth_token)

        self.trials =3
        self.timer1.timeout.connect(self.stoptrials)  # Connect timeout to the output function
        self.timer1.start(60000)
        message = client.messages.create(
            to="+971559983045",

            from_="+12067454268",
            body="your Friend "+name +'  tel: '+tel+ ' requesting access , please send him this code:' + str(self.otp))

    def stoptrials(self):
        self.trials = 0
        self.openButton.setEnabled(False)

    def openDoor(self):
        if self.trials > 0:
            if len(self.otpText.text())==4 :
                if str(self.otp) == self.otpText.text():
                    self.doorOpen()
                    self.insertlog('visitor', 'Visitor Access Granted')
            else:
                print('wrong OTP')
                self.insertlog('visitor', 'Visitor Access Rejected Wrong OTP')
            self.trials = self.trials -1
        if self.trials == 0 :
            self.openButton.setEnabled(False)
        print(self.trials)


    def doorOpen(self):
        print('door opened')

    def insertlog(self,name,status_):
        time_ = str(time.strftime("%Y %m %d %H %M %S"))
        #print(time_)
        filename = time_.replace(':', ' ')
        #print(filename)
        self.capture = cv2.VideoCapture(0)
        ret, self.img = self.capture.read()
        cv2.imwrite("photos\{0}.jpg".format(filename), self.img)
        db = sqlite3.connect('faceAccess.db')
        cursor = db.cursor()
        name_ = name

        row = (name_,time_,time_, status_)
        command = '''REPLACE INTO log (name ,time,photo,status) VALUES (?,?,?,?)'''
        cursor.execute(command, row)
        db.commit()
