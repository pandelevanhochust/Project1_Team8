from PIL import Image
import cv2 as cv
import os
import face_recognition
from ultralytics import YOLO
from module.YOLOverse import face_encodings

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

imageInput=[]
video_path=""
faceInInput=[]

def inputProcess(images_path):
# Load and preprocess reference images and video
    imageInput=[convert_to_jpg(img) for img in images_path]
    argImages = preprocess([cv.imread(img) for img in imageInput])
    faceInInput = [enc for img in argImages for enc in face_encodings(img, model)]
    images_path=images_path

    if len(faceInInput) == 0:
       return [0,0]
    else: return [imageInput,faceInInput]