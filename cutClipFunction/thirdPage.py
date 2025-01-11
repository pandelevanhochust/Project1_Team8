from PySide6.QtWidgets import ( 
    QApplication, QWidget, QPushButton, QMessageBox, QLabel, QGridLayout
)
from PySide6.QtGui import QPixmap, QPalette, QBrush
from PySide6.QtCore import QTimer, QUrl,Qt
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
import sys
from functools import partial


class ThirdWindow(QWidget):
    def __init__(self, video_path, clipDetail,segmented_objects,segmented_actions):
        """
        ThirdWindow Constructor.
        :param video_path: Đường dẫn video cần hiển thị (mặc định là None)
        """
        super().__init__()
        self.video_path = video_path
        self.data_list = clipDetail
        self.segmented_objects = segmented_objects
        self.segmented_actions = segmented_actions
        self.initUI()

    def initUI(self):
        # Cài đặt hình nền
        background_image_path = 'thirdPage.png'

        pixmap = QPixmap(background_image_path)
        if pixmap.isNull():
            QMessageBox.critical(self, "Error", f"Failed to load background image: {background_image_path}")
            sys.exit(1)

        self.setFixedSize(pixmap.width(), pixmap.height())
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)

        self.setWindowTitle("Third Window")

        # Khu vực xem video
        self.video_widget = QVideoWidget(self)
        self.video_widget.setGeometry(310, 45, 721, 405)  # x, y, width, height
        self.video_widget.setStyleSheet("background-color: #000; border: 1px solid #999;")


        #Image showcase
        self.image_overlay = QLabel(self)
        # self.image_overlay.setGeometry(310, 45, 405, 405)
        self.image_overlay.setStyleSheet("background-color: transparent;")
        self.image_overlay.setAlignment(Qt.AlignCenter)
        self.image_overlay.hide()  # Initially hidden

        # Nút HOME
        self.finishButton = QPushButton("RETURN HOME", self)
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

        # Image selection
        self.image_preview = QLabel(self)  # Change from QWidget to QLabel
        self.image_preview.setGeometry(0, 230, 200, 200)  # Size and position
        self.image_preview.setStyleSheet("background-color: #eeeeee; border: 1px solid #ccc; border-radius: 10px;")
        self.image_preview.setAlignment(Qt.AlignCenter)

        # Tạo lưới hiển thị bên trong widget con
        self.grid_layout = QGridLayout(self.image_preview)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)  # Lề xung quanh
        self.grid_layout.setSpacing(5)  # Khoảng cách giữa các ô

        # Thêm các nút vào lưới
        # self.add_buttons_to_grid(self.data_list)
        self.add_buttons_to_grid(data_list=self.data_list)

        # Khởi tạo MediaPlayer
        self.media_player = QMediaPlayer(self)
        self.media_player.setVideoOutput(self.video_widget)

        # Nếu có đường dẫn video, hiển thị ngay
        if self.video_path:
            self.play_video(self.video_path)

    def confirm(self):
        self.close()

    def play_video(self, video_path):
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        self.media_player.play()
        self.video_widget.show()

    def set_video_path(self, video_path):
        self.video_path = video_path
        self.play_video(video_path)
        
    def add_buttons_to_grid(self, data_list):
        for index, clip in enumerate(data_list):
            clip["detected_objects"]=clip["detected_objects"][1:]
            if(len(clip["detected_objects"])==0 ) : continue
            
            detected_objects = ", ".join(clip["detected_objects"]) 
            button_text = f"{detected_objects}"
            
            # Tạo nút
            button = QPushButton(button_text, self)
            button.setStyleSheet("""
            QPushButton {
                font-family: Muli;  
                font-size: 16px;
                font-weight: bold;
                color: white;
                background-color:  #00a181;
                padding: 10px;
            }
            QPushButton {border-radius: 10px;}
            QPushButton:hover {
                background-color: #7ed957;
                color: #004651;
            }
        """)
            
            # Kết nối nút với sự kiện bấm
            button.clicked.connect(partial(self.handle_button_click, index))
            self.grid_layout.addWidget(button, index, 0)  # Thêm nút vào lưới ở hàng index, cột 0


    def handle_button_click(self, index):
        start_time = self.data_list[index]["start_time"]
        end_time = self.data_list[index]["end_time"]

        if self.media_player.source().toString() != QUrl.fromLocalFile(self.video_path).toString():
            self.media_player.setSource(QUrl.fromLocalFile(self.video_path))
        
        # Đặt video bắt đầu tại start_time
        self.media_player.setPosition(int(start_time) * 1000)
        self.media_player.play()

        # Sử dụng QTimer để dừng video
        duration = (int(end_time) - int(start_time)) * 1000
        QTimer.singleShot(duration, self.media_player.pause)

        # Theo dõi thời điểm hiện tại và dừng khi đạt end_time
        def stop_at_end_time(position):
            if position >= int(end_time) * 1000:  # end_time cũng chuyển sang milliseconds
                self.media_player.pause()
                self.media_player.positionChanged.disconnect(stop_at_end_time)

        try:
            self.media_player.positionChanged.disconnect()
        except TypeError:
            pass
        self.media_player.positionChanged.connect(stop_at_end_time)

        # Hiển thị thông báo xác nhận





if __name__ == "__main__":
    app = QApplication(sys.argv)

    # # Dữ liệu mẫu cho clipsDetail
    # clipsDetail = [
    #     {
    #         "start_time": "00:00:05",
    #         "end_time": "00:00:15",
    #         "detected_objects": ["Car", "Tree", "Dog"]
    #     },
    #     {
    #         "start_time": "00:01:00",
    #         "end_time": "00:01:30",
    #         "detected_objects": ["Person", "Bicycle"]
    #     },
    #     {
    #         "start_time": "00:02:00",
    #         "end_time": "00:02:30",
    #         "detected_objects": ["Cat", "Bus"]
    #     },
    # ]

    # segmented_objects = {
    #     "Car": [
    #         {"track_id": 1, "image_path": "D:\\CODIng\\CV\\YOLO Image Detection\\segmented objects\\billie on the chair\\person\\person-1_from_4_to_94.jpg","appear_frame": 20, "disappear_frame": 30},
    #         {"track_id": 2, "image_path": "car2.jpg", "appear_frame": 20, "disappear_frame": 30}
    #     ],
    #     "Person": [
    #         {"track_id": 3, "image_path": "D:\CODIng\CV\Project1_Team8\BillieEilish2.jpg", "appear_frame": 5, "disappear_frame": 15}
    #     ]
    # }

    # # Example segmented_actions
    # segmented_actions = {
    #     "Person holding a cup": [
    #         {
    #             "object1": "Person",
    #             "object2": "Cup",
    #             "appear_time": 4,  
    #             "disappear_time": 64,  
    #             "video_path": "D:\\CODIng\\CV\\YOLO Image Detection\\segmented clips\\billie on the chair\\person and chair-('1', '3')_from_4_to_64.mp4",
    #             "description": "A person holding a cup"
    #         }
    #     ],
    #     "Car interacting with Person": [
    #         {
    #             "object1": "Car",
    #             "object2": "Person",
    #             "appear_time": 10,
    #             "disappear_time": 50,
    #             "video_path": "D:\\CODIng\\CV\\YOLO Image Detection\\billie on the couch.mp4",
    #             "description": "A car interacting with a person"
    #         }
    #     ]
    # }

    video_path = "exportVideo\\KhanhNgoc.mp4" # Thay bằng đường dẫn thực tế
    window = ThirdWindow()
    window.show()

    sys.exit(app.exec())