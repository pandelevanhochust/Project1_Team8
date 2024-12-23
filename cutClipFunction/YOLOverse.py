import cv2 as cv
import numpy as np
from moviepy import VideoFileClip, concatenate_videoclips
import face_recognition
import keyboard
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort


# Load YOLO model
model = YOLO("yolo11m.pt")
tracker = DeepSort(max_age=1)

def rotate_image(image, angle):
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv.getRotationMatrix2D(center, angle, scale=1.0)
    rotated = cv.warpAffine(image, M, (w, h))
    return rotated

def preprocess(images):   
    argImages = []
    for image in images:
        resized_image = cv.resize(image, (image.shape[1] * 2, image.shape[0] * 2))
        argImages.extend([
            resized_image,
            cv.flip(resized_image, 1),
            cv.rotate(resized_image, cv.ROTATE_90_CLOCKWISE),
            cv.rotate(resized_image, cv.ROTATE_90_COUNTERCLOCKWISE),
        ])
        argImages.extend([rotate_image(resized_image, angle) for angle in [-30, 30]])
    return argImages

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

# Load and preprocess reference images and video
imageInput = [
    "D:\\PyLesson\\Photos\\bof1.jpg",
    "D:\\PyLesson\\Photos\\bof2.jpg",
    "D:\\PyLesson\\Photos\\bof3.jpg",
    "D:\\PyLesson\\Photos\\bof4.jpg",
    "D:\\PyLesson\\Photos\\billie2.jpg",
    "D:\\PyLesson\\Photos\\billie4.jpg"
]
video_path = "D:\\PyLesson\\Ellish_BirdOfFeatther.mp4"
cap = cv.VideoCapture(video_path)


#get all the params:

argImages = preprocess([cv.imread(img) for img in imageInput])
faceInInput = [enc for img in argImages for enc in face_encodings(img, model)]

if len(faceInInput) == 0:
    print("There're no faces in the images. Please choose other images!")
    exit(0)

tolerance = 0.6
fps = int(cap.get(cv.CAP_PROP_FPS)/2)
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
#Create dict to save the detail of each clips:
clipsDetail= []



# main code :
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("The video will be exported in seconds")
        break
    
    cv.imshow("Processing Frame", frame)
    cv.waitKey(1)
    
    frame_resized = cv.resize(frame, (width, height))
    if frame_number % 2 == 0:   # reduce the frame process
        results = model.predict(source=frame_resized, conf=0.5)    #adjust the conf and size here
        
        
    face_detected = False
    detected_objects = set()
    
    for result in results:
        for box in result.boxes.data:
            print(box)
            x1, y1, x2, y2 = map(int, box[:4])  # Bounding box coordinates
            face_crop = frame[y1:y2, x1:x2]
            face_crop_encodings = face_encodings(face_crop, model)
            cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            class_id = int(box[5])
            detected_objects.add(class_id)
            
            
            if any(
                face_recognition.compare_faces(faceInInput, enc, tolerance=tolerance)
                for enc in face_crop_encodings
            ):

                face_detected = True
                latestFace = frame_number
                break

    if face_detected:
        print(f"I found her face at {frame_number / fps} seconds\n")
        if currStart is None:
            currStart = frame_number / fps
    else:
        if currStart is not None and frame_number - latestFace > limitClipLen:
            end_time = frame_number / fps + 2
            
            if currStart < last_clip_end_time:
                currStart = last_clip_end_time
                
            clipsDetail.append({
                "start_time": currStart,
                "end_time": end_time,
                "detected_objects": list(detected_objects)
            })
            
            clip = VideoFileClip(video_path).subclipped(currStart, end_time)
            clips.append(clip)
            
            cap.set(cv.CAP_PROP_POS_MSEC, currStart * 1000)
            ret, first_frame = cap.read()
            if ret:
                imageInput.append(first_frame)
                new_encodings = face_encodings(first_frame, model)
                faceInInput.extend(new_encodings)
                print(f"Added first frame of clip starting at {currStart} seconds to reference images.")
                
            last_clip_end_time = end_time    
            currStart = None
    if cv.waitKey(1) & 0xFF == ord('q'):
        print("Stop processing the video. The video will be exported in seconds")
        break

    frame_number += 1
cv.destroyAllWindows()
cap.release()


#Export video:
output_path = "D:\\PyLesson\\Videos\\YOLOKhanhNgoc.mp4"
if clips:
    for clip_info in clipsDetail:
        print(clip_info)
    final_video = concatenate_videoclips(clips)
    print(f"Exporting video to: {output_path}")
    final_video.write_videofile(output_path, codec='libx264')

else:
    print("Oops i did it again!!")


#23/12:sử dụng YOLO, fix lỗi đè clips, thêm tính năng lưu dữ liệu của clips để phục vụ các fuction tìm kiếm sau này
# dectect_object chưa hoạt động tốt , số lượng nhận diện còn hạn chế
#chưa ghép nội dung của Toàn