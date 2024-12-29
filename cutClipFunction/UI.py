from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFileDialog, QMessageBox
from PySide6.QtGui import QPixmap, QPalette, QBrush,QIcon
from PySide6.QtCore import Qt
import sys


style="""
            QPushButton {
                font-family: Muli;  
                font-size: 15px;
                font-weight: bold;
                color: white;
                background-color:  #00a181;
                padding :10px;
            }
            QPushButton {border-radius:3 px;}
            QPushButton:hover {
                background-color: #7ed957;
                color:#004651;
                
            }
           
        """
        
class FaceRecognitionUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set background image and window size
        background_image_path = "D:\\BTL\\Project1_Team8\\background.png"
        self.set_background_and_size(background_image_path)

        self.setWindowTitle("WhereTheFace")

        # Add Images Button
        self.add_images_button = QPushButton("ADD IMAGES HERE", self)
        self.add_images_button.setGeometry(0, 186, 190, 55)  # x, y, width, height
        self.add_images_button.setStyleSheet(style)
        self.add_images_button.clicked.connect(self.add_images)
        
        #change the video button
        
        self.add_images_button = QPushButton("CHANGE THE VIDEO", self)
        self.add_images_button.setGeometry(600, 425, 250, 40)  # x, y, width, height
        self.add_images_button.setStyleSheet(style)
        self.add_images_button.clicked.connect(self.add_video)
        

        # Image Preview Area
        self.image_preview = QLabel("[+]", self)
        self.image_preview.setGeometry(10, 278, 60, 60)  # x, y, width, height
        self.image_preview.setStyleSheet("background-color: #eeeeee; border: 1px solid #ccc; padding: 10px;")
        self.image_preview.setAlignment(Qt.AlignCenter)

        # Add Video Button
        self.add_video_button = QPushButton("ADD VIDEO HERE", self)
        self.add_video_button.setGeometry(750, 101, 200, 55)  # x, y, width, height
        self.add_video_button.setStyleSheet(style)
        self.add_video_button.clicked.connect(self.add_video)

        # Video Preview Area
        self.video_preview = QLabel("[Video Preview Area]", self)
        self.video_preview.setGeometry(620, 222, 300, 200)  # x, y, width, height
        self.video_preview.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color:  #00a181;
                padding : 10px;
                border-radius: 90px;
            }
             
           
        """)
        self.video_preview.setAlignment(Qt.AlignCenter)

        
        
        # launch Button (Circular)
        self.launch_button = QPushButton( self)
        self.launch_button.setGeometry(412, 242, 185, 185)  # x, y, width, height
        self.launch_button.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color:  #00a181;
                border-radius: 90px;  
            }
            QPushButton:hover {
                background-color: #7ed957;
                
            }
        """)
        icon = QIcon("rock3.png")  # Replace with your icon path
        self.launch_button.setIcon(icon)
        self.launch_button.setIconSize(self.launch_button.size()*0.87)
        self.launch_button.clicked.connect(self.show_help)

        

        # # Note Section
        # self.note_label = QLabel("Note: More images, more precise!!\nJust upload 3/8 images, so our program could\nget under 50% of the target face time.", self)
        # self.note_label.setGeometry(50, 350, 200, 100)  # x, y, width, height
        # self.note_label.setStyleSheet("font-size: 12px; padding: 10px;")

    def set_background_and_size(self, image_path):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            QMessageBox.critical(self, "Error", f"Failed to load background image: {image_path}")
            sys.exit(1)

        self.setFixedSize(pixmap.width(), pixmap.height())
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)

    def add_images(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Image Files (*.jpg *.jpeg *.png *.bmp *.gif)")
        if filenames:
            QMessageBox.information(self, "Images Added", f"You selected {len(filenames)} image(s).")
            # Display the first image as a preview
            pixmap = QPixmap(filenames[0])
            pixmap = pixmap.scaled(400, 300, Qt.KeepAspectRatio)
            self.image_preview.setPixmap(pixmap)

    def add_video(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.avi *.mov *.mkv)")
        if filename:
            QMessageBox.information(self, "Video Added", f"You selected: {filename}")
            # Placeholder: You can add functionality to preview video
            self.video_preview.setText(f"Selected Video: {filename}")

    def launch(self):
        QMessageBox.information(self, "Launch", "Launch button clicked! Add your functionality here.")
        
    def show_help(self):
        QMessageBox.information(self, "Help", "This is the help section. Provide guidance to the user here.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceRecognitionUI()
    window.show()
    sys.exit(app.exec())


# tạo  các chức năng cho các button add video, add images, chỉnh sửa view area cho image và video ,
 #chỉnh sửa launch button để kiểm tra input và  dẫn vào trang khác
# thêm Note section