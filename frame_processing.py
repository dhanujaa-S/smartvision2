"""
Module 2: Frame Processing (OpenCV)
------------------------------------
Preprocessing utilities applied to each raw frame before it goes into the
object detection model: resizing, color conversion, and simple frame-rate
throttling so we don't run detection on every single frame (which is slow).
"""

import time
import cv2


def resize_frame(frame, target_width=640):
    """Resize while keeping aspect ratio, so YOLO gets a consistent input size."""
    h, w = frame.shape[:2]
    if w == target_width:
        return frame
    scale = target_width / w
    target_height = int(h * scale)
    return cv2.resize(frame, (target_width, target_height))


def to_rgb(frame):
    """YOLO/Ultralytics expects RGB; OpenCV reads frames as BGR."""
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


class FrameThrottler:
    """
    Only lets through 1 frame every `process_every_n` frames, or at most
    `max_fps` frames per second — whichever you configure. Keeps detection
    running smoothly on a laptop instead of processing every frame.
    """

    def __init__(self, process_every_n=2, max_fps=None):
        self.process_every_n = process_every_n
        self.max_fps = max_fps
        self._frame_count = 0
        self._last_processed_time = 0.0

    def should_process(self):
        self._frame_count += 1

        if self.max_fps is not None:
            now = time.time()
            min_interval = 1.0 / self.max_fps
            if now - self._last_processed_time < min_interval:
                return False
            self._last_processed_time = now
            return True

        return self._frame_count % self.process_every_n == 0


def preprocess(frame, target_width=640):
    """Convenience wrapper: resize + convert to RGB in one call."""
    resized = resize_frame(frame, target_width=target_width)
    rgb = to_rgb(resized)
    return resized, rgb
