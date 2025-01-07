from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import json
import os
import hashlib
import subprocess
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

def calculate_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

def extract_image_metadata(file_path):
    metadata = {}
    try:
        result = subprocess.run(["exiftool", file_path], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            key, _, value = line.partition(": ")
            metadata[key.strip()] = value.strip()
    except Exception as e:
        print(f"Error extracting image metadata: {e}")
    return metadata

def detect_image_tampering(file_path):
    tampering_data = {"tampering_suspected": False}
    try:
        image = cv2.imread(file_path)
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        h, w = gray_image.shape
        split_images = [
            gray_image[0:h//2, 0:w//2],
            gray_image[0:h//2, w//2:],
            gray_image[h//2:, 0:w//2],
            gray_image[h//2:, w//2:]
        ]
        ssim_scores = [ssim(split_images[i], split_images[j]) for i in range(4) for j in range(i + 1, 4)]
        if any(score < 0.5 for score in ssim_scores):
            tampering_data["tampering_suspected"] = True
        tampering_data["ssim_scores"] = ssim_scores
    except Exception as e:
        print(f"Error during tampering detection: {e}")
    return tampering_data

def save_report(file_data, tampering_analysis, output_pdf="image_report.pdf"):
    doc = SimpleDocTemplate(output_pdf, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("Image Metadata Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 12))
    
    metadata_table = [["Attribute", "Value"]] + [[k, v] for k, v in file_data["metadata"].items()]
    table = Table(metadata_table, colWidths=[200, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    
    elements.append(Paragraph("Tampering Analysis", styles["Heading2"]))
    tampering_text = "Tampering Suspected: Yes" if tampering_analysis["tampering_suspected"] else "Tampering Suspected: No"
    elements.append(Paragraph(tampering_text, styles["Normal"]))
    elements.append(Spacer(1, 12))
    
    doc.build(elements)
    print(f"Report saved as {output_pdf}")

def process_file(file_path):
    file_data = {
        "file_path": file_path,
        "hash": calculate_hash(file_path),
        "metadata": extract_image_metadata(file_path)
    }
    tampering_analysis = detect_image_tampering(file_path) if file_path.lower().endswith(('png', 'jpg', 'jpeg')) else {}
    save_report(file_data, tampering_analysis)

def main():
    file_path = input("Enter the image file path: ")
    if os.path.exists(file_path):
        process_file(file_path)
    else:
        print("File not found!")

if __name__ == "__main__":
    main()
