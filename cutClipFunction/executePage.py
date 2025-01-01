from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QGridLayout, QLabel
)
import cv2 as cv
from PySide6.QtGui import QPixmap, QPalette, QBrush, QPainter,QImage
from PySide6.QtCore import Qt,QRect, QTimer
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl
import sys
from thirdPage import ThirdWindow



class SecondWindow(QWidget):
    isClose = False

    def __init__(self):
        super().__init__()
        self.cap = None  # OpenCV VideoCapture object
        # self.timer = QTimer(self)  # Timer để tự động cập nhật frame
        # self.timer.timeout.connect(self.update_frame)  # Liên kết với phương thức update_frame
        self.initUI()

    def initUI(self):
        
        
        background_image_path='secondWinn.png'
        pixmap = QPixmap(background_image_path)
        if pixmap.isNull():
            QMessageBox.critical(self, "Error", f"Failed to load background image: {background_image_path}")
            sys.exit(1)

        self.setFixedSize(pixmap.width(), pixmap.height())
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)

        self.setWindowTitle("Second Window")
        
        self.video_preview = QLabel("[Video Preview Area]", self)
        self.video_preview.setGeometry(190, 30, 750, 421)  # x, y, width, height
        self.video_preview.setStyleSheet("background-color: #cccccc; border: 1px solid #999; font-size: 14px;")
        self.video_preview.setAlignment(Qt.AlignCenter)
        
        self.finishButton = QPushButton("FINISH NOW",self)
        self.finishButton.setText("FINISH \nNOW")
        self.finishButton.setGeometry(860, 360, 160, 160)  # x, y, width, height
        self.finishButton.setStyleSheet("""
            QPushButton {
                font-family: Muli;  
                font-size: 35px;
                font-weight: bold;
                color: white;
                background-color:  #00a181;
                padding: 10px;
            }
            QPushButton {border-radius: 80px;}
            QPushButton:hover {
                background-color: #7ed957;
                color: #004651;
            }
        """)
        self.finishButton.clicked.connect(self.confirm)
        

    def confirm(self):
        self.isClose = True
        self.win=ThirdWindow("D:\\PyLesson\\Ellish_BirdOfFeatther.mp4")
        self.win.show()
        self.close()
        
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SecondWindow()
    window.show()
    sys.exit(app.exec())
    
    