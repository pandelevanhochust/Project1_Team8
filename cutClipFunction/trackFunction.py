from ultralytics import YOLO
import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort
import os
import math
from moviepy.video.io.VideoFileClip import VideoFileClip

model = YOLO('yolo11m.pt')
tracker = DeepSort(max_age=1)

#exceptional_classes
# exceptional_classes = []
# Define actions
actions = {
    "person": {
        "ball": "playing with a ball",
        "laptop": "using a laptop",
        "bicycle": "riding a bicycle",
        "cell phone": "holding a cellphone",
        "cup": "holding a cup",
        "chair": "sitting on a chair",
        "sofa": "sitting on a sofa",
        "car" : "riding a car",
        "horse": "riding a horse",
        "person" : "with another person",
        "bench": "sitting on a bench"
    }
}

# Initialize variables
tracks = []
track_objects = {}
close_objects = {}

# Ham xet su tuong tac
def are_close(obj1, obj2, iou_threshold=0.1, distance_threshold=10):
    x1, y1, x2, y2 = obj1["bbox"]
    x1_, y1_, x2_, y2_ = obj2["bbox"]

    # Calculate IoU
    xi1 = max(x1, x1_)
    yi1 = max(y1, y1_)
    xi2 = min(x2, x2_)
    yi2 = min(y2, y2_)
    intersection_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)

    bbox1_area = (x2 - x1) * (y2 - y1)
    bbox2_area = (x2_ - x1_) * (y2_ - y1_)
    union_area = bbox1_area + bbox2_area - intersection_area
    iou = intersection_area / union_area if union_area > 0 else 0

    # Calculate distance between centers
    center1 = ((x1 + x2) / 2, (y1 + y2) / 2)
    center2 = ((x1_ + x2_) / 2, (y1_ + y2_) / 2)
    distance = math.sqrt((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2)

    # Check IoU or distance thresholds
    return iou >= iou_threshold or distance <= distance_threshold

# tracking two objects interaction
def action_tracker(detections,frame_number):
    for det in detections:
        if det["name"] == 'person':
            for obj in detections:
                if det["track_id"] != obj["track_id"] and are_close(det, obj):
                    action = actions.get('person', {}).get(obj["name"], None)
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

# Hai ham xuat ra chuong trinh chinh
def object_segmentation(input):
    cap = cv2.VideoCapture(input)
    # Dau ra
    export_dir = "exportVideo"
    os.makedirs(export_dir, exist_ok=True)
    # Sub directory
    images_dir = os.path.join(export_dir, "segmentedImages")
    os.makedirs(images_dir, exist_ok=True)

    segmented_objects = {}

    for track_id, obj in track_objects.items():
        x1, y1, x2, y2 = map(int, obj["bbox"])
        appear = obj["appear"]
        disappear = obj["disappear"]

        #Loc anh xuat hien duoi 1s
        if appear == disappear or (disappear - appear <= 24):
            continue

        cap.set(cv2.CAP_PROP_POS_FRAMES, obj["appear"])
        ret, frame = cap.read()

        segmented_object = frame[y1:y2, x1:x2]

        # Folder cho tung class
        class_dir = os.path.join(images_dir, obj["name"])
        os.makedirs(class_dir, exist_ok=True)

        output_path = os.path.join(
            class_dir,
            f"{obj['name']}_{track_id}_Frames{appear}_{disappear}.jpg"
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
    #Loai bo vat the xuat hien mot lan duy nhat
    filtered_segmented_objects = {
        class_name: objects
        for class_name, objects in segmented_objects.items()
        if len(objects) > 1
    }

    print("All objects detected:")
    for class_name, objects in filtered_segmented_objects.items():
        for obj in objects:
            print(f"{class_name}-{obj['track_id']}from frame {obj['appear_frame']} to {obj['disappear_frame']}")
    return filtered_segmented_objects

def action_segmentation(input):

    cap = cv2.VideoCapture(input)
    clip = VideoFileClip(input)
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Dau ra
    export_dir = "exportVideo"
    os.makedirs(export_dir, exist_ok=True)

    # Sub directory
    videos_dir = os.path.join(export_dir, "segmentedVideos")
    os.makedirs(videos_dir, exist_ok=True)

    segmented_actions = {}

    for pair, obj in close_objects.items():
        obj1 = obj['object1']
        obj2 = obj['object2']
        appear = obj['appear']
        disappear = obj['disappear']

        # Loc video rac
        if appear == disappear or (disappear - appear <= 24):
            continue

        appear_time = appear / fps
        disappear_time = disappear / fps
        des = obj['description']

        # Ensure description or default fallback
        safe_description = des.replace(" ", "_").replace(":", "_") if des else f"{obj1}_with_{obj2}"

        output_filename = os.path.join(
            videos_dir,
            f"{safe_description}_Frames_{appear}_{disappear}.mp4"
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
                f"from frame {int(action['appear_time'])} to frame {int(action['disappear_time'])}.")

    return segmented_actions

# Ham tracker chinh
def trackerFunc (results,width,height,frame,frame_number):
    frame_resized = cv2.resize(frame, (width, height))
    detected_objects = []

    #Phân tích results
    for box in results[0].boxes:
        bbox = box.xyxy.tolist()[0]
        x1, y1, x2, y2 = map(int, bbox)
        class_id = int(box.cls)
        confidence = float(box.conf)
        if len(bbox) == 4 and (confidence > 0.5):
            detected_objects.append([[x1, y1, x2 - x1, y2 - y1], confidence, class_id])

    tracks = tracker.update_tracks(detected_objects, frame=frame_resized)

    # Tracking
    current_objects = []
    for track in tracks:
        track_id = track.track_id
        if track.is_confirmed():
            ltrb = track.to_ltrb()
            class_id = track.get_det_class()
            if track_id not in track_objects:
                track_objects[track_id] = {
                    "name": model.names[class_id],
                    "bbox": ltrb,
                    "appear": frame_number,
                    "disappear": None
                }
            track_objects[track_id]["disappear"] = frame_number + 2

            current_objects.append({
                "name": model.names[class_id],
                "bbox": ltrb,
                "track_id": track_id
            })
        action_tracker(current_objects, frame_number)



