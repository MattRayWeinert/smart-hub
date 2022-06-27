#rtsp://admin:Mandarin53$@192.168.1.220:554//h264Preview_01_main
#rtsp://admin:123456@192.168.1.243:554//h264Preview_01_main
from cmath import rect
import socket
import sys
import os
import cv2
import numpy as np
import imutils
import time
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QRect
from PyQt5.QtWidgets import (
    QWidget, 
    QApplication, 
    QLabel, 
    QVBoxLayout, 
    QFormLayout, 
    QLineEdit,
    QPushButton,
    QStackedLayout,
    QTableWidget,
    QPushButton,
    QAbstractItemView,
    QListWidget,
    QListWidgetItem,
    QHBoxLayout
)
 
class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'SmartHub'
        self.left = 0
        self.top = 0
        self.stream_on = False
        self.display_width = 1024
        self.display_height = 600
        self.fps = 60
        self.initUI()
        self.rtsp_url = self.retrieve_rtsp_url()
        self.display_rtsp_form()
        self.recording = (VideoRecording)
        self.live = (VideoStream)
        self.type_of_stream = "home"
 
    def initUI(self):
        # self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.display_width, self.display_height)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.createTable()
 
        # Add box layout, add table to box layout and add box layout to widget
        self.layout = QStackedLayout()
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)
 
        self.initialize_rtsp_stream_layout()
 
        # Show widget
        self.show()
 
    def createTable(self):
        # Create first widget for table (left column)
        self.rtsp_form = QWidget()
        self.rtsp_form_layout = QFormLayout() # Layout to place the RTSP credential form
        self.rtsp_form_layout.setAlignment(Qt.AlignHCenter)
        self.user_input_username = QLineEdit("")
        self.user_input_password = QLineEdit("")
        self.user_input_password.setEchoMode(QLineEdit.Password)
        self.user_input_ip = QLineEdit("")
        self.submit_btn = QPushButton("Submit")
        self.rtsp_username = QLabel("Enter Username:")
        self.rtsp_password = QLabel("Enter Password:")
        self.submit_btn.clicked.connect(lambda:self.submit_btn_clicked())
        self.rtsp_form_layout.addRow(self.rtsp_username)
        self.rtsp_form_layout.addRow(self.user_input_username)
        self.rtsp_form_layout.addRow(self.rtsp_password)
        self.rtsp_form_layout.addRow(self.user_input_password)
        self.rtsp_form_layout.addRow(self.submit_btn)
        self.rtsp_form_layout.setFormAlignment(Qt.AlignVCenter)
        self.rtsp_form.setStyleSheet('width: 500px;')
        self.rtsp_form.setLayout(self.rtsp_form_layout)
 
        # Create second widget for table (middle column)
#         self.im = QPixmap("./dst/image.png")
        self.im = QPixmap(".//dst//image.png")
        self.label = QLabel()
        self.label.setPixmap(self.im)
 
        # Create third widget for table (right column)
        self.list_widget = QListWidget()
#         arr = os.listdir('/home/seniordesign/Desktop/smarthub/videos')
        arr = os.listdir('C:\\Users\\matth\\Desktop\\videos')
        for file in arr:
            QListWidgetItem(file, self.list_widget)
        self.list_widget.clicked.connect(self.list_item_clicked)
 
        # Creating the table of widgets
        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(1)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setCellWidget(0, 0, self.rtsp_form)
        self.tableWidget.setCellWidget(0, 1, self.label)
        self.tableWidget.setCellWidget(0, 2, self.list_widget)
        self.tableWidget.setColumnWidth(0, 340)
        self.tableWidget.setRowHeight(0, 600)
        self.tableWidget.setColumnWidth(1, 342)
        self.tableWidget.setRowHeight(1, 600)
        self.tableWidget.setColumnWidth(2, 340)
        self.tableWidget.setRowHeight(2, 600)
 
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setFocusPolicy(Qt.NoFocus)
        self.tableWidget.setSelectionMode(QAbstractItemView.NoSelection)
 
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
 
    def initialize_rtsp_stream_layout(self):
        self.type_of_stream = "home"
        self.footage = QWidget()
 
        self.back_button = QPushButton(self)
        self.back_button.setVisible(False)
        self.back_button.setGeometry(200, 150, 200, 40)
        self.back_button.clicked.connect(self.back_button_clicked)
        self.back_button.setIcon(QtGui.QIcon(".//dst//back.png"))
        self.back_button.setIconSize(QtCore.QSize(32, 32))
        self.back_button.setStyleSheet("border-radius: 15px; color: black; font-size: 25px; width: 50px;")
 
        self.pause_button = QPushButton(self)
        self.pause_button.setVisible(False)
        self.pause_button.clicked.connect(self.pause_button_clicked)
        self.pause_button.setIcon(QtGui.QIcon(".//dst//pause.png"))
        self.pause_button.setIconSize(QtCore.QSize(32, 32))
        self.pause_button.setStyleSheet("border-radius: 15px; color: black; font-size: 25px;")
 
        self.play_button = QPushButton(self)
        self.play_button.setVisible(False)
        self.play_button.clicked.connect(self.play_button_clicked)
        self.play_button.setIcon(QtGui.QIcon(".//dst//play.png"))
        self.play_button.setIconSize(QtCore.QSize(32, 32))
        self.play_button.setStyleSheet("border-radius: 15px; color: black; font-size: 25px;")
 
        self.fast_forward = QPushButton(self)
        self.fast_forward.setVisible(False)
        self.fast_forward.clicked.connect(self.fast_forward_button_clicked)
        self.fast_forward.setIcon(QtGui.QIcon(".//dst//fast-forward.png"))
        self.fast_forward.setIconSize(QtCore.QSize(32, 32))
        self.fast_forward.setStyleSheet("border-radius: 15px; color: black; font-size: 25px;")
 
        self.rewind_button = QPushButton(self)
        self.rewind_button.setVisible(False)
        self.rewind_button.clicked.connect(self.rewind_button_clicked)
        self.rewind_button.setIcon(QtGui.QIcon(".//dst//rewind.png"))
        self.rewind_button.setIconSize(QtCore.QSize(32, 32))
        self.rewind_button.setStyleSheet("border-radius: 15px; color: black; font-size: 25px;")

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.rewind_button)
        self.button_layout.addWidget(self.back_button)
        self.button_layout.addWidget(self.play_button)
        self.button_layout.addWidget(self.pause_button)
        self.button_layout.addWidget(self.fast_forward)
 
        self.image_label = QLabel(self) # Label used to hold the image
        self.image_label.resize(self.display_width, self.display_height)
        self.footage_layout = QVBoxLayout() # Layout to place RTSP stream footage
        self.footage_layout.setContentsMargins(0, 0, 0, 0)
        self.footage_layout.addWidget(self.image_label)
        self.footage_layout.setAlignment(Qt.AlignCenter)
        self.footage_layout.addLayout(self.button_layout)
        self.footage.setLayout(self.footage_layout)
        self.layout.addWidget(self.footage)
        self.play_button.setVisible(True)
        self.pause_button.setVisible(True)
        self.rewind_button.setVisible(True)
        self.back_button.setVisible(True)
        self.fast_forward.setVisible(True)
    
    def display_rtsp_form(self):
        self.layout.setCurrentIndex(0)
 
    def display_rtsp_stream(self):
        self.layout.setCurrentIndex(1) # Makes this layout visible
        self.play_button.setVisible(False)
        self.pause_button.setVisible(False)
        self.fast_forward.setVisible(False)
        self.rewind_button.setVisible(False)
        self.live = self.thread = VideoStream(self.rtsp_url, self.image_label, self.display_width, self.display_height) # Starts the RTSP stream
        self.thread.change_pixels_obj.connect(self.thread.update_image)
        self.thread.start()
 
    def display_rtsp_recording(self):
        self.layout.setCurrentIndex(1) # Makes this layout visible
        self.play_button.setVisible(True)
        self.pause_button.setVisible(True)
        self.fast_forward.setVisible(True)
        self.rewind_button.setVisible(True)
        self.recording = self.thread = VideoRecording(self.rtsp_url, self.image_label, self.display_width, self.display_height, self.fps) # Starts the RTSP stream
        self.thread.change_pixels_obj.connect(self.thread.update_image)
        self.thread.start()
 
    def submit_btn_clicked(self):
        self.user_input = "rtsp://" + self.user_input_username.text() + ":" + self.user_input_password.text() + "@192.168.1.243:554//h264Preview_01_main"
        self.type_of_stream = "live"
        self.store_user_input()
        self.display_rtsp_stream()
 
    def list_item_clicked(self):
        self.type_of_stream = "recording"
        self.item = self.list_widget.currentItem().text()
        self.store_item_input()
        self.display_rtsp_recording()
 
    def pause_button_clicked(self):
        self.recording.pause = True
 
    def play_button_clicked(self):
        self.recording.play = True
 
    def back_button_clicked(self):
        self.layout.setCurrentIndex(0)
        print(self.type_of_stream)
        if(self.type_of_stream == "recording"):
            self.recording.close_stream()
        if(self.type_of_stream == "live"):
            self.live.close_stream()
 
    def rewind_button_clicked(self):
        self.recording.rewind = True
 
    def fast_forward_button_clicked(self):
        self.recording.fps = int(self.recording.fps / 2)
 
    def store_item_input(self):
#         self.rtsp_url = self.save_rtsp_url('/home/seniordesign/Desktop/smarthub/videos/' + self.item)
        self.rtsp_url = self.save_rtsp_url('C:\\Users\\matth\Desktop\\videos\\' + self.item)
        
    def store_user_input(self):
        self.rtsp_url = self.save_rtsp_url(self.user_input)
 
    def retrieve_rtsp_url(self):
#         if(os.path.exists("/home/seniordesign/Desktop/smarthub/dst/credentials.txt")):
        if(os.path.exists("C://Users//matth//Desktop//dst//credentials.txt")):
#             file = open("/home/seniordesign/Desktop/smarthub/dst/credentials.txt", "r")
            file = open("C://Users//matth//Desktop//dst//credentials.txt", "r")
            rtsp_url = file.read()
            file.close()
            return rtsp_url
        else:
            return ""
 
    def save_rtsp_url(self, rtsp_url):
#         file = open("/home/seniordesign/Desktop/smarthub/dst/credentials.txt", "w")
        file = open("C://Users//matth//Desktop//dst//credentials.txt", "w")
        try:
            rtsp_url.index('rtsp')
        except ValueError:
            print("substring not found")
        else:
            file.write(rtsp_url)
        file.close()
        return rtsp_url
 
class VideoStream(QThread, object):
    # When placed inside init, the code code does not work
    change_pixels_obj = pyqtSignal(np.ndarray) # Object for updating frames
 
    def __init__(self, rtsp_str, image_label, display_width, display_height):
        super().__init__()
        self.rtsp_str = rtsp_str
        self.image_label = image_label
        self.display_width = 900
        self.display_height = 540
 
        # Capture RTSP stream
        while(True):
            self.cap = cv2.VideoCapture(self.rtsp_str)
            if(self.cap.isOpened()):
                break
    
    # Function gets called every time VideoStream is instantiated
    def run(self):
        # Initializing the HOG person detector
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
 
        frame_width = int(self.cap.get(3))
        frame_height = int(self.cap.get(4))
        size = (frame_width, frame_height)
 
        ret, frame = self.cap.read()
 
        # Video codec and output destination - filename formatted: MonthDayYear - HourMinuteSecond
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#         out = cv2.VideoWriter('/home/seniordesign/Desktop/smarthub/videos/' + time.strftime("%m%d%Y-%H%M%S") + '.mp4', fourcc, 20.0, size)
        out = cv2.VideoWriter('C://Users//matth//Desktop//videos//' + time.strftime("%m%d%Y-%H%M%S") + '.avi', fourcc, 20.0, size)
        
        def detect_human(detection_frame):
            # Detecting all the regions in the Image that has a pedestrians inside it
            # For speedup, increase scale in range (1.0 - 1.5), increase winStride 
            (regions, _) = hog.detectMultiScale(detection_frame, winStride=(10, 10), padding=(4, 4), scale=1.4)
            if (len(regions) == 1): # len == 0 when no detection found
                print("Human Detected!  Results: " + str(regions))
                
        while True:
            ret, frame = self.cap.read()
            if ret:
                # Commented the lines below since they are slowing down the app
                # TODO: Create a new thread for each segment of work 
                # Resize image for better detection
                detection_frame = imutils.resize(frame, width=min(400, frame.shape[1]))
                detect_human(detection_frame)
                self.change_pixels_obj.emit(frame)
                out.write(frame)
 
    # Function gets called for each new frame
    @pyqtSlot(np.ndarray)
    def update_image(self, img):
        qt_img = self.convert_image_to_qt_image(img)
        self.image_label.setPixmap(qt_img)
    
    def convert_image_to_qt_image(self, img):
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Converts opencv image to QPixmap image
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio))
 
    # Function gets called when user exits app
    def close_stream(self):
        # self.cap.release()
        self.cap.release()
        cv2.destroyAllWindows()
        print("RTSP stream closed")
 
class VideoRecording(QThread, object):
    # When placed inside init, the code code does not work
    change_pixels_obj = pyqtSignal(np.ndarray) # Object for updating frames
 
    def __init__(self, rtsp_str, image_label, display_width, display_height, fps):
        super().__init__()
        self.rtsp_str = rtsp_str
        self.image_label = image_label
        self.display_width = 852 # 1024
        self.display_height = 480 # 600
        self.fps = fps
        self.frame_list = []
        self.counter = 0
        self.pause = False
        self.play = False
        self.rewind = False
        self.total_frames = 0
        self.chopped_frames = len(self.frame_list) - 1
        self.chopped_frames_temp = len(self.frame_list) - 1
        self.recap_frames = 0
        self.recap = False
 
        # Capture RTSP stream
        while(True):
            self.cap = cv2.VideoCapture(self.rtsp_str)
            if(self.cap.isOpened()):
                break
 
    # Function gets called every time VideoStream is instantiated
    def run(self):
        # Initializing the HOG person detector
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
                
        while True:
            ret, frame = self.cap.read()
            self.chopped_frames_temp = len(self.frame_list) - 1
            while self.pause == True:
                if(self.play == True):
                    self.pause = False
                    self.play = False
                    break
 
            while self.rewind:
                # if(self.chopped_frames == 0):
                #     self.rewind == False
                #     break
                imutils.resize(self.frame_list[self.chopped_frames_temp], width=min(400, frame.shape[1]))
                self.change_pixels_obj.emit(self.frame_list[self.chopped_frames_temp])
                if cv2.waitKey(self.fps) & 0xFF == ord('q'):
                    break
                if ord('p'):
                    cv2.waitKey(-1)
                if(self.chopped_frames_temp >= 2):
                    self.chopped_frames_temp = self.chopped_frames_temp - 1
                if(self.chopped_frames_temp == 1):
                    self.chopped_frames = self.chopped_frames_temp
                    self.recap_frames = self.chopped_frames
                    self.rewind = False
                    self.pause = True
                    self.play = False
                    self.recap = True
                    break
                if(self.play == True):
                    self.chopped_frames = self.chopped_frames_temp
                    self.recap_frames = self.chopped_frames
                    self.rewind = False
                    self.play = False
                    self.recap = True
                    break
 
            while self.pause == True:
                if(self.play == True):
                    self.pause = False
                    self.play = False
                    break
 
            while self.recap:
                imutils.resize(self.frame_list[self.recap_frames], width=min(400, frame.shape[1]))
                self.change_pixels_obj.emit(self.frame_list[self.recap_frames])
                if cv2.waitKey(self.fps) & 0xFF == ord('q'):
                    break
                if ord('p'):
                    cv2.waitKey(-1)
                self.recap_frames += 1
                if(self.recap_frames + 1 == self.total_frames):
                    self.recap = False
                    break
 
            while self.pause == True:
                if(self.play == True):
                    self.pause = False
                    self.play = False
                    break
 
            if ret and (self.recap == False):
                # Resize image for better detection
                imutils.resize(frame, width=min(400, frame.shape[1]))
                self.change_pixels_obj.emit(frame)
                if cv2.waitKey(self.fps) & 0xFF == ord('q'):
                    break
                if ord('p'):
                # if cv2.waitKey(1) == ord('p'):
                    cv2.waitKey(-1)
                self.frame_list.append(frame)
                self.total_frames += 1
            
            while self.pause == True:
                if(self.play == True):
                    self.pause = False
                    self.play = False
                    break
 
        # for frame in self.frame_list:
        #     cv2.imshow("Frame", frame)
        #     if cv2.waitKey(25) and 0xFF == ord("q"):
        #         break
 
    # Function gets called for each new frame
    @pyqtSlot(np.ndarray)
    def update_image(self, img):
        qt_img = self.convert_image_to_qt_image(img)
        self.image_label.setPixmap(qt_img)
    
    def convert_image_to_qt_image(self, img):
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # Converts opencv image to QPixmap image
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        return QPixmap.fromImage(qt_image.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio))
 
    # Function gets called when user exits app
    def close_stream(self):
        # self.cap.release()
        self.cap.release()
        cv2.destroyAllWindows()
        print("RTSP stream closed")
 
def exit_app(q_app, app):
    q_app.exec_() # Function's execution pauses here until user exits app 
    app.thread.close_stream() # Closes RTSP stream 
    sys.exit() # Exits app
 
def main():
    q_app = QApplication(sys.argv)
    app = App()
    app.show() 
    exit_app(q_app, app)
 
if __name__=="__main__":
    main()