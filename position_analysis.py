"""
Module 5: Position & Distance Analysis
-----------------------------------------
Takes raw Detection objects (bounding boxes) and converts them into
spatial information a blind user actually needs:
  - Horizontal position: left / center / right
  - Rough distance: near / medium / far  (estimated from how much of the
    frame the bounding box occupies -- bigger box = closer object)

This is the module that turns "there's a chair at pixel (320, 400)" into
"chair, center, near" -- which Module 6 then turns into a sentence.
"""

from dataclasses import dataclass
from .object_detection import Detection


@dataclass
class PositionedDetection:
    label: str
    confidence: float
    horizontal: str   # "left" | "center" | "right"
    distance: str      # "near" | "medium" | "far"


def analyze_position(detection: Detection, frame_width: int, frame_height: int,
                      left_bound=0.35, right_bound=0.65,
                      near_area_ratio=0.25, far_area_ratio=0.06) -> PositionedDetection:
    """
    left_bound / right_bound: fraction of frame width that divides
        left / center / right zones (defaults: left <35%, center 35-65%, right >65%)
    near_area_ratio / far_area_ratio: fraction of total frame area the
        bounding box must cover to be considered "near" or "far"
    """
    cx, _ = detection.center
    normalized_x = cx / frame_width

    if normalized_x < left_bound:
        horizontal = "left"
    elif normalized_x > right_bound:
        horizontal = "right"
    else:
        horizontal = "center"

    frame_area = frame_width * frame_height
    area_ratio = detection.box_area / frame_area if frame_area > 0 else 0

    if area_ratio >= near_area_ratio:
        distance = "near"
    elif area_ratio <= far_area_ratio:
        distance = "far"
    else:
        distance = "medium"

    return PositionedDetection(
        label=detection.label,
        confidence=detection.confidence,
        horizontal=horizontal,
        distance=distance,
    )


def analyze_all(detections, frame_width, frame_height):
    return [analyze_position(d, frame_width, frame_height) for d in detections]
