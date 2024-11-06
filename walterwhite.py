import os
import hashlib
import json
import csv
import subprocess
from datetime import datetime
from PIL import Image
import PyPDF2
import fitz  # PyMuPDF
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from skimage.metrics import structural_similarity as ssim
import cv2
import numpy as np
import platform

# File hashing function
def calculate_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()

# Extract high-level metadata using ExifTool for images
def extract_image_metadata(file_path):
    metadata = {}
    try:
        # Suppress the warnings from exiftool by redirecting stderr and stdout
        result = subprocess.run(
            ["exiftool", file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,  # Redirect stderr to suppress warnings
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

# PDF metadata extraction
def extract_pdf_metadata(file_path):
    metadata = {}
    try:
        with fitz.open(file_path) as pdf:
            metadata.update(pdf.metadata)
    except Exception as e:
        print(f"Error extracting PDF metadata with PyMuPDF: {e}")

    try:
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfFileReader(f)
            metadata["num_pages"] = pdf_reader.numPages
            metadata.update(pdf_reader.getDocumentInfo())
    except Exception as e:
        print(f"Error extracting PDF metadata with PyPDF2: {e}")
    return metadata

# File creation and modification dates, owner, and license info (platform-specific)
def extract_filesystem_metadata(file_path):
    metadata = {}
    try:
        if platform.system() == 'Windows':
            metadata['creation_date'] = datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
        else:  # macOS and Linux
            stat = os.stat(file_path)
            metadata['creation_date'] = datetime.fromtimestamp(stat.st_birthtime).isoformat() if hasattr(stat, 'st_birthtime') else datetime.fromtimestamp(stat.st_mtime).isoformat()
        metadata['modification_date'] = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        metadata['owner'] = os.stat(file_path).st_uid if hasattr(os, 'st_uid') else "N/A"
    except Exception as e:
        print(f"Error extracting file system metadata: {e}")
    return metadata

# Detecting tampering in images using SSIM
def detect_image_tampering(file_path):
    tampering_data = {"tampering_suspected": False}
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
    return tampering_data

# Low-level metadata extraction using Hachoir
def extract_low_level_metadata(file_path):
    metadata = {}
    parser = createParser(file_path)
    if parser:
        metadata_obj = extractMetadata(parser)
        if metadata_obj:
            for line in metadata_obj.exportPlaintext():
                key, _, value = line.partition(": ")
                metadata[key.strip()] = value.strip()
    return metadata

# Process individual files and gather metadata
def process_file(file_path):
    file_data = {
        "file_path": file_path,
        "hash": calculate_hash(file_path),
        "filesystem_metadata": extract_filesystem_metadata(file_path),
        "low_level_metadata": extract_low_level_metadata(file_path)
    }
    if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
        file_data["type"] = "image"
        file_data["metadata"] = extract_image_metadata(file_path)
        file_data["tampering_analysis"] = detect_image_tampering(file_path)
    elif file_path.lower().endswith('.pdf'):
        file_data["type"] = "pdf"
        file_data["metadata"] = extract_pdf_metadata(file_path)
    return file_data

# Batch processing function for files
def batch_process_files(file_paths):
    from multiprocessing import Pool, cpu_count
    with Pool(cpu_count()) as pool:
        results = pool.map(process_file, file_paths)
    return results

# Save results to JSON and CSV
def save_results(results, output_json="forensic_results.json", output_csv="forensic_results.csv"):
    with open(output_json, "w") as json_file:
        json.dump(results, json_file, indent=4)
    keys = results[0].keys()
    with open(output_csv, "w", newline="") as csv_file:
        dict_writer = csv.DictWriter(csv_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(results)

# Main function to process a directory or single file
def main(directory):
    if os.path.isfile(directory):
        file_paths = [directory]
    elif os.path.isdir(directory):
        file_paths = [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    else:
        print("Invalid path.")
        return
    results = batch_process_files(file_paths)
    save_results(results)
    print("Results saved to forensic_results.json and forensic_results.csv")

if __name__ == "__main__":
    directory_path = input("Enter the file or directory path to process: ")
    main(directory_path)
