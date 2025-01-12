import sys
<<<<<<< HEAD
from module.input import inputProcess
from module.YOLOverse import execute
=======

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QBrush, QIcon, QPalette, QPixmap
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (QApplication, QFileDialog, QGridLayout, QLabel,
                               QMessageBox, QPushButton, QVBoxLayout, QWidget)

from cutClipFunction.input import faceInInput
from input import inputProcess
>>>>>>> pr/2
from thirdPage import ThirdWindow
from YOLOverse import execute

# from trackFunction import tracker


style = """
            QPushButton {
                font-family: Muli;  
                font-size: 15px;
                font-weight: bold;
                color: white;
                background-color:  #00a181;
                padding: 10px;
            }
            QPushButton {border-radius: 27px;}
            QPushButton:hover {
                background-color: #7ed957;
                color: #004651;
            }
        """


class FaceRecognitionUI(QWidget):
    def __init__(self):
        super().__init__()
        self.image_paths = []  # Mảng lưu trữ đường dẫn ảnh
        self.initUI()
        self.video_path=""

    def initUI(self):
        # Set background image and window size
        background_image_path = "background.png"
        self.set_background_and_size(background_image_path)
        self.setWindowTitle("WhereTheFace")

        # Add Images Button
        self.add_images_button = QPushButton("ADD IMAGES HERE", self)
        self.add_images_button.setGeometry(-20, 186, 205, 55)  # x, y, width, height
        self.add_images_button.setStyleSheet(style)
        self.add_images_button.clicked.connect(self.add_images)

        # Image Grid Area
        self.image_preview = QWidget(self)
        self.image_preview.setGeometry(0, 245, 350, 200)  # Kích thước vừa phải cho lưới 2x4
        self.image_preview.setStyleSheet("background-color: #eeeeee; border: 1px solid #ccc;border-radius: 10px")
        self.grid_layout = QGridLayout(self.image_preview)  # Lưới hiển thị ảnh
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.grid_layout.setSpacing(10)
        self.init_empty_grid()

        # Add Video Button
        self.add_video_button = QPushButton("ADD VIDEO HERE", self)
        self.add_video_button.setGeometry(755, 101, 210, 55)  # x, y, width, height
        self.add_video_button.setStyleSheet(style)
        self.add_video_button.clicked.connect(self.add_video)

        # Video Preview Area
        self.video_preview = QLabel("[Video Preview Area]", self)
        self.video_preview.setGeometry(620, 222, 300, 200)  # x, y, width, height
        self.video_preview.setStyleSheet("background-color: #cccccc; border: 1px solid #999; font-size: 14px;")
        self.video_preview.setAlignment(Qt.AlignCenter)
        
        self.add_images_button = QPushButton("CHANGE THE VIDEO", self)
        self.add_images_button.setGeometry(617, 438, 250, 40)  # x, y, width, height
        self.add_images_button.setStyleSheet("""
            QPushButton {
                font-family: Muli;  
                font-size: 15px;
                font-weight: bold;
                color: white;
                background-color:  #00a181;
                padding: 10px;
            }
            QPushButton {border-radius: 4px;}
            QPushButton:hover {
                background-color: #7ed957;
                color: #004651;
            }
        """)
        self.add_images_button.clicked.connect(self.add_video)

        # Launch Button (Circular)
        self.launch_button = QPushButton(self)
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
        self.launch_button.setIconSize(self.launch_button.size() * 0.8)
        self.launch_button.clicked.connect(self.launch)

    def set_background_and_size(self, image_path):
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            QMessageBox.critical(self, "Error", f"Failed to load background image: {image_path}")
            sys.exit(1)

        self.setFixedSize(pixmap.width(), pixmap.height())
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)

    def init_empty_grid(self):
        """Khởi tạo lưới trống 2x4."""
        for row in range(2):
            for col in range(4):
                placeholder = QLabel("[+]", self)
                placeholder.setStyleSheet(
                    """background-color: #004651; border: 1px dashed #999; color: white;
                    font-size: 25px; text-align: center;border-radius: 10px""")
                placeholder.setAlignment(Qt.AlignCenter)
                self.grid_layout.addWidget(placeholder, row, col)

    def add_images(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Image Files (*.jpg *.jpeg *.png *.bmp *.gif)")
        if not filenames:
            return

        for filename in filenames:
            if len(self.image_paths) >= 8:
                QMessageBox.warning(self, "Grid Full", "The grid is full. Please remove some images to add new ones.")
                break

            self.image_paths.append(filename)  # Lưu đường dẫn ảnh
            self.update_grid()

    def update_grid(self):
        """Cập nhật lưới hiển thị ảnh."""
        # Xóa tất cả widget trong lưới
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)

        # Thêm ảnh và nút xóa vào lưới
        for idx, path in enumerate(self.image_paths):
            row, col = divmod(idx, 4)  # Tính toán vị trí hàng và cột

            # Tạo QLabel hiển thị ảnh
            image_container = QWidget(self)
            layout = QVBoxLayout(image_container)
            layout.setContentsMargins(0, 0, 0, 0)

            image_label = QLabel(image_container)
            pixmap = QPixmap(path).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image_label.setPixmap(pixmap)
            image_label.setAlignment(Qt.AlignCenter)

            # Nút xóa
            delete_button = QPushButton("X", image_container)
            delete_button.setStyleSheet(
                "background-color:#00a181 ; color: white; font-size: 12px; font-weight: bold; border-radius: 10px;"
            )
            delete_button.clicked.connect(lambda _, p=path: self.remove_image(p))

            # Thêm QLabel và nút xóa vào container
            layout.addWidget(image_label)
            layout.addWidget(delete_button, alignment=Qt.AlignCenter)

            # Thêm container vào lưới
            self.grid_layout.addWidget(image_container, row, col)

        # Điền các ô trống còn lại trong lưới
        for idx in range(len(self.image_paths), 8):
            row, col = divmod(idx, 4)
            placeholder = QLabel("[+]", self)
            placeholder.setStyleSheet(
                "background-color: #cccccc; border: 1px dashed #999; color: #666; font-size: 16px; text-align: center;"
            )
            placeholder.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(placeholder, row, col)

    def remove_image(self, path):
        """Xóa ảnh khỏi mảng và cập nhật lưới."""
        self.image_paths.remove(path)  
        self.update_grid()

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

    def launch(self):
       [imageInput,faceInInput]=inputProcess(images_path=self.image_paths)
       if(self.video_path=="" or [imageInput,faceInInput]==[0,0]) : QMessageBox.information(self, "Help", """There's no face recognise in all images.
             Make sure that images have face!!!""")
       else : 
           output_path,clipDetail,seg_obj,seg_act=execute(imageInput,self.video_path,faceInInput)
           self.win=ThirdWindow(output_path,clipDetail,seg_obj,seg_act)
           self.win.show()
           

<<<<<<< HEAD
            
       
=======
        # # Phan nay dung de test ghep code cua module trackFunction
        # imageInput = []
        # faceInInput = []
        # output_path, clipDetail, segmented_objects, segmented_actions = execute(imageInput, self.video_path, faceInInput)
        #
        # self.win=ThirdWindow(output_path,clipDetail,segmented_objects,segmented_actions)
        # self.win.show()
>>>>>>> pr/2


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FaceRecognitionUI()
    window.show()
    sys.exit(app.exec())






