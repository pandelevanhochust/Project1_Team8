import cv2 as cv
import numpy as np
from mtcnn import MTCNN
import face_recognition
from moviepy import VideoFileClip, concatenate_videoclips


mtcnn = MTCNN(device='cpu')

def preprocess(images):   
    argImages = []
    for image in images:
        resized_image = cv.resize(image, (image.shape[1]*2, image.shape[0]*2))
        argImages.extend([
            resized_image,  
            cv.flip(resized_image, 1),
            cv.rotate(resized_image, cv.ROTATE_90_CLOCKWISE),
            cv.rotate(resized_image, cv.ROTATE_90_COUNTERCLOCKWISE),
        ])
    return argImages

def face_encodings(image, model):
    faces = model.detect_faces(image)
    encodings = []
    for face in faces:
        x1, y1, width, height = face['box']
        x2, y2 = x1 + width, y1 + height
        face_crop = image[y1:y2, x1:x2]
        face_crop_rgb = cv.cvtColor(face_crop, cv.COLOR_BGR2RGB)
        if face_crop_rgb.shape[0] >= 10 and face_crop_rgb.shape[1] >= 10:     #adjust the num to choose the size of recog face
            face_enc = face_recognition.face_encodings(face_crop_rgb)
            if face_enc:
                encodings.append(face_enc[0])
    return encodings

# Load and preprocess reference images
#add constraints that user must upload jusst .jpg file
imageInput = ["D:\\PyLesson\\Photos\\bof1.jpg",
                    "D:\\PyLesson\\Photos\\bof2.jpg",
                    "D:\\PyLesson\\Photos\\bof3.jpg",
                    "D:\\PyLesson\\Photos\\bof4.jpg",
                    "D:\\PyLesson\\Photos\\billie2.jpg",
                    "D:\\PyLesson\\Photos\\billie4.jpg"] #the input that should be upload by user
argImages = preprocess(
    [cv.imread(img) for img in imageInput]
)
faceInInput = [
    enc for img in argImages for enc in face_encodings(img, mtcnn)
]
if len(faceInInput) == 0 :
    print("There're no face in image , please choose other images!!! ")
    exit(0)

tolerance = 0.6
video_path = "D:\\PyLesson\\Ellish_BirdOfFeatther.mp4"
cap = cv.VideoCapture(video_path)

fps = int(cap.get(cv.CAP_PROP_FPS))
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

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    cv.imshow("Processing Frame", frame)
    cv.waitKey(1)
    faces = mtcnn.detect_faces(frame)
    face_detected = False
    
    for face in faces:
        x1, y1, width, height = face['box']
        x2, y2 = x1 + width, y1 + height
        face_crop = frame[y1:y2, x1:x2]
        face_crop_encodings = face_encodings(face_crop, mtcnn)

        if any(
            face_recognition.compare_faces(faceInInput, enc, tolerance=tolerance)
            for enc in face_crop_encodings
        ):
            
            face_detected = True
            latestFace=frame_number
            break

    if face_detected:
        print(f"I found her face at {frame_number/fps} \n")
        if currStart is None:
            currStart = frame_number / fps
    else:
        if currStart is not None and frame_number - latestFace > limitClipLen:
            end_time = frame_number / fps + 2
            clip = VideoFileClip(video_path).subclipped(currStart, end_time)
            clips.append(clip)
            currStart = None
#in here create an arg to record the latest face momment, decreasing by frame,
# if>0 update new momment and add into latest clip, else make new clip

    frame_number += 1
cv.destroyAllWindows()

cap.release()
output_path = "D:\\PyLesson\\Videos\\KhanhNgoc.mp4"
if clips:
    final_video = concatenate_videoclips(clips)
    print(f"Xuất video tới: {output_path}")
    final_video.write_videofile(output_path, codec='libx264')
else:
    print("Oops !I did it again,my bad")

#18/12 vấn đề : đang bị trùng lặp quá nhiều frame, cần 1 giải pháp là nếu đã nhận diện được rồi thì ghi thời điểm bắt đầu vào ,
# ghi thời điểm kết thúc từ thời điểm bắt đầu đầu tiên và cộng dồn lại
#với nguồn vào input cần có nhiều góc độ mặt khác nhau   -->solve



#19/12 sau khi  thay đổi : thời gian render giảm đáng kể từ 35p->20p
#nguyên nhân : do để nhầm vị trí của destroyallwindow-> cửa sổ quan sát bị tắt liên tục -> tăng số tiến trình IO

# input nhập vào chỉ chạy được khi ở dạng jpg
#20/12 : thêm vào các breakPoint để chương trình kiểm tra từng công đoạn