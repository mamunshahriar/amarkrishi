"""
Amar Krishi - Leaf Image Validator
Runs BEFORE disease prediction to reject images that clearly aren't plant
leaves (faces, animals, cars, buildings, food, random objects).

v2: the original color-ratio-only heuristic was too permissive on real
photos (a face/selfie with any warm-toned background could clear a 12%
"vegetation hue" bar). This version adds:
  1. Haar-cascade face detection as a hard rejection signal.
  2. A much stricter vegetation-dominance requirement (a real leaf
     close-up should fill most of the frame, not just be present in it).
  3. A narrower, higher-saturation green/yellow-green hue band that
     doesn't overlap with skin tones or wood/tan backgrounds.
"""

import os
import cv2
import numpy as np

_FACE_CASCADE_PATH = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
_face_cascade = cv2.CascadeClassifier(_FACE_CASCADE_PATH) if os.path.exists(_FACE_CASCADE_PATH) else None


def _load_image(path):
    img = cv2.imread(path)
    if img is None:
        return None
    return img


def _has_face(gray):
    if _face_cascade is None or _face_cascade.empty():
        return False
    faces = _face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
    if len(faces) == 0:
        return False
    frame_area = gray.shape[0] * gray.shape[1]
    return any((w * h) / frame_area > 0.03 for (x, y, w, h) in faces)


def _vegetation_ratio(hsv):
    lower = np.array([25, 40, 30])
    upper = np.array([90, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    return float(np.count_nonzero(mask)) / mask.size


def _skin_tone_ratio(hsv):
    lower = np.array([0, 30, 60])
    upper = np.array([25, 150, 255])
    mask = cv2.inRange(hsv, lower, upper)
    return float(np.count_nonzero(mask)) / mask.size


def _edge_texture_score(gray):
    edges = cv2.Canny(gray, 60, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=60, maxLineGap=8)
    return 0 if lines is None else len(lines)


def is_leaf_image(image_path):
    """
    Returns (is_leaf: bool, confidence: float 0-100, reason: str).
    """
    img = _load_image(image_path)
    if img is None:
        return False, 0.0, "unreadable_image"

    img = cv2.resize(img, (300, 300))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if _has_face(gray):
        return False, 0.0, "human_face_detected"

    green_ratio = _vegetation_ratio(hsv)
    skin_ratio = _skin_tone_ratio(hsv)
    straight_lines = _edge_texture_score(gray)

    if skin_ratio > 0.25:
        return False, round((1 - skin_ratio) * 100, 2), "likely_skin"

    if straight_lines > 40 and green_ratio < 0.30:
        return False, round(green_ratio * 100, 2), "likely_manmade_object"

    if green_ratio < 0.30:
        return False, round(green_ratio * 100, 2), "insufficient_vegetation_color"

    confidence = min(99.0, round(50 + green_ratio * 50, 2))
    return True, confidence, "vegetation_detected"