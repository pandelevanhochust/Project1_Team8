from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QMessageBox, QLabel,QGridLayout
)
from PySide6.QtGui import QPixmap, QPalette, QBrush
from PySide6.QtCore import Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
import sys


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
            self.grid_layout.addWidget(button, index, 0)  # Thêm nút vào lưới ở hàng index, cột 0


    def handle_button_click(self, index, clip):
        """
        Xử lý sự kiện khi nút được nhấn.
        Phát video từ thời điểm start_time đến end_time.
        :param index: Chỉ số của clip.
        :param clip: Thông tin chi tiết của clip (start_time, end_time, detected_objects).
        """
        start_time = clip["start_time"]
        end_time = clip["end_time"]
        self.media_player.setSource(QUrl.fromLocalFile(video_path))
        self.media_player.setVideoOutput(self.video_widget)
        # Đặt video bắt đầu tại start_time
        self.media_player.setPosition(int(start_time) *1000)  
        self.media_player.play()

        # Theo dõi thời điểm hiện tại và dừng khi đạt end_time
        def stop_at_end_time(position):
            if position >= int(end_time) * 1000:  # end_time cũng chuyển sang milliseconds
                self.media_player.pause()
                

        # Kết nối tín hiệu positionChanged để kiểm tra thời gian
        self.media_player.positionChanged.connect(stop_at_end_time)

        # Hiển thị thông báo xác nhận



if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Dữ liệu mẫu cho clipsDetail
    clipsDetail = [
       
    ]
    
    video_path = "exportVideo\\KhanhNgoc.mp4"  # Thay bằng đường dẫn thực tế
    window = ThirdWindow(video_path=video_path, clipDetail=clipsDetail)
    window.show()

    sys.exit(app.exec())