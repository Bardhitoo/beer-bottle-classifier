import os
import numpy as np

from loguru import logger
from ultralytics import YOLO


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_yolo(yolo_model_path: str, device: str = 'cuda:0') -> YOLO:
    """
    Load the trained YOLO classification model.
    
    Device: ("cpu" | "cuda:0")
    """
    try:
        logger.info(f"Loading YOLO to {device.upper()}")
        yolo_model = YOLO(os.path.join(ROOT_DIR, yolo_model_path))
    except Exception as e:
        logger.error(f"Please ensure the correct file path! {e}")
        exit(-1)
    else:
        logger.success("Model loaded successfully!")

    dry_run(yolo_model, device)

    return yolo_model


def dry_run(yolo_model: YOLO, device: str = 'cuda:0'):
    """
    Make a prediction with YOLOv8 to ensure YOLO and CUDA are loaded successfully 
    before intial inference.

    Device: ("cpu" | "cuda:0")
    """
    logger.info("\t Dry run starting...")

    sample_data = np.random.randint(0, 255, (1920, 1080, 3)).astype(np.uint8)
    yolo_model(sample_data, device=device)

    logger.info("\t Dry run successful!")
