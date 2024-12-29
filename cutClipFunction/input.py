from PIL import Image
import cv2 as cv
import os
import face_recognition
from ultralytics import YOLO

model = YOLO("yolo11m.pt")

def convert_to_jpg(input_path, output_path=None):
    try:
   
        img = Image.open(input_path)
        
        
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        
        if output_path is None:
            base_name = os.path.splitext(input_path)[0]
            output_path = f"{base_name}.jpg"
        
      
        img.save(output_path, format='JPEG', quality=95)
        print(f"Đã lưu tệp JPG: {output_path}")
        return output_path

    except Exception as e:
        print(f"Lỗi khi chuyển đổi tệp: {e}")
        return None

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
imageInput1 = [
    "D:\PyLesson\Photos\hanni1.png",
    "D:\PyLesson\Photos\hanni2.png",
    "D:\PyLesson\Photos\hanni3.png",
    "D:\PyLesson\Photos\hanni4.png",
    "D:\PyLesson\Photos\hanni5.png",
    
]

imageInput=[convert_to_jpg(img) for img in imageInput1]

video_path = "D:\\PyLesson\\Photos\\eta.mp4"
cap = cv.VideoCapture(video_path)


#get all the params:

argImages = preprocess([cv.imread(img) for img in imageInput])
faceInInput = [enc for img in argImages for enc in face_encodings(img, model)]

if len(faceInInput) == 0:
    print("There're no faces in the images. Please choose other images!")
    exit(0)