import json
import os
import hashlib
import subprocess
from datetime import datetime
from PIL import Image
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

def calculate_hash(file_path):
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def extract_image_metadata(file_path):
    metadata = {}
    try:
        result = subprocess.run(
            ["exiftool", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.stdout:
            for line in result.stdout.splitlines():
                key, _, value = line.partition(": ")
                metadata[key.strip()] = value.strip()
        else:
            print(f"No metadata found for {file_path}")
    except Exception as e:
        print(f"Error extracting image metadata: {e}")
    return metadata

def detect_image_tampering(file_path):
    tampering_data = {"tampering_suspected": False}
    try:
        image = cv2.imread(file_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        (h, w) = gray_image.shape
        split_images = [
            gray_image[0:h//2, 0:w//2],
            gray_image[0:h//2, w//2:],
            gray_image[h//2:, 0:w//2],
            gray_image[h//2:, w//2:]
        ]
        ssim_scores = []
        for i in range(len(split_images)):
            for j in range(i + 1, len(split_images)):
                score, _ = ssim(split_images[i], split_images[j], full=True)
                ssim_scores.append(score)
        if any(score < 0.5 for score in ssim_scores):
            tampering_data["tampering_suspected"] = True
        tampering_data["ssim_scores"] = ssim_scores
    except Exception as e:
        print(f"Error during tampering detection: {e}")
    return tampering_data

def extract_low_level_metadata(file_path):
    metadata = {}
    try:
        parser = createParser(file_path)
        if parser:
            metadata_obj = extractMetadata(parser)
            if metadata_obj:
                for line in metadata_obj.exportPlaintext():
                    key, _, value = line.partition(": ")
                    metadata[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error extracting low-level metadata: {e}")
    return metadata

def save_metadata_to_pdf(metadata, tampering_analysis, output_pdf="output_metadata.pdf"):
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter
    y_position = height - 40
    margin = 40
    line_height = 12

    c.drawString(margin, y_position, "Metadata and Tampering Analysis")
    y_position -= line_height * 2

    formatted_metadata = json.dumps(metadata, indent=4)
    formatted_tampering = json.dumps(tampering_analysis, indent=4)

    c.drawString(margin, y_position, "Metadata:")
    y_position -= line_height
    for line in formatted_metadata.splitlines():
        c.drawString(margin, y_position, line)
        y_position -= line_height
        if y_position < 40:
            c.showPage()
            y_position = height - 40

    c.drawString(margin, y_position, "Tampering Analysis:")
    y_position -= line_height
    for line in formatted_tampering.splitlines():
        c.drawString(margin, y_position, line)
        y_position -= line_height
        if y_position < 40:
            c.showPage()
            y_position = height - 40

    c.save()
    print(f"PDF saved as {output_pdf}")

def process_file(file_path):
    file_data = {
        "file_path": file_path,
        "hash": calculate_hash(file_path),
        "low_level_metadata": extract_low_level_metadata(file_path)
    }
    tampering_analysis = {}
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        file_data["type"] = "image"
        file_data["metadata"] = extract_image_metadata(file_path)
        tampering_analysis = detect_image_tampering(file_path)
    save_metadata_to_pdf(file_data, tampering_analysis, output_pdf="output_metadata.pdf")

def main():
    from google.colab import files
    print("Please upload the file to analyze:")
    uploaded = files.upload()
    for file_name in uploaded.keys():
        process_file(file_name)

if __name__ == "__main__":
    main()
