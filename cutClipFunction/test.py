import cv2 as cv
import numpy as np
from moviepy import VideoFileClip, concatenate_videoclips
import face_recognition
from trackFunction import (
    are_close1, are_close2, action_description,
    object_segmentation, action_segmentation,
    tracker, actions, classes_name
)
from input import *
# Load YOLO model


def tracking(detections, frame):
    colors = np.random.randint(0, 255, size=(len(classes_name), 3))
    tracks = tracker.update_tracks(detections, frame=frame)
    for track in tracks:
        if not track.is_confirmed():
            continue
        track_id = track.track_id  # ID theo dõi
        ltrb = track.to_ltrb()  # Toạ độ bounding box (left, top, right, bottom)
        cv.rectangle(frame, (int(ltrb[0]), int(ltrb[1])), (int(ltrb[2]), int(ltrb[3])), colors, 2)
        cv.putText(frame, f"ID: {track_id}", (int(ltrb[0]), int(ltrb[1] - 10)),
                   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Hiển thị frame
    cv.imshow("DeepSort Tracking", frame)


tolerance = 0.6
fps = int(cap.get(cv.CAP_PROP_FPS) / 2)
width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
frame_count = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps

face_timestamps = []
frame_number = 0
clips = []
currStart = None
latestFace = -1
limitClipLen = int(2 * fps)
last_clip_end_time = 0
finetuneImages = 10 - len(imageInput)  # set the needed images is 10
# Create dict to save the detail of each clips:
clipsDetail = []
detections = []

# Initialize variables
track_objects = {}
close_objects = {}

# main code :
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("The video will be exported in seconds")
        break

    if frame_number % 2 == 0:  # Reduce the frame process
        results = model.predict(source=frame, conf=0.5)  # Adjust the conf and size here

    face_detected = False
    detected_objects = []

    for result in results:
        for box in result.boxes.data:
            x1, y1, x2, y2 = map(int, box[:4])  # Bounding box coordinates
            class_id = int(box[5])
            confidence = float(box[4])
            detected_objects.append({
                "bbox": [x1, y1, x2, y2],
                "track_id": None,  # Sử dụng track ID từ tracker sau
                "name": model.names[class_id]
            })

    # Gọi tracker
    tracks = tracker.update_tracks(detected_objects, frame=frame)
    current_objects = [
        {
            "bbox": track.to_ltrb(),
            "track_id": track.track_id,
            "name": model.names[track.get_det_class()]
        }
        for track in tracks if track.is_confirmed()
    ]

    # Gọi hàm mô tả hành động
    action_description(current_objects, actions, frame_number)

    # Hiển thị frame
    cv.imshow("Processed Frame", frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break

    frame_number += 1

# Gọi phân đoạn cuối cùng sau khi xử lý xong:
object_segmentation(track_objects)
action_segmentation(close_objects)

# Export video:
output_path = "D:\\PyLesson\\Videos\\YOLOKhanhNgoc.mp4"
if clips:
    for clip_info in clipsDetail:
        print(clip_info)
    final_video = concatenate_videoclips(clips)
    print(f"Exporting video to: {output_path}")
    final_video.write_videofile(output_path, codec='libx264')
else:
    print("Oops i did it again!!")

cv.destroyAllWindows()
cap.release()
