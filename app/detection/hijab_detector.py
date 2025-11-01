from ultralytics import YOLO

# Load pretrained or custom YOLO model
# Replace 'best.pt' with your own trained model path if available
model = YOLO("yolov8n.pt")

def detect_hijabs(image_path: str) -> int:
    """
    Run YOLO detection and count hijab wearers.
    """
    results = model(image_path)

    hijab_count = 0
    for result in results:
        boxes = result.boxes
        for cls in boxes.cls:
            class_name = model.names[int(cls)]
            if "hijab" in class_name.lower():
                hijab_count += 1

    return hijab_count
