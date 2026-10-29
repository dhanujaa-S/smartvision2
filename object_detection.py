"""
Module 3: Object Detection (YOLOv8)
-------------------------------------
Wraps an Ultralytics YOLOv8 model. Start with the pretrained "yolov8n.pt"
for a working baseline. Once your custom model (trained on your own
indoor-objects-detection dataset in Module 4) is ready, just point
`model_path` at your new weights file — nothing else in the pipeline
needs to change.
"""

from dataclasses import dataclass
from ultralytics import YOLO


@dataclass
class Detection:
    label: str
    confidence: float
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def center(self):
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    @property
    def box_area(self):
        return (self.x2 - self.x1) * (self.y2 - self.y1)


class ObjectDetector:
    def __init__(self, model_path="yolov8n.pt", confidence_threshold=0.5):
        """
        model_path: "yolov8n.pt" (pretrained baseline) or a path to your
                    custom-trained weights, e.g. "runs/detect/train/weights/best.pt"
        """
        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold

    def detect(self, frame_rgb):
        """
        frame_rgb: a single frame (numpy array, RGB).
        Returns a list of Detection objects.
        """
        results = self.model.predict(
            source=frame_rgb,
            conf=self.confidence_threshold,
            verbose=False,
        )

        detections = []
        for result in results:
            names = result.names
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
                detections.append(
                    Detection(
                        label=names[cls_id],
                        confidence=conf,
                        x1=x1, y1=y1, x2=x2, y2=y2,
                    )
                )
        return detections

    def draw_detections(self, frame_bgr, detections):
        """Optional: draw boxes on a BGR frame for on-screen debugging."""
        import cv2
        for d in detections:
            p1 = (int(d.x1), int(d.y1))
            p2 = (int(d.x2), int(d.y2))
            cv2.rectangle(frame_bgr, p1, p2, (0, 255, 0), 2)
            label = f"{d.label} {d.confidence:.2f}"
            cv2.putText(frame_bgr, label, (p1[0], max(p1[1] - 10, 0)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return frame_bgr
