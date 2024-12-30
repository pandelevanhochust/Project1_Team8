import cv2 as cv
import numpy as np
from moviepy import VideoFileClip, concatenate_videoclips
import face_recognition
from ultralytics import YOLO
#from trackFunction import get_action_descriptions,tracker,actions,classes_name
from PySide6.QtCore import Qt,QRect, QTimer
from executePage import SecondWindow 
model = YOLO("yolo11m.pt")
# Load YOLO model
def face_encodings(image, model):
    results = model.predict(source=image, conf=0.5)
    encodings = []
    for result in results:
        for box in result.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box)  # Bounding box coordinates
            face_crop = image[y1:y2, x1:x2]
            face_crop_rgb = cv.cvtColor(face_crop, cv.COLOR_BGR2RGB)
            if face_crop_rgb.shape[0] >= 10 and face_crop_rgb.shape[1] >= 10:
                face_enc = face_recognition.face_encodings(face_crop_rgb)
                if face_enc:
                    encodings.append(face_enc[0])
    return encodings



def execute(imageInput, video_path, faceInInput):
    window = SecondWindow()
    cap = cv.VideoCapture(video_path)

    tolerance = 0.6
    fps = int(cap.get(cv.CAP_PROP_FPS) / 2)
    frame_number = 0
    limitClipLen = int(2 * fps)
    latestFace = -1
    detected_objects = set()
    currStart = None
    clipsDetail = []
    clips = []
    finetuneImages = 10 - len(imageInput)  # Số lượng ảnh cần lấy thêm

    def process_frame():
        nonlocal cap, frame_number, currStart, latestFace, detected_objects

        ret, frame = cap.read()
        if not ret:
            print("The video will be exported in seconds")
            timer.stop()
            cap.release()
            return

        # Hiển thị frame trên giao diện
        window.add_video(frame)

        # Xử lý YOLO và nhận diện khuôn mặt
        if frame_number % 2 == 0:  # Giảm tần suất xử lý
            results = model.predict(source=frame, conf=0.5)  # Điều chỉnh conf nếu cần
            detected_objects.clear()

            for result in results:
                for box in result.boxes.data:
                    x1, y1, x2, y2 = map(int, box[:4])
                    face_crop = frame[y1:y2, x1:x2]
                    face_crop_encodings = face_encodings(face_crop, model)

                    # Vẽ bounding box
                    cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    class_id = int(box[5])
                    detected_objects.add(model.names[class_id])

                    # Kiểm tra khuôn mặt
                    if class_id == 0 and any(
                        face_recognition.compare_faces(faceInInput, enc, tolerance=tolerance)
                        for enc in face_crop_encodings
                    ):
                        latestFace = frame_number

        # Kiểm tra phát hiện khuôn mặt
        if latestFace != -1 and frame_number - latestFace > limitClipLen:
            end_time = frame_number / fps + 2
            clipsDetail.append({
                "start_time": currStart,
                "end_time": end_time,
                "detected_objects": list(detected_objects),
            })
            clip = VideoFileClip(video_path).subclipped(currStart, end_time)
            clips.append(clip)
            currStart = None

        frame_number += 1

        # Kiểm tra nếu cửa sổ đóng
        if window.isClose:
            print("Stop processing the video.")
            timer.stop()
            cap.release()

    # Sử dụng QTimer để cập nhật frame
    timer = QTimer()
    timer.timeout.connect(process_frame)
    timer.start(1000 // 30)  # 30 FPS hoặc thay đổi theo nhu cầu

    # Hiển thị giao diện
    window.show()



    output_path = "D:\\PyLesson\\Videos\\YOLOKhanhNgoc.mp4"
    if clips:
        for clip_info in clipsDetail:
            print(clip_info)
        final_video = concatenate_videoclips(clips)
        print(f"Exporting video to: {output_path}")
        final_video.write_videofile(output_path, codec='libx264')

    else:
        print("Oops i did it again!!")


