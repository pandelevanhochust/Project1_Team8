from ultralytics import YOLO
import cv2
import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort
from PIL import Image
import os
import math
from moviepy.video.io.VideoFileClip import VideoFileClip
# from module.YOLOverse import frame, class_id, output_path

# Initialize YOLO model
model = YOLO('yolo11l.pt')  # Replace with your pretrained YOLO model path
#create directory for segmented objects

# Initialize DeepSort tracker
tracker = DeepSort(max_age=1)

#exceptional_classes
exceptional_classes = [56,57,58]
# Define actions
actions = {
    "person": {
        "ball": "playing with a ball",
        "laptop": "using a laptop",
        "bicycle": "riding a bicycle",
        "cell phone": "holding a cellphone",
        "cup": "holding a cup",
        "chair": "sitting on a chair",
        "couch": "sitting on a couch",
        "car" : "riding a car",
        "horse": "riding a horse",
        "person" : "with another person",
        "bench": "sitting on a bench"
    }
}

# # Assign unique colors for tracks
# colors = np.random.randint(0,255, size=(80,3 ))

# Initialize variables
tracks = []
track_objects = {}
close_objects = {}


#check whether two objects are close
#intersection area method
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
#distance between bounding box method
def are_close2(obj1, obj2, distance_threshold=10):
    x1, y1, x2, y2 = obj1["bbox"]
    x1_, y1_, x2_, y2_ = obj2["bbox"]
    center1 = ((x1 + x2) / 2, (y1 + y2) / 2)
    center2 = ((x1_ + x2_) / 2, (y1_ + y2_) / 2)
    distance = math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)
    return distance <= distance_threshold

# tracking two objects interaction
def action_tracker(detections,frame_number):
    # descriptions = set()
    for det in detections:
        if det["name"] == 'person':
            for obj in detections:
                if det["track_id"] != obj["track_id"] and (are_close1(det, obj) or are_close2(det,obj)):
                    action = actions.get('person', {}).get(obj["name"], None)
                    # action_tracker(det, obj,frame_number)
                    descriptions = None
                    if action:
                        descriptions = (f"A person {det['track_id']} is {action} {obj['track_id']}")
                    objects_pair = (det["track_id"], obj["track_id"])
                    if objects_pair not in close_objects:
                        close_objects[objects_pair] = {
                            "object1": det["name"],
                            "object2": obj["name"],
                            "appear": frame_number,
                            "disappear": frame_number,
                            "description" : descriptions,
                        }
                    else:
                        close_objects[objects_pair]["disappear"] = frame_number
    # des = list(descriptions)
    # for i, desc in enumerate(des):
    #     cv2.putText(frame, desc, (10, 30 + i * 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    #     print(desc)

# Hai ham xuat ra chuong trinh chinh
def object_segmentation(input):
    cap = cv2.VideoCapture(input)
    # Dau ra
    export_dir = "Export Video"
    os.makedirs(export_dir, exist_ok=True)
    # Sub directory
    images_dir = os.path.join(export_dir, "Segmented Images")
    os.makedirs(images_dir, exist_ok=True)

    segmented_objects = {}

    for track_id, obj in track_objects.items():
        x1, y1, x2, y2 = map(int, obj["bbox"])
        appear = obj["appear"]
        disappear = obj["disappear"]

        #Loc anh
        if appear == disappear or (disappear - appear <= 10):
            continue

        cap.set(cv2.CAP_PROP_POS_FRAMES, obj["appear"])
        ret, frame = cap.read()

        segmented_object = frame[y1:y2, x1:x2]

        # Folder cho tung class
        class_dir = os.path.join(images_dir, obj["name"])
        os.makedirs(class_dir, exist_ok=True)

        output_path = os.path.join(
            class_dir,
            f"{obj['name']}_{track_id}_Frames{appear}-{disappear}.jpg"
        )
        cv2.imwrite(output_path, segmented_object)

        if obj["name"] not in segmented_objects:
            segmented_objects[obj["name"]] = []

        segmented_objects[obj["name"]].append({
            "track_id": track_id,
            "bbox": (x1, y1, x2, y2),
            "appear_frame": obj["appear"],
            "disappear_frame": obj["disappear"],
            "image_path": output_path,
            "cropped_image": segmented_object
        })

    print("All objects detected:")
    for class_name, objects in segmented_objects.items():
        for obj in objects:
            print(f"{class_name}-{obj['track_id']}from frame {obj['appear_frame']} to {obj['disappear_frame']}")

    return segmented_objects

def action_segmentation(input):

    cap = cv2.VideoCapture(input)
    clip = VideoFileClip(input)
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Dau ra
    export_dir = "Export Video"
    os.makedirs(export_dir, exist_ok=True)

    # Sub directory
    videos_dir = os.path.join(export_dir, "Segmented Videos")
    os.makedirs(videos_dir, exist_ok=True)

    segmented_actions = {}

    for pair, obj in close_objects.items():
        obj1 = obj['object1']
        obj2 = obj['object2']
        appear = obj['appear']
        disappear = obj['disappear']

        # Loc video rac
        if appear == disappear or (disappear - appear <= 10):
            continue

        appear_time = appear / fps
        disappear_time = disappear / fps
        des = obj['description']

        # Ensure description or default fallback
        safe_description = des.replace(" ", "_").replace(":", "_") if des else f"{obj1}_with_{obj2}"

        output_filename = os.path.join(
            videos_dir,
            f"{safe_description}_Frames{appear}-{disappear}.mp4"
        )

        # Extract clip
        subclip = clip.subclipped(appear_time, disappear_time)
        subclip.write_videofile(output_filename, codec="libx264")
        print(f"Clip saved: {output_filename}")

        if des not in segmented_actions:
            segmented_actions[des] = []

        segmented_actions[des].append({
            "object1": obj1,
            "object2": obj2,
            "appear_time": appear,
            "disappear_time": disappear,
            "video_path": output_filename,
            "clip_object": subclip,
        })

        print("Close_objects:")
        for description, actions in segmented_actions.items():
            for action in actions:
                print(f"{action['object1']} and {action['object2']} "
                      f"from frame {int(action['appear_time'] * fps)} to frame {int(action['disappear_time'] * fps)}.")

    return segmented_actions

# Ham tracker chinh
def trackerFunc (results,input,frame,frame_number):
    cap = cv2.VideoCapture(input)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_resized = cv2.resize(frame, (width, height))

    detected_objects = []

    # Parse detections
    for box in results[0].boxes:
        bbox = box.xyxy.tolist()[0]
        x1, y1, x2, y2 = map(int, bbox)
        class_id = int(box.cls)
        confidence = float(box.conf)
        if len(bbox) == 4 and (confidence > 0.5 or (confidence <= 0.5 and class_id in exceptional_classes)):
            detected_objects.append([[x1, y1, x2 - x1, y2 - y1], confidence, class_id])

    tracks = tracker.update_tracks(detected_objects, frame=frame_resized)

    # Generate action descriptions
    current_objects = []
    for track in tracks:
        track_id = track.track_id
        if track.is_confirmed():
            ltrb = track.to_ltrb()
            class_id = track.get_det_class()
            x1, y1, x2, y2 = map(int, ltrb)
            # tracking objects
            if track_id not in track_objects:
                track_objects[track_id] = {
                    "name": model.names[class_id],
                    "bbox": ltrb,
                    "appear": frame_number,
                    "disappear": None
                }
            track_objects[track_id]["disappear"] = frame_number

            current_objects.append({
                "name": model.names[class_id],
                "bbox": ltrb,
                "track_id": track_id
            })

            # label = f"{model.names[class_id]} {track_id}"

            # color = colors[class_id]
            # B, G, R = map(int, color)

            # Annotate frame no need
            # cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
            # cv2.putText(frame, label, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Generate descriptions for actions and track
        action_tracker(current_objects, frame_number)


# main code
# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break
#     # skipping odd frames for performance optimization
#     if frame_number % 2 != 0:
#         frame_number += 1
#         continue
#
#     frame_resized = cv2.resize(frame, (width, height))
#
#     # Running YOLO
#     results = model(frame_resized)
#     detected_objects = []
#
#     # Parse detections
#     for box in results[0].boxes:
#         bbox = box.xyxy.tolist()[0]
#         x1, y1, x2, y2 = map(int, bbox)
#         class_id = int(box.cls)
#         confidence = float(box.conf)
#         if len(bbox) == 4 and (confidence > 0.5 or (confidence <= 0.5 and class_id in exceptional_classes)):
#             detected_objects.append([[x1, y1, x2 - x1, y2 - y1], confidence, class_id])
#
#     # Debugging: Print detected_objects
#     print("Detected objects passed to tracker:")
#     for obj in detected_objects:
#         print(model.names[obj[2]], obj)
#
#     # Update tracker with detected objects
#     tracks = tracker.update_tracks(detected_objects, frame=frame_resized)
#
#     # Generate action descriptions
#     current_objects = []
#     for track in tracks:
#         track_id = track.track_id
#         if track.is_confirmed():
#             ltrb = track.to_ltrb()
#             class_id = track.get_det_class()
#             x1, y1, x2, y2 = map(int, ltrb)
#             # tracking objects
#             if track_id not in track_objects:
#                 track_objects[track_id] = {
#                     "name": model.names[class_id],
#                     "bbox": ltrb,
#                     "appear": frame_number,
#                     "disappear": None
#                 }
#             track_objects[track_id]["disappear"] = frame_number
#
#             current_objects.append({
#                 "name": model.names[class_id],
#                 "bbox": ltrb,
#                 "track_id": track_id
#             })
#
#             label = f"{model.names[class_id]} {track_id}"
#
#             color = colors[class_id]
#             B, G, R = map(int, color)
#
#             # Annotate frame
#             cv2.rectangle(frame, (x1, y1), (x2, y2), (B, G, R), 2)
#             cv2.putText(frame, label, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
#
#         # Generate descriptions for actions and track
#         action_description(current_objects, actions, frame_number)
#
#     # Show the frame
#     cv2.imshow('YOLO Object Detection', frame)
#
#     # Exit on 'q' key
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
#     frame_number += 1
#
#     # Print all detected objects
# print("All objects detected:")
# for track_id, obj in track_objects.items():
#     print(f"Object {obj['name']}-{track_id} appears from frame {obj['appear']} to {obj['disappear']}")
#
# print("Close_objects:")
# for pair, obj in close_objects.items():
#     print(f"Objects {obj['object1']} {pair[0]} and {obj['object2']} {pair[1]} "
#           f"from frame {obj['appear']} to frame {obj['disappear']}.")
#
# object_segmentation(track_objects)
# action_segmentation(close_objects)
#
# # Release resources
# cap.release()
# cv2.destroyAllWindows()
