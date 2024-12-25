from ultralytics import YOLO
import cv2
import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort
from PIL import Image
import os
import math
from moviepy.video.io.VideoFileClip import VideoFileClip

# Initialize YOLO model
model = YOLO('yolo11l.pt')  # Replace with your pretrained YOLO model path

#create directory for segmented objects
output_image = "segmented objects"
os.makedirs(output_image,exist_ok=True)

output_video = "segmented clips"
os.makedirs(output_video, exist_ok=True)

# Initialize DeepSort tracker
tracker = DeepSort(max_age=0)

# Load COCO class names
with open("data_ext/classes.names") as f:
    classes_name = f.read().strip().split("\n")
#exceptional_classes
exceptional_classes = [56,57]

# Define actions
actions = {
    "person": {
        "ball": "playing with a ball",
        "laptop": "using a laptop",
        "bicycle": "riding a bicycle",
        "cell phone": "is holding a cellphone",
        "cup": "is holding a cup",
        "chair": "is sitting on a chair",
        "couch": "is sitting on a couch",
        "car" : "riding a car",
        "horse": "riding a horse",
        "person" : "with another person"
    }
}

# Assign unique colors for tracks
colors = np.random.randint(0,255, size=(len(classes_name),3 ))

#check whether two objects are close
def are_close1(obj1, obj2, iou_threshold=0.1):
    # Extract bounding box coordinates
    x1, y1, x2, y2 = obj1["bbox"]
    x1_, y1_, x2_, y2_ = obj2["bbox"]
    # Calculate the intersection
    xi1 = max(x1, x1_)
    yi1 = max(y1, y1_)
    xi2 = min(x2, x2_)
    yi2 = min(y2, y2_)
    intersection_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    # Calculate the union
    bbox1_area = (x2 - x1) * (y2 - y1)
    bbox2_area = (x2_ - x1_) * (y2_ - y1_)
    union_area = bbox1_area + bbox2_area - intersection_area
    # Handle division by zero
    if union_area == 0:
        return False
    # Calculate IoU and check if it meets the threshold
    iou = intersection_area / union_area
    return iou >= iou_threshold

def are_close2(obj1, obj2, distance_threshold=10):
    x1, y1, x2, y2 = obj1["bbox"]
    x1_, y1_, x2_, y2_ = obj2["bbox"]
    center1 = ((x1 + x2) / 2, (y1 + y2) / 2)
    center2 = ((x1_ + x2_) / 2, (y1_ + y2_) / 2)
    distance = math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)
    return distance <= distance_threshold

def object_segmentation(track_id,class_id,ltrb,frame_number):
    x1, y1, x2, y2 = map(int, ltrb)
    if track_id not in track_objects:
        track_objects[track_id] = {
            "name": model.names[class_id],
            "bbox": ltrb,
            "appear": frame_number,
            "disappear": None
        }

    pil_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    segmented_object = pil_image.crop((x1, y1, x2, y2))

    parent_dir = os.path.join(output_image, video_name)
    os.makedirs(parent_dir, exist_ok=True)

    class_dir = os.path.join(parent_dir, classes_name[class_id])
    os.makedirs(class_dir, exist_ok=True)

    output_path = os.path.join( class_dir, f"{classes_name[class_id]}-{track_id}_from_{track_objects[track_id]['appear']}_to_{track_objects[track_id]['disappear']}.jpg"
    )
    # Create a subdirectory for the object class
    class_dir = os.path.join(parent_dir, classes_name[class_id])
    os.makedirs(class_dir, exist_ok=True)

    segmented_object.save(output_path)

    track_objects[track_id]["disappear"] = frame_number

#Function to track actions
def action_tracker(det,obj,frame_number):
    objects_pair = (det["track_id"], obj["track_id"])
    if objects_pair not in close_objects:
        close_objects[objects_pair] = {
            "object1": det["name"],
            "object2": obj["name"],
            "appear": frame_number,
            "disappear": frame_number,
        }
    else:
        close_objects[objects_pair]["disappear"] = frame_number

# Function to generate action descriptions and create actions
def action_description(detections, actions,frame_number):
    descriptions = set()
    for det in detections:
        if det["name"] == 'person':
            for obj in detections:
                if det["track_id"] != obj["track_id"] and (are_close1(det, obj) or are_close2(det,obj)):
                    action = actions.get('person', {}).get(obj["name"], None)
                    action_tracker(det, obj,frame_number)
                    if action:
                        descriptions.add(f"A person {det['track_id']} is {action} {obj['track_id']}")
    des = list(descriptions)
    for i, desc in enumerate(des):
        cv2.putText(frame, desc, (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        print(desc)

def action_segmentation (close_objects):
    for pair,obj in close_objects.items():
        obj1 = obj['object1']
        obj2 = obj['object2']
        appear = obj['appear']
        disappear = obj['disappear']
        appear_time = appear / 2 / fps
        disappear_time = disappear / 2 / fps

        parent_dir = os.path.join(output_video, video_name)
        os.makedirs(parent_dir, exist_ok=True)

        output_filename = os.path.join(parent_dir,f"{obj1} and {obj2}-{pair}_from_{appear}_to_{disappear}.mp4")

        #extract clip
        subclip = clip.subclipped(appear_time, disappear_time)
        subclip.write_videofile(output_filename,codec="libx264")
        print (f"Clip {obj1} and {obj2}-{pair}_from_{appear}_to_{disappear} saved")

# Initialize video capture
input = "billie on the couch.mp4"
cap = cv2.VideoCapture(input)
clip = VideoFileClip(input)
video_name = os.path.splitext(os.path.basename(input))[0]

# Initialize variables
tracks = []
track_objects = {}
close_objects = {}

# Get video properties
fps = int(cap.get(cv2.CAP_PROP_FPS)/2)
frame_number =0
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#main code
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # skipping odd frames for performance optimization
    if frame_number % 2 != 0:
        frame_number += 1
        continue

    frame_resized = cv2.resize(frame, (width, height))

    #Running YOLO
    results = model(frame_resized)
    detected_objects = []

    #Parse detections
    for box in results[0].boxes:
        bbox = box.xyxy.tolist()[0]
        x1, y1, x2, y2 = map(int, bbox)
        class_id = int(box.cls)
        confidence = float(box.conf)
        if len(bbox) == 4 and (confidence > 0.5 or (confidence <= 0.5 and class_id in exceptional_classes)):
            detected_objects.append([[x1, y1, x2 - x1, y2 - y1], confidence, class_id])

    # Debugging: Print detected_objects
    print("Detected objects passed to tracker:")
    for obj in detected_objects:
        print(classes_name[obj[2]],obj)

    # Update tracker with detected objects
    tracks = tracker.update_tracks(detected_objects,frame=frame_resized)

    # Generate action descriptions
    current_objects = []
    for track in tracks:
        track_id = track.track_id
        if track.is_confirmed():
            ltrb = track.to_ltrb()
            class_id = track.get_det_class()
            x1, y1, x2, y2 = map(int, ltrb)

            if track_id not in track_objects:
                object_segmentation(track_id,class_id,ltrb,frame_number)

            current_objects.append({
                "name": model.names[class_id],
                "bbox": ltrb,
                "track_id": track_id
            })

            label = f"{classes_name[class_id]} {track_id}"

            color = colors[class_id]
            B, G, R = map(int,color)

            # Annotate frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
            cv2.putText(frame, label, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Generate descriptions for actions
        action_description(current_objects, actions,frame_number)

    # Show the frame
    cv2.imshow('YOLO Object Detection', frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_number += 1

# Print all detected objects
print("All objects detected:")
for track_id,obj in track_objects.items():
    print(f"Object {obj['name']}-{track_id} appears from frame {obj['appear']} to {obj['disappear']}")

print("Close_objects:")
for pair,obj in close_objects.items():
    print(f"Objects {obj['object1']} {pair[0]} and {obj['object2']} {pair[1]} "
          f"from frame {obj['appear']} to frame {obj['disappear']}.")

action_segmentation(close_objects)

# Release resources
cap.release()
cv2.destroyAllWindows()

#22/12: xác định được các vật thể có trong video, cho vào mảng các đồ vật xuất hiện.
# Chưa thêm mảng events các cảnh có vật thể và export ra

#24/12: đã lưu toàn bộ vật thể được track và khoảng thời gian xuất hiện, cũng như segment vật thể ra ảnh

#25/12: đã track được hai vật thể tương tác với nhau
#25/12: đã tối giản mọi thú về functions
#25/12: extract duoc video ra cho tung action




