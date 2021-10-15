
import sqlite3

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtGui import QImage, QPixmap ,QIcon
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSlot, QTimer, QDate, Qt
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidgetItem, QApplication, QMainWindow ,QInputDialog, QLineEdit
import cv2
import face_recognition
import numpy as np
import datetime
import os
import time
import sys
#from mainwindow import Ui_Dialog
from visitor_window import Ui_visitorDialog
from admin_window import Ui_Admin_Dialog

class Ui_OutputDialog(QDialog):
    def __init__(self):
        super(Ui_OutputDialog, self).__init__()
        loadUi("./outputwindow.ui", self)

        #Update time
        now = QDate.currentDate()
        current_date = now.toString('ddd dd MMMM yyyy')
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.Date_Label.setText(current_date)
        self.Time_Label.setText(current_time)
        self.start()
        self.buttonHandle()
        self.image = None
        self.img =None
        self.timer = QTimer(self)  # Create Timer
    def buttonHandle(self):
        self.visitorButton.clicked.connect(self.visitor)
        self.adminButton.clicked.connect(self.admin)
        self.residentBtn.clicked.connect(self.residentAccess)

    def startReg(self):
        self.timer.timeout.connect(self.displayImage2)  # Connect timeout to the output function
        self.timer.start(50)  # emit the timeout() signal at x=10ms

    def visitor(self):
        ret , self.img  = self.capture.read()
        self.timer.stop()
       # self.visitor_()  # Create and open new output window
        self.insertlog('visitor','Visitor req Access')
        self._new_window1 = Ui_visitorDialog()
        self._new_window1.show()

    def admin(self):
        self.timer.stop()
    # Create and open new output window
        if self. getInputPassword() == "1234":

            self._new_window2 = Ui_Admin_Dialog()
            self._new_window2.show()


    @pyqtSlot()
    def start(self):
        self.timer2=QTimer(self)
        path = 'users'
        if not os.path.exists(path):
            os.mkdir(path)
        # known face encoding and known face name list
        images = []
        self.class_names = []
        self.encode_list = []
        self.TimeList1 = []
        self.TimeList2 = []
        users_list = os.listdir(path)

        # print(attendance_list)
        ## get user names from photos names
        for cl in users_list:
            cur_img = cv2.imread(f'{path}/{cl}')
            images.append(cur_img)
            self.class_names.append(os.path.splitext(cl)[0])

         # get encoding for the existing users images
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  ## convert color
            boxes = face_recognition.face_locations(img)   # get face location
            encodes_cur_frame = face_recognition.face_encodings(img, boxes)[0]  #get the encoding for the detected face
            # encode = face_recognition.face_encodings(img)[0]
            self.encode_list.append(encodes_cur_frame)

        self.capture = cv2.VideoCapture(0)

    def face_rec_(self, frame, encode_list_known, class_names):
        # face recognition
        faces_cur_frame = face_recognition.face_locations(frame)
        encodes_cur_frame = face_recognition.face_encodings(frame, faces_cur_frame)
        # count = 0
        for encodeFace, faceLoc in zip(encodes_cur_frame, faces_cur_frame):
            match = face_recognition.compare_faces(encode_list_known, encodeFace, tolerance=0.50)
            face_dis = face_recognition.face_distance(encode_list_known, encodeFace)
            name = "unknown"
            best_match_index = np.argmin(face_dis)
            # print("s",best_match_index)
            if match[best_match_index] :

                name = class_names[best_match_index]
                y1, x2, y2, x1 = faceLoc
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y2 - 20), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(frame, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

                if self.getUserPassword(name)== self.getInputPassword() :

                    self.insertlog(name,"Access Granted")
                    self.NameLabel.setStyleSheet("background-color: green")
                    self.StatusLabel.setStyleSheet("background-color: green")
                    self.NameLabel.setText(name)
                    self.StatusLabel.setText('Access Accepted')
                    self.HoursLabel.setText(str(time.strftime("%d %m %Y . %H:%M:%S")))
                    self.timer.stop()
                    # self.showdialog(name)
                    # self.timer2.start(3000)
                else:
                    self.insertlog(name, "Rejected Wrong PIN")
                    self.NameLabel.setStyleSheet("background-color: red")
                    self.StatusLabel.setStyleSheet("background-color: red")

                    self.NameLabel.setText(name)
                    self.StatusLabel.setText('Access Rejected Wrong PIN')
                    self.HoursLabel.setText(str(time.strftime("%d %m %Y . %H:%M:%S")))

            else:
                self.NameLabel.setStyleSheet("background-color: red")
                self.StatusLabel.setStyleSheet("background-color: red")

                self.NameLabel.setText('Unknown')
                self.StatusLabel.setText('Access Rejected')
                self.HoursLabel.setText(str(time.strftime("%d %m %Y . %H:%M:%S")))

        return frame

    def getUserPassword(self, text):
        db = sqlite3.connect('faceAccess.db')
        cursor = db.cursor()
        command = '''SELECT PassCode FROM users WHERE name=? '''
        result = cursor.execute(command, [text]).fetchone()
        #if result:
        password = result[0]
        return password

    def getInputPassword(self):
        text, okPressed = QInputDialog.getText(self, "Get PIN", "Enter Your PIN:", QLineEdit.Normal, "")
        if okPressed and text != '':
            return text

    def insertlog(self,name,status_):
        time_ = str(time.strftime("%Y %m %d %H %M %S"))
        #print(time_)
        filename = time_.replace(':', ' ')
        #print(filename)
        cv2.imwrite("photos\{0}.jpg".format(filename), self.img)
        db = sqlite3.connect('faceAccess.db')
        cursor = db.cursor()
        name_ = name

        row = (name_,time_,time_, status_)
        command = '''REPLACE INTO log (name ,time,photo,status) VALUES (?,?,?,?)'''
        cursor.execute(command, row)
        db.commit()

    def residentAccess(self):
        self.timer3 =QTimer(self)
        self.timer3.singleShot(15000, self.stopTimer)

        self.timer.timeout.connect(self.update_frame)  # Connect timeout to the output function
        self.timer.start(50)  # emit the timeout() signal at x=50ms
    def stopTimer(self):
        self.timer.stop()
        print('timer stopped')


    def update_frame(self):
        ret, self.image = self.capture.read()
        self.displayImage(self.image, self.encode_list, self.class_names)

    def displayImage(self, image, encode_list, class_names):
        """
        :param image: frame from camera
        :param encode_list: known face encoding list
        :param class_names: known face names
        :return:
        """
        image = cv2.resize(image, (640, 480))
        self.img = image.copy()
        try:
            image = self.face_rec_(image, encode_list, class_names)
        except Exception as e:
            print(e)
        qformat = QImage.Format_Indexed8
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                qformat = QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], qformat)
        outImage = outImage.rgbSwapped()

        #if window == 1:
        self.imgLabel.setPixmap(QPixmap.fromImage(outImage))
        self.imgLabel.setScaledContents(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = Ui_OutputDialog()
    ui.show()
    # app = QApplication(sys.argv)
    # window = MainDialog()
    # window.show()
    sys.exit(app.exec_())