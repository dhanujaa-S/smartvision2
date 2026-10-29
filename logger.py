"""
Module 8: Data Logging & Analytics
-------------------------------------
Logs every detection event to a CSV (and can export a summary to Excel)
so you have a record of frame counts, objects detected, timestamps, and
FPS -- useful for your report / evaluation section.
"""

import csv
import os
import time
from datetime import datetime

import pandas as pd


class DetectionLogger:
    def __init__(self, csv_path="results.csv"):
        self.csv_path = csv_path
        self._file_exists = os.path.exists(csv_path)
        self._csv_file = open(csv_path, mode="a", newline="", encoding="utf-8")
        self._writer = csv.writer(self._csv_file)
        if not self._file_exists:
            self._writer.writerow([
                "timestamp", "frame_number", "label", "confidence",
                "horizontal", "distance", "sentence"
            ])
        self._start_time = time.time()
        self._frame_count = 0

    def log_detection(self, frame_number, positioned_detection, confidence, sentence=""):
        self._writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            frame_number,
            positioned_detection.label,
            round(confidence, 3),
            positioned_detection.horizontal,
            positioned_detection.distance,
            sentence,
        ])
        self._csv_file.flush()

    def mark_frame_processed(self):
        self._frame_count += 1

    def summary(self):
        elapsed = time.time() - self._start_time
        avg_fps = self._frame_count / elapsed if elapsed > 0 else 0
        return {
            "frames_processed": self._frame_count,
            "elapsed_seconds": round(elapsed, 2),
            "average_fps": round(avg_fps, 2),
        }

    def print_summary(self):
        s = self.summary()
        print(f"[Logger] Frames processed: {s['frames_processed']}")
        print(f"[Logger] Elapsed time: {s['elapsed_seconds']}s")
        print(f"[Logger] Average FPS: {s['average_fps']}")

    def export_to_excel(self, excel_path="results.xlsx"):
        """Converts the CSV log into a formatted Excel file for the report."""
        df = pd.read_csv(self.csv_path)
        df.to_excel(excel_path, index=False)
        print(f"[Logger] Exported {len(df)} rows to {excel_path}")

    def close(self):
        self._csv_file.close()
