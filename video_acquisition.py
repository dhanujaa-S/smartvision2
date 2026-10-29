"""
Module 1: Video Acquisition
----------------------------
Handles connecting to a video source (IP Webcam stream from a phone, or a
local webcam / video file) and yielding frames one at a time.

Usage:
    from smartvision.video_acquisition import VideoStream

    stream = VideoStream(source="http://192.168.1.5:8080/video")  # IP Webcam
    # OR
    stream = VideoStream(source=0)                                 # laptop webcam
    # OR
    stream = VideoStream(source="my_test_video.mp4")                # test video

    for frame in stream.frames():
        ...

Notes for IP Webcam (Android app):
    1. Install "IP Webcam" on your phone and start the server.
    2. Make sure the phone and laptop are on the SAME WiFi network.
    3. The app shows a URL like http://192.168.1.5:8080
       The MJPEG video feed is usually at http://192.168.1.5:8080/video

Windows note:
    Local webcams (source=0, 1, ...) are opened with the DirectShow backend
    (cv2.CAP_DSHOW) instead of the default Media Foundation backend, since
    MSMF frequently throws "can't grab frame" errors on Windows with many
    webcam drivers. IP Webcam / video file sources are unaffected.
"""

import time
import cv2


class VideoStream:
    def __init__(self, source, reconnect_attempts=5, reconnect_delay=2.0):
        """
        source: int (0 for default webcam), str (video file path), or
                 str URL (e.g. IP Webcam MJPEG stream URL)
        """
        self.source = source
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self.cap = None
        self._connect()

    def _connect(self):
        if isinstance(self.source, int):
            # Local webcam on Windows: DirectShow is far more reliable than
            # the default Media Foundation backend.
            self.cap = cv2.VideoCapture(self.source, cv2.CAP_DSHOW)
        else:
            # Video file path or network stream URL (e.g. IP Webcam)
            self.cap = cv2.VideoCapture(self.source)

        if not self.cap.isOpened():
            raise ConnectionError(f"Could not open video source: {self.source}")
        print(f"[VideoAcquisition] Connected to source: {self.source}")

    def _reconnect(self):
        print("[VideoAcquisition] Stream dropped, attempting to reconnect...")
        for attempt in range(1, self.reconnect_attempts + 1):
            try:
                if self.cap is not None:
                    self.cap.release()
                self._connect()
                print(f"[VideoAcquisition] Reconnected on attempt {attempt}")
                return True
            except ConnectionError:
                print(f"[VideoAcquisition] Reconnect attempt {attempt} failed")
                time.sleep(self.reconnect_delay)
        return False

    def frames(self):
        """Generator that yields frames (numpy arrays, BGR) one at a time."""
        while True:
            ok, frame = self.cap.read()
            if not ok or frame is None:
                if not self._reconnect():
                    print("[VideoAcquisition] Giving up on stream.")
                    break
                continue
            yield frame

    def get_fps(self):
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        return fps if fps and fps > 0 else 30.0

    def release(self):
        if self.cap is not None:
            self.cap.release()


if __name__ == "__main__":
    # Quick manual test: replace with your IP Webcam URL or 0 for laptop camera
    stream = VideoStream(source=0)
    count = 0
    for frame in stream.frames():
        count += 1
        cv2.imshow("SmartVision - Video Acquisition Test", frame)
        if cv2.waitKey(1) & 0xFF == ord("q") or count > 200:
            break
    stream.release()
    cv2.destroyAllWindows()