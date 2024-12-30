import cv2 as cv
import numpy as np
from moviepy import VideoFileClip, concatenate_videoclips
import face_recognition
#from trackFunction import get_action_descriptions,tracker,actions,classes_name
from input import *

# Load YOLO model
cap = cv.VideoCapture(video_path)




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
finetuneImages=10- len(imageInput)  #set the needed images is 10
#Create dict to save the detail of each clips:
clipsDetail= []
detections=[]



# main code :
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("The video will be exported in seconds")
        break
    
    # cv.imshow("Processing Frame", frame)
    # cv.waitKey(1)
    
    
    if frame_number % 2 == 0:   # reduce the frame process
        results = model.predict(source=frame, conf=0.5)    #adjust the conf and size here
        
        
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
            detected_objects.add(model.names[class_id])
            
            if(class_id==0.0000) and any(
                    face_recognition.compare_faces(faceInInput, enc, tolerance=tolerance)
                    for enc in face_crop_encodings):

                face_detected = True
                latestFace = frame_number
                break
            
    # decriptions=get_action_descriptions(detected_objects,actions)        
   # tracking(detections,frame)  
         

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
            if finetuneImages:
                cap.set(cv.CAP_PROP_POS_MSEC, currStart * 1000)
                ret, first_frame = cap.read()
                if ret:
                    finetuneImages-=1
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






output_path = "D:\\PyLesson\\Videos\\YOLOKhanhNgoc.mp4"
if clips:
    for clip_info in clipsDetail:
        print(clip_info)
    final_video = concatenate_videoclips(clips)
    print(f"Exporting video to: {output_path}")
    final_video.write_videofile(output_path, codec='libx264')

else:
    print("Oops i did it again!!")


