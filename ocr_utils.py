import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import os
import logging

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\tesseract.exe' 

def preprocess_image(image_path):
    """
    Preprocess image using OpenCV for better OCR results.
    """
    try:
        image = cv2.imread(image_path)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Increase contrast and brightness
        gray = cv2.convertScaleAbs(gray, alpha=2.0, beta=50)

        # Optional: Gaussian blur
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        # Thresholding
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return Image.fromarray(thresh)

    except Exception as e:
        logging.error(f"Preprocessing failed: {e}")
        return Image.open(image_path)

def clean_extracted_text(text):
    if not text:
        return ""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    cleaned_text = '\n'.join(lines)
    replacements = {
        '|': 'I',
        'O': '0',
        '§': 'S',
        'ﬁ': 'fi',
        'ﬂ': 'fl',
        '—': '-',
        '’': "'",
        '"': '"'
    }
    for old, new in replacements.items():
        cleaned_text = cleaned_text.replace(old, new)
    return cleaned_text

def extract_text_from_image(image_path, preprocess=True):
    """
    Extract text using Tesseract with fallback modes.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"File not found: {image_path}")

    try:
        image = preprocess_image(image_path) if preprocess else Image.open(image_path)

        text_results = []

        # Try multiple PSM modes
        configs = [
            '--oem 3 --psm 6 -l eng -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ:.%₹,/-',
            '--oem 3 --psm 4 -l eng',
            '--oem 3 --psm 11 -l eng'
        ]

        for config in configs:
            try:
                result = pytesseract.image_to_string(image, config=config)
                if result:
                    text_results.append(result)
            except:
                continue

        if text_results:
            extracted = max(text_results, key=len)
        else:
            extracted = pytesseract.image_to_string(image)

        return clean_extracted_text(extracted)

    except Exception as e:
        logging.error(f"OCR failed: {e}")
        raise Exception(f"OCR failed: {e}")
