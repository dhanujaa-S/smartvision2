"""
Module 10: Deployment / Packaging (Main Pipeline)
----------------------------------------------------
Wires every module together into one runnable end-to-end pipeline:

  Video Acquisition -> Frame Processing -> Object Detection
      -> Position Analysis -> Text Generation -> Text-to-Speech
      -> Data Logging

Object Detection can run two ways:
  1. Local pretrained/custom YOLO weights (default) -- object_detection.py
  2. Roboflow cloud API, using your custom-trained model -- roboflow_detector.py
     (requires internet + an API key)

Run (local model):
    python main.py --source 0 --show-window

Run (Roboflow cloud model):
    python main.py --source 0 --show-window --backend roboflow --api-key YOUR_KEY --roboflow-model indoor-navigation-objects/1
"""

import argparse
import cv2

from smartvision.video_acquisition import VideoStream
from smartvision.frame_processing import preprocess, FrameThrottler
from smartvision.object_detection import ObjectDetector
from smartvision.position_analysis import analyze_all
from smartvision.text_generation import generate_announcements
from smartvision.tts_module import VoiceGuide
from smartvision.logger import DetectionLogger


def parse_args():
    parser = argparse.ArgumentParser(description="SmartVision - AI Vision Assistant")
    parser.add_argument("--source", default=0,
                         help="0 for webcam, a video file path, or an IP Webcam stream URL")
    parser.add_argument("--model", default="yolov8n.pt",
                         help="Path to local YOLOv8 weights (used when --backend local)")
    parser.add_argument("--backend", default="local", choices=["local", "roboflow"],
                         help="Detection backend: 'local' (default) or 'roboflow' (cloud API)")
    parser.add_argument("--api-key", default=None,
                         help="Roboflow private API key (required when --backend roboflow)")
    parser.add_argument("--roboflow-model", default=None,
                         help="Roboflow model id, e.g. 'indoor-navigation-objects/1' (required when --backend roboflow)")
    parser.add_argument("--language", default="en", choices=["en", "ta"],
                         help="Voice guidance language: en (English) or ta (Tamil)")
    parser.add_argument("--confidence", type=float, default=0.5,
                         help="Minimum detection confidence threshold (local backend)")
    parser.add_argument("--show-window", action="store_true",
                         help="Show a debug window with bounding boxes drawn")
    parser.add_argument("--csv-path", default="results.csv",
                         help="Where to save the detection log CSV")
    parser.add_argument("--cooldown", type=float, default=3.0,
                         help="Minimum seconds between voice announcements")
    return parser.parse_args()


def build_detector(args):
    if args.backend == "roboflow":
        if not args.api_key or not args.roboflow_model:
            raise ValueError("--backend roboflow requires both --api-key and --roboflow-model")
        from smartvision.roboflow_detector import RoboflowDetector
        print(f"[Main] Using Roboflow cloud model: {args.roboflow_model}")
        return RoboflowDetector(
            api_key=args.api_key,
            model_id=args.roboflow_model,
            confidence_threshold=0.3,
        )
    else:
        print(f"[Main] Using local model: {args.model}")
        return ObjectDetector(model_path=args.model, confidence_threshold=args.confidence)


def main():
    args = parse_args()

    source = args.source
    try:
        source = int(source)
    except (ValueError, TypeError):
        pass

    stream = VideoStream(source=source)
    detector = build_detector(args)
    voice = VoiceGuide(cooldown_seconds=args.cooldown)
    logger = DetectionLogger(csv_path=args.csv_path)
    throttler = FrameThrottler(process_every_n=3)

    frame_number = 0
    print("[Main] SmartVision running. Press 'q' in the debug window (if shown) to stop, or Ctrl+C in terminal.")

    try:
        for raw_frame in stream.frames():
            frame_number += 1
            logger.mark_frame_processed()

            if not throttler.should_process():
                continue

            resized_bgr, frame_rgb = preprocess(raw_frame)
            h, w = resized_bgr.shape[:2]

            detections = detector.detect(frame_rgb)
            positioned = analyze_all(detections, frame_width=w, frame_height=h)
            sentences = generate_announcements(positioned, language=args.language, max_announcements=2)

            for pd, det, sentence in zip(positioned, detections, sentences + [""] * len(detections)):
                logger.log_detection(frame_number, pd, det.confidence, sentence)

            if sentences:
                voice.say(" ".join(sentences), language=args.language)

            if args.show_window:
                if hasattr(detector, "draw_detections"):
                    annotated = detector.draw_detections(resized_bgr, detections)
                else:
                    annotated = resized_bgr.copy()
                    for d in detections:
                        p1 = (int(d.x1), int(d.y1))
                        p2 = (int(d.x2), int(d.y2))
                        cv2.rectangle(annotated, p1, p2, (0, 255, 0), 2)
                        cv2.putText(annotated, f"{d.label} {d.confidence:.2f}",
                                    (p1[0], max(p1[1] - 10, 0)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.imshow("SmartVision", annotated)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    except KeyboardInterrupt:
        print("\n[Main] Stopped by user.")

    finally:
        stream.release()
        cv2.destroyAllWindows()
        logger.print_summary()
        logger.export_to_excel(excel_path=args.csv_path.replace(".csv", ".xlsx"))
        logger.close()


if __name__ == "__main__":
    main()