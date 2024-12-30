from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QGridLayout, QLabel
)
from PySide6.QtGui import QPixmap, QPalette, QBrush, QPainter
from PySide6.QtCore import Qt,QRect, QTimer
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl
import sys


class ThirdWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        background_image_path='thirdPage.png'
        pixmap = QPixmap(background_image_path)
        if pixmap.isNull():
            QMessageBox.critical(self, "Error", f"Failed to load background image: {background_image_path}")
            sys.exit(1)

        self.setFixedSize(pixmap.width(), pixmap.height())
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)

        self.setWindowTitle("Third Window")
        
        self.video_preview = QLabel("[Video Preview Area]", self)
        self.video_preview.setGeometry(310, 45, 721, 405)  # x, y, width, height
        self.video_preview.setStyleSheet("background-color: #cccccc; border: 1px solid #999; font-size: 14px;")
        self.video_preview.setAlignment(Qt.AlignCenter)
        
        self.finishButton = QPushButton("HOME",self)
        self.finishButton.setText("RETURN HOME")
        self.finishButton.setGeometry(740, 485, 270, 60)  # x, y, width, height
        
        self.finishButton.setStyleSheet("""
            QPushButton {
                font-family: Muli;  
                font-size: 30px;
                font-weight: bold;
                color: white;
                background-color:  #00a181;
                padding: 10px;
            }
            QPushButton {border-radius: 30px;}
            QPushButton:hover {
                background-color: #7ed957;
                color: #004651;
            }
        """)
        self.finishButton.clicked.connect(self.confirm)
        
    def confirm(self):
        self.close()
        
    
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
    window = ThirdWindow()
    window.show()
    sys.exit(app.exec())
    
    