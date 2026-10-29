# SmartVision — AI-Powered Smart Vision Assistant

Rebuilt from scratch, split into clean modules.

## Project Structure

```
SmartVision/
├── smartvision/
│   ├── __init__.py
│   ├── video_acquisition.py      # Module 1: camera / IP Webcam stream
│   ├── frame_processing.py       # Module 2: OpenCV preprocessing
│   ├── object_detection.py       # Module 3: YOLOv8 wrapper
│   ├── position_analysis.py      # Module 5: left/right/near/far logic
│   ├── text_generation.py        # Module 6: sentence generation (EN/TA)
│   ├── tts_module.py             # Module 7: voice output (EN/TA)
│   └── logger.py                 # Module 8: CSV/Excel logging
├── main.py                       # Module 10: full pipeline, run this
├── requirements.txt
└── README.md
```

**Module 4 (Dataset & Custom Model Training)** and **Module 9 (Testing &
Evaluation)** are intentionally NOT included here — that's the part you're
doing yourselves: collecting/annotating the `indoor-objects-detection`
dataset, fine-tuning YOLOv8 on it, and benchmarking pretrained vs.
custom-trained performance. Everything here is built so your trained
weights drop straight in — just point `--model` at your `best.pt` file.

## Setup

```bash
pip install -r requirements.txt
```

If `playsound` gives you trouble on Windows, this exact pinned version
(`1.2.2`) avoids the common `PlaysoundException` bug.

## Running it

```bash
# Laptop webcam, English voice, on-screen debug window
python main.py --source 0 --show-window

# IP Webcam stream from your phone (replace with your actual IP)
python main.py --source "http://192.168.1.5:8080/video"

# Tamil voice guidance
python main.py --source 0 --language ta

# Once your custom-trained model is ready
python main.py --source 0 --model runs/detect/train/weights/best.pt
```

Outputs `results.csv` and `results.xlsx` in the project root with every
detection logged (timestamp, label, confidence, position, distance,
spoken sentence) — useful directly for your evaluation section.

## How a frame flows through the pipeline

```
Mobile Camera / Webcam
   -> Video Acquisition   (video_acquisition.py)
   -> Frame Processing    (frame_processing.py)
   -> Object Detection    (object_detection.py)      <- Module 4 plugs in here
   -> Position Analysis   (position_analysis.py)
   -> Text Generation     (text_generation.py)
   -> Text-to-Speech      (tts_module.py)
   -> Data Logging        (logger.py)                 <- Module 9 evaluation reads this
```

## Next steps for you

1. Collect and annotate the indoor-objects dataset.
2. Train YOLOv8 on it (`yolo detect train data=... model=yolov8n.pt`),
   which produces `runs/detect/train/weights/best.pt`.
3. Benchmark that against the pretrained baseline using the logged CSV
   data (accuracy, FPS, per-class performance).
4. Tune the thresholds in `position_analysis.py`
   (`left_bound`, `right_bound`, `near_area_ratio`, `far_area_ratio`) once
   you have real test footage — the defaults are reasonable starting
   points, not final numbers.
