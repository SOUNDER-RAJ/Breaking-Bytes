
﻿Project Title: Breaking Bytes

Disclaimer:
This script is for **educational** and **ethical purposes only**. Unauthorized tampering with files or data without consent is **illegal**.

By using this script, you agree to follow all applicable laws and use it solely for legal and educational purposes. The author is not responsible for any misuse of this tool.


________________


Overview

Breaking Bytes is a forensic analysis tool designed to extract, analyze, and document metadata and potential tampering in digital images. The tool utilizes various libraries and techniques to provide a structured forensic report.

Core Functionalities

1. File Hashing

Computes SHA-256 hash values to ensure file integrity.

Helps in detecting unauthorized modifications.

2. Metadata Extraction

High-Level Metadata (ExifTool)

Extracts metadata such as timestamps, camera model, and GPS coordinates.

Uses ExifTool for detailed image metadata retrieval.

Low-Level Metadata (Hachoir)

Parses deep metadata from image files.

Retrieves structural and format-related information.

3. Image Tampering Detection

Utilizes Structural Similarity Index (SSIM) to analyze anomalies.

Splits images into quadrants and compares regions for inconsistencies.

Identifies significant changes that might indicate tampering.

4. PDF Report Generation

Aggregates extracted metadata and tampering analysis.

Formats findings into a structured and human-readable PDF report.

Ensures easy accessibility and forensic documentation.

Output

The final report is saved as a PDF file containing extracted metadata, hash values, and tampering detection results.

Useful for forensic investigations, digital evidence collection, and cybersecurity analysis.

Conclusion

Breaking Bytes provides an efficient approach to digital forensic analysis of images. It enables the detection of modifications while maintaining structured documentation for further analysis.

End...
