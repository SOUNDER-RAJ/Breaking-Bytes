import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Function to pretty-print JSON in the terminal
def print_json_pretty(json_data):
    """Print JSON data in a readable format in the terminal."""
    print(json.dumps(json_data, indent=4))

# Function to save JSON content as a PDF
def save_json_as_pdf(json_data, pdf_filename="json_output.pdf"):
    """Convert JSON content into a PDF document."""
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    # Starting y-position for content
    y_position = height - 40
    margin = 40
    line_height = 12

    # Formatting the JSON data into a readable format
    formatted_json = json.dumps(json_data, indent=4)
    lines = formatted_json.splitlines()

    # Adding the lines to the PDF, ensuring they don't exceed the page height
    for line in lines:
        c.drawString(margin, y_position, line)
        y_position -= line_height

        # If the line reaches the bottom of the page, start a new page
        if y_position < 40:
            c.showPage()
            y_position = height - 40
    
    c.save()
    print(f"PDF saved as {pdf_filename}")

# Main function to handle input, display, and save as PDF
def main():
    # Load JSON data from a file
    input_file = input("Enter the path of the JSON file: ")
    try:
        with open(input_file, "r") as file:
            json_data = json.load(file)

        # Display JSON in a readable format in the terminal
        print_json_pretty(json_data)

        # Optionally save the JSON data to a PDF
        save_pdf = input("Would you like to save this JSON as a PDF? (y/n): ")
        if save_pdf.lower() == 'y':
            output_pdf = input("Enter output PDF filename (default is json_output.pdf): ")
            if not output_pdf:
                output_pdf = "json_output.pdf"
            save_json_as_pdf(json_data, pdf_filename=output_pdf)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
