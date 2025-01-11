import cv2 as cv
import numpy as np
from moviepy import VideoFileClip, concatenate_videoclips
import face_recognition
from ultralytics import YOLO

# from cutClipFunction.MTCNNVerse import output_path
from executePage import SecondWindow
from trackFunction import trackerFunc, object_segmentation, action_segmentation

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
            face_crop_rgb = face_crop_rgb.astype('uint8')
            if face_crop_rgb.shape[0] >= 10 and face_crop_rgb.shape[1] >= 10:
                face_enc = face_recognition.face_encodings(face_crop_rgb)
                if face_enc:
                    encodings.append(face_enc[0])
    return encodings


def execute(imageInput, video_path, faceInInput):
    window = SecondWindow()
    window.start_video(video_path)
    cap = cv.VideoCapture(video_path)
    window.show()

    tolerance = 0.6
    fps = int(cap.get(cv.CAP_PROP_FPS))  # chỉnh fps còn 1 nửa gây ra lỗi
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps

    frame_number = 0
    clips = []
    currStart = None
    latestFace = -1
    limitClipLen = fps
    last_clip_end_time = 0
    finetuneImages = 10 - len(imageInput)  # set the needed images is 10
    # Create dict to save the detail of each clips:
    clipsDetail = []

    # main code :
    while cap.isOpened():
        # bắt đầu thêm các tính năng từ đây
        ret, frame = cap.read()
        if not ret:
            print("The video will be exported in seconds")
            break

        framed = cv.resize(frame, (int(frame.shape[1] * 0.75), int(frame.shape[0] * 0.75)))
        # cv.imshow("processing frame",framed)
        cv.waitKey(1)

        # da bo conf = 0.5 o doan  nay va dua xuong phia duoi
        if frame_number % 4 == 0:  # reduce the frame process
            results = model.predict(source=frame)  # adjust the conf and size here

        trackerFunc(results, video_path, frame,frame_number)

        face_detected = False
        detected_objects = []

        for result in results:
            for box in result.boxes.data:
                # confidence
                confidence = float(box[4])
                class_id = int(box[5])
                if confidence < 0.5:
                    continue

                x1, y1, x2, y2 = map(int, box[:4])  # Bounding box coordinates
                face_crop = frame[y1:y2, x1:x2]
                face_crop_encodings = face_encodings(face_crop, model)
                cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                detected_objects.append([[x1, y1, x2 - x1, y2 - y1], confidence, class_id])

                if (class_id == 0.0000) and any(
                        face_recognition.compare_faces(faceInInput, enc, tolerance=tolerance)
                        for enc in face_crop_encodings):
                    face_detected = True
                    latestFace = frame_number
                    break


        if face_detected:
            print(f"I found her face at {frame_number / fps} seconds\n")
            if currStart is None:
                currStart = frame_number / fps
        else:
            if currStart is not None and frame_number - latestFace > limitClipLen:
                end_time = (frame_number / fps + 2) if (frame_number / fps + 2) < duration else duration

                if currStart < last_clip_end_time:
                    currStart = last_clip_end_time

                clipsDetail.append({
                    "start_time": currStart,
                    "end_time": end_time,
                    "detected_objects": list(detected_objects)
                })

                clip = VideoFileClip(video_path).subclipped(currStart, end_time)
                clips.append(clip)
                if finetuneImages:
                    cap.set(cv.CAP_PROP_POS_MSEC, currStart * 1000)
                    ret, first_frame = cap.read()
                    if ret:
                        finetuneImages -= 1
                        imageInput.append(first_frame)
                        new_encodings = face_encodings(first_frame, model)
                        faceInInput.extend(new_encodings)
                        print(f"Added first frame of clip starting at {currStart} seconds to reference images.")

                last_clip_end_time = end_time
                currStart = None

        if window.isClose == True:
            print("Stop processing the video. The video will be exported in seconds")
            break
        frame_number += 1
    cap.release()
    cv.destroyAllWindows()

    # Segmenting after tracking
    segmented_objects = object_segmentation(video_path)
    segmented_actions = action_segmentation(video_path)

    output_path = "D:\CODIng\CV\YOLO Image Detection\dung.mp4"

    # if segmented_objects or segmented_actions:
    #     return output_path,clipsDetail,segmented_objects, segmented_actions

    if clips:
        for clip_info in clipsDetail:
            print(clip_info)
        final_video = concatenate_videoclips(clips)
        print(f"Exporting video to: {output_path}")
        final_video.write_videofile(output_path, codec='libx264')
        final_video.close()  # đoạn này chưa chắc đã giải phóng tài nguyên nên cần thực hiện giải phóng trước
        print("Export complete")
        return output_path, clipsDetail, segmented_objects, segmented_actions

    else:
        print("Oops! I did it again!! I couldn't get any clip which having her face")

# file gốc YOLO nằm ở đây