from ultralytics import YOLO
import cv2
import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort
from moviepy import VideoFileClip, concatenate_videoclips


# Initialize YOLO model
model = YOLO('yolo11m.pt')  # Replace with your pretrained YOLO model path

# Initialize DeepSort tracker
tracker = DeepSort(max_age=1)

# Load COCO class names
with open("D:\\PyLesson\\Videos\\data\\classes.names") as f:
    classes_name = f.read().strip().split("\n")

# Assign unique colors for tracks
colors = np.random.randint(0,255, size=(len(classes_name),3 ))
tracks = []

# Define actions
actions = {
    "person": {
        "ball": "playing with a ball",
        "laptop": "using a laptop",
        "bicycle": "riding a bicycle",
        "cell phone": "is holding a cellphone",
        "cup": "is holding a cup",
        "chair": "is sitting on a chair",
        "couch": "is sitting on a couch"
    }
}

def are_close(obj1, obj2, threshold=50):
    x1, y1, x2, y2 = obj1["bbox"]
    x1_, y1_, x2_, y2_ = obj2["bbox"]
    center1 = ((x1 + x2) / 2, (y1 + y2) / 2)
    center2 = ((x1_ + x2_) / 2, (y1_ + y2_) / 2)
    distance = np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
    return distance < threshold

def get_action_descriptions(detections, actions):
    descriptions = set()
    for det in detections:
        if det['name'] == 'person':
            for obj in detections:
                # if obj['name'] != 'person' and are_close(det, obj):
                if obj['name'] != 'person':
                    action = actions.get('person', {}).get(obj['name'], None)
                    if action:
                        descriptions.add(f"A person is {action}")
    return list(descriptions)

# Initialize video capture
cap = cv2.VideoCapture("D:\\PyLesson\\Videos\\12_18KhanhNgoc.mp4")  # Replace with your input video path

fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO inference
    results = model(frame)

    # Extract detections and format for DeepSort
    detected_objects = []
    all_objects = []

    for box in results[0].boxes:
        bbox = box.xyxy.tolist()[0]

        x1, y1, x2, y2 = map(int, bbox)
        class_id = int(box.cls)
        confidence = float(box.conf)

        # Validate bbox to ensure it has 4 elements
        if len(bbox) == 4:
            all_objects.append([classes_name[class_id],confidence])

            if confidence > 0.5:
                detected_objects.append([ [x1, y1, x2-x1, y2 - y1], confidence, class_id ])
            elif confidence <= 0.5 and (class_id == 56 or class_id == 57):
                detected_objects.append([ [x1, y1, x2-x1, y2 - y1], confidence, class_id ])


    # Debugging: Print detected_objects
    print("Detected objects passed to tracker:")
    for obj in all_objects:
        print(obj)

    # Update tracker with detected objects
    tracks = tracker.update_tracks(
        detected_objects,
        frame=frame
    )

    # Generate action descriptions
    track_objects = []
    for track in tracks:
        if track.is_confirmed():
            ltrb = track.to_ltrb()
            class_id = track.get_det_class()
            track_id = track.track_id
            x1, y1, x2, y2 = map(int, ltrb)

            label = f"{classes_name[class_id]}"

            color = colors[class_id]
            B, G, R = map(int,color)

            track_objects.append({
                "name": model.names[class_id],
                "bbox": ltrb
            })

            # Annotate frame
            cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
            cv2.rectangle(frame, (x1 - 1, y1 - 20), (x1 + len(label) * 12, y1), (B, G, R), -1)
            cv2.putText(frame, label, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            # Generate descriptions for actions
            descriptions = get_action_descriptions(track_objects, actions)

            # Display action descriptions
            y_offset = 30
            for desc in descriptions:
                cv2.putText(frame, desc, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                y_offset += 30

    # Show the frame
    cv2.imshow('YOLOv8 Action Detection', frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources

cv2.destroyAllWindows()

# Print all detected objects
for obj in all_objects:
    print(f"Detected: {obj['name']} with confidence {obj['confidence']:.2f}")
    

output_path = "D:\\PyLesson\\Videos\\KhanhNgoc.mp4"
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec video (có thể dùng 'XVID', 'mp4v', vv.)

# Tạo đối tượng VideoWriter để ghi video
out = cv2.VideoWriter(output_path, fourcc, fps, (width,height))

cap.release()
out.release()