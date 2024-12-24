from ultralytics import YOLO
import cv2
import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort
from PIL import Image
import os
import random

# Initialize YOLO model
model = YOLO('yolo11m.pt')  # Replace with your pretrained YOLO model path

#create directory for segmented objects
output = "segmented objects"
os.makedirs(output,exist_ok=True)

# Initialize DeepSort tracker
tracker = DeepSort(max_age=2)

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
        "horse": "riding a horse"
    }
}

# Assign unique colors for tracks
colors = np.random.randint(0,255, size=(len(classes_name),3 ))

#check whether two objects are close
def are_close(obj1, obj2, iou_threshold=0.3):
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

# Function to generate action descriptions
def get_action_descriptions(detections, actions):
    descriptions = set()
    for det in detections:
        if det["name"] == 'person':
            for obj in detections:
                if obj["name"] != 'person' and are_close(det, obj):
                    action = actions.get('person', {}).get(obj["name"], None)
                    if action:
                        descriptions.add(f"A person is {action}")
    return list(descriptions)

# def extract_objects(track_id,class_id,frame):

# Initialize video capture
cap = cv2.VideoCapture('billie on the couch.mp4')  # Replace with your input video path

# Initialize variables
tracks = []
track_objects = {}

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
    tracks = tracker.update_tracks(
        detected_objects,
        frame=frame_resized
    )

    # Generate action descriptions
    current_objects = []
    for track in tracks:
        track_id = track.track_id
        if track.is_confirmed():
            ltrb = track.to_ltrb()
            class_id = track.get_det_class()
            x1, y1, x2, y2 = map(int, ltrb)

            if track_id not in track_objects:
                track_objects[track_id] = {
                    "name":  model.names[class_id],
                    "bbox": ltrb,
                    "appear": frame_number,
                    "disappear": None
                }

                pil_image = Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
                segmented_object = pil_image.crop((x1, y1, x2, y2))
                output_path = os.path.join(output,f"{classes_name[class_id]}-{track_id} from {track_objects[track_id]['appear']} to {track_objects[track_id]['disappear']}.jpg")
                segmented_object.save(output_path)

            track_objects[track_id]["disappear"] = frame_number

            current_objects.append({
                "name": model.names[class_id],
                "bbox": ltrb
            })

            label = f"{classes_name[class_id]} {track_id}"

            color = colors[class_id]
            B, G, R = map(int,color)

            # Annotate frame
            # cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
            cv2.putText(frame, label, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Generate descriptions for actions
    descriptions = get_action_descriptions(current_objects, actions)

    # Display action descriptions
    for i, desc in enumerate(descriptions):
        cv2.putText(frame, desc, (10, 30 + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # Show the frame
    cv2.imshow('YOLO Object Detection', frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_number += 1

# Print all detected objects
print("All objects detected:")
for obj in track_objects:
    print(f"Object {track_objects[obj]['name']}-{obj} appears from frame {track_objects[obj]['appear']} to {track_objects[obj]['disappear']}")

# Release resources
cap.release()
cv2.destroyAllWindows()

#22/12: xác định được các vật thể có trong video, cho vào mảng các đồ vật xuất hiện.
# Chưa thêm mảng events các cảnh có vật thể và export ra

#24/12: đã lưu toàn bộ vật thể được track và khoảng thời gian xuất hiện, cũng như segment vật thể ra ảnh
