"""
Amar Krishi - Leaf Image Validator
Runs BEFORE disease prediction to reject images that clearly aren't plant
leaves (faces, animals, cars, buildings, food, random objects).

Implementation choice: a lightweight OpenCV/NumPy color+shape heuristic
instead of a full CNN (MobileNetV2/EfficientNet). Rationale:
  - Zero extra model weights to ship/download — works instantly on Render's
    free tier without hitting memory/slug-size limits.
  - opencv-python-headless + numpy are already dependencies.
  - Good enough to catch the requested cases (people, cars, buildings, food,
    random objects) which are overwhelmingly non-green / non-organic in
    color and texture compared to a leaf close-up.

This is intentionally isolated behind `is_leaf_image()` so it can be swapped
for a real MobileNetV2/EfficientNet TensorFlow classifier later without
touching any calling code — just replace the body of that function.
"""

import cv2
import numpy as np


def _load_image(path):
    img = cv2.imread(path)
    if img is None:
        return None
    return img


def _green_vegetation_ratio(hsv):
    # Broad "vegetation" hue range covering healthy green through
    # yellowing/browning diseased leaf tissue.
    lower = np.array([15, 25, 25])
    upper = np.array([95, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    return float(np.count_nonzero(mask)) / mask.size


def _skin_tone_ratio(hsv):
    # Rough human-skin hue/saturation band, used to help rule out selfies.
    lower = np.array([0, 30, 60])
    upper = np.array([25, 150, 255])
    mask = cv2.inRange(hsv, lower, upper)
    return float(np.count_nonzero(mask)) / mask.size


def _edge_texture_score(gray):
    # Leaves have organic, irregular vein/edge patterns; man-made objects
    # (buildings, cars) tend to have strong straight-line edges instead.
    edges = cv2.Canny(gray, 60, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=60, maxLineGap=8)
    straight_line_count = 0 if lines is None else len(lines)
    return straight_line_count


def is_leaf_image(image_path):
    """
    Returns (is_leaf: bool, confidence: float 0-100, reason: str).
    `reason` is only used for logging/debugging, not shown to the user.
    """
    img = _load_image(image_path)
    if img is None:
        return False, 0.0, "unreadable_image"

    img = cv2.resize(img, (300, 300))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    green_ratio = _green_vegetation_ratio(hsv)
    skin_ratio = _skin_tone_ratio(hsv)
    straight_lines = _edge_texture_score(gray)

    # Heuristic decision:
    # - Needs a meaningful amount of vegetation-colored pixels.
    # - Rejected if dominated by skin tone (likely a person).
    # - Rejected if dominated by strong straight-line geometry (buildings/cars)
    #   AND vegetation coverage is low.
    if skin_ratio > 0.35 and green_ratio < 0.30:
        return False, round((1 - skin_ratio) * 100, 2), "likely_skin"

    if straight_lines > 40 and green_ratio < 0.20:
        return False, round(green_ratio * 100, 2), "likely_manmade_object"

    if green_ratio < 0.12:
        return False, round(green_ratio * 100, 2), "insufficient_vegetation_color"

    confidence = min(99.0, round(50 + green_ratio * 50, 2))
    return True, confidence, "vegetation_detected"