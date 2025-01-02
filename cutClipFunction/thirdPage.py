from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QMessageBox, QLabel,QGridLayout
)
from PySide6.QtGui import QPixmap, QPalette, QBrush
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
import sys
import cv2



class ThirdWindow(QWidget):
    def __init__(self, video_path,clipDetail):
        """
        ThirdWindow Constructor.
        :param video_path: Đường dẫn video cần hiển thị (mặc định là None)
        """
        super().__init__()
        self.video_path = video_path
        self.data_list=clipDetail
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
        
        self.image_preview = QWidget(self)
        self.image_preview.setGeometry(0, 230, 120, 200)  # Kích thước hiển thị
        self.image_preview.setStyleSheet("background-color: #eeeeee; border: 1px solid #ccc; border-radius: 10px;")
        
        # Tạo lưới hiển thị bên trong widget con
        self.grid_layout = QGridLayout(self.image_preview)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)  # Lề xung quanh
        self.grid_layout.setSpacing(5)  # Khoảng cách giữa các ô

        # Thêm các nút vào lưới
        self.add_buttons_to_grid(self.data_list)

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
            button.clicked.connect(lambda _, idx=index: self.handle_button_click(idx, clip))
            self.grid_layout.addWidget(button, index, 0)  # Thêm nút vào lưới ở hàng `index`, cột 0


    def handle_button_click(self, index, clip):
        """
        Xử lý sự kiện khi nút được nhấn.
        Phát video từ thời điểm start_time đến end_time.
        :param index: Chỉ số của clip.
        :param clip: Thông tin chi tiết của clip (start_time, end_time, detected_objects).
        """

        start_time = clip["start_time"]
        end_time = clip["end_time"]
        self.play_video_from_time(video_path,start_time)

        # Hiển thị thông báo xác nhận

    def play_video_from_time(video_path,start_time):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Cannot open video file {video_path}")
            return

        # Lấy FPS (Frames Per Second) và tính toán frame bắt đầus
        fps = cap.get(cv2.CAP_PROP_FPS)  # Số khung hình mỗi giây
        start_frame = int(start_time * fps)

        # Đặt vị trí phát từ frame tương ứng với start_time
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        print(f"Playing video from {start_time} seconds...")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("End of video or error in reading frame.")
                break

            cv2.imshow("Video Player", frame)
            if (cv2.waitKey(int(1000 / fps)) & 0xFF == ord('q')) :
                break

        cap.release()
        cv2.destroyAllWindows()





if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Dữ liệu mẫu cho clipsDetail
    clipsDetail = [
        {'start_time': 5.0, 'end_time': 11.291666666666666, 'detected_objects': ['person']},
{'start_time': 11.291666666666666, 'end_time': 15.583333333333334, 'detected_objects': ['person']},
{'start_time': 15.583333333333334, 'end_time': 19.416666666666668, 'detected_objects': ['person']},
{'start_time': 20.625, 'end_time': 24.208333333333332, 'detected_objects': ['person']},
{'start_time': 24.208333333333332, 'end_time': 37.208333333333336, 'detected_objects': ['person']},
{'start_time': 37.5, 'end_time': 41.708333333333336, 'detected_objects': ['person', 'chair']},
{'start_time': 43.541666666666664, 'end_time': 52.583333333333336, 'detected_objects': ['person']},
{'start_time': 52.833333333333336, 'end_time': 59.666666666666664, 'detected_objects': ['person']},
{'start_time': 59.666666666666664, 'end_time': 64.75, 'detected_objects': ['person']},
{'start_time': 64.75, 'end_time': 66.08333333333333, 'detected_objects': ['person']},
{'start_time': 72.29166666666667, 'end_time': 75.33333333333333, 'detected_objects': ['person']},
{'start_time': 76.0, 'end_time': 79.08333333333333, 'detected_objects': ['person']},
{'start_time': 79.08333333333333, 'end_time': 83.0, 'detected_objects': ['person']},
{'start_time': 83.33333333333333, 'end_time': 87.04166666666667, 'detected_objects': ['person', 'chair']},
{'start_time': 87.04166666666667, 'end_time': 89.70833333333333, 'detected_objects': ['person']},
{'start_time': 89.70833333333333, 'end_time': 91.875, 'detected_objects': ['person']},
{'start_time': 98.16666666666667, 'end_time': 102.75, 'detected_objects': ['person']},
{'start_time': 110.66666666666667, 'end_time': 113.91666666666667, 'detected_objects': ['person']},
{'start_time': 114.875, 'end_time': 119.91666666666667, 'detected_objects': ['person']},
{'start_time': 119.91666666666667, 'end_time': 123.08333333333333, 'detected_objects': ['person', 'couch']},
{'start_time': 124.41666666666667, 'end_time': 127.875, 'detected_objects': ['person']},
{'start_time': 134.83333333333334, 'end_time': 140.04166666666666, 'detected_objects': ['person']},
{'start_time': 146.29166666666666, 'end_time': 152.375, 'detected_objects': ['snowboard']},
{'start_time': 172.70833333333334, 'end_time': 176.08333333333334, 'detected_objects': ['person', 'chair']},
{'start_time': 180.0, 'end_time': 186.41666666666666, 'detected_objects': ['person']},
       
    ]
    
    video_path = "exportVideo\\KhanhNgoc.mp4"  # Thay bằng đường dẫn thực tế
    window = ThirdWindow(video_path=video_path, clipDetail=clipsDetail)
    window.show()

    sys.exit(app.exec())