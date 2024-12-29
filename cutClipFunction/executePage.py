from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QGridLayout, QLabel
)
from PySide6.QtGui import QPixmap, QPalette, QBrush, QPainter
from PySide6.QtCore import Qt,QRect, QTimer
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl
import sys


class SecondWindow(QWidget):
    
    def __init__(self):
        super().__init__()
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
            QPushButton {border-radius: 80px;}s
            QPushButton:hover {
                background-color: #7ed957;
                color: #004651;
            }
        """)
        self.finishButton.clicked.connect(self.confirm)
    def confirm(self):
        print("yes")
    
    def add_video(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.avi *.mov *.mkv)")
        if filename:
            self.video_path=filename
            QMessageBox.information(self, "Video Added", f"You selected: {filename}")

            self.video_player = QMediaPlayer(self)
            self.video_widget = QVideoWidget(self)

            self.video_widget.setGeometry(620, 222, 300, 200)
            self.video_widget.show()

            self.video_player.setVideoOutput(self.video_widget)
            self.video_player.setSource(QUrl.fromLocalFile(filename))
            self.video_player.play()
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SecondWindow()
    window.show()
    sys.exit(app.exec())
    
    