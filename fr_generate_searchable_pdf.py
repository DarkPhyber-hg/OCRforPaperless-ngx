# Script to create searchable PDF from scan PDF or images using Azure Form Recognizer
# Required packages
# pip install --upgrade azure-ai-formrecognizer>=3.3 pypdf>=3.0 reportlab pillow pdf2image
import sys
import io
import math
import argparse
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas
from reportlab.lib import pagesizes
from reportlab import rl_config
from PIL import Image, ImageSequence
from pypdf import PdfWriter, PdfReader
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

# Please provide your Azure Form Recognizer endpoint and key
endpoint = YOUR_FORM_RECOGNIZER_ENDPOINT
key = YOUR_FORM_RECOGNIZER_KEY

def dist(p1, p2):
    return math.sqrt((p1.x - p2.x)*(p1.x - p2.x) + (p1.y - p2.y) * (p1.y - p2.y))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help="Input PDF or image (jpg, jpeg, tif, tiff, bmp, png) file name")
    parser.add_argument('-o', '--output', type=str, required=False, default="", help="Output PDF file name. Default: input_file + .ocr.pdf")
    args = parser.parse_args()

    input_file = args.input_file
    if args.output:
        output_file = args.output
    else:
        output_file = input_file + ".ocr.pdf"

    # Loading input file
    print(f"Loading input file {input_file}")
    if input_file.lower().endswith('.pdf'):
        # read existing PDF as images
        image_pages = convert_from_path(input_file)
    elif input_file.lower().endswith(('.tif', '.tiff', '.jpg', '.jpeg', '.png', '.bmp')):
        # read input image (potential multi page Tiff)
        image_pages = ImageSequence.Iterator(Image.open(input_file))
    else:
        sys.exit(f"Error: Unsupported input file extension {input_file}. Supported extensions: PDF, TIF, TIFF, JPG, JPEG, PNG, BMP.")

    # Running OCR using Azure Form Recognizer Read API 
    print(f"Starting Azure Form Recognizer OCR process...")
    document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key), headers={"x-ms-useragent": "searchable-pdf-blog/1.0.0"})

    with open(input_file, "rb") as f:
        poller = document_analysis_client.begin_analyze_document("prebuilt-read", document = f)

    ocr_results = poller.result()
    print(f"Azure Form Recognizer finished OCR text for {len(ocr_results.pages)} pages.")

    # Generate OCR overlay layer
    print(f"Generating searchable PDF...")
    output = PdfWriter()
    default_font = "Times-Roman"
    for page_id, page in enumerate(ocr_results.pages):
        ocr_overlay = io.BytesIO()

        # Calculate overlay PDF page size
        if image_pages[page_id].height > image_pages[page_id].width:
            page_scale = float(image_pages[page_id].height) / pagesizes.letter[1]
        else:
            page_scale = float(image_pages[page_id].width) / pagesizes.letter[1]

        page_width = float(image_pages[page_id].width) / page_scale
        page_height = float(image_pages[page_id].height) / page_scale

        scale = (page_width / page.width + page_height / page.height) / 2.0
        pdf_canvas = canvas.Canvas(ocr_overlay, pagesize=(page_width, page_height))

        # Add image into PDF page
        pdf_canvas.drawInlineImage(image_pages[page_id], 0, 0, width=page_width, height=page_height, preserveAspectRatio=True)

        text = pdf_canvas.beginText()
        # Set text rendering mode to invisible
        text.setTextRenderMode(3)
        for word in page.words:
            # Calculate optimal font size
            desired_text_width = max(dist(word.polygon[0], word.polygon[1]), dist(word.polygon[3], word.polygon[2])) * scale
            desired_text_height = max(dist(word.polygon[1], word.polygon[2]), dist(word.polygon[0], word.polygon[3])) * scale
            font_size = desired_text_height
            actual_text_width = pdf_canvas.stringWidth(word.content, default_font, font_size)
            
            # Calculate text rotation angle
            text_angle = math.atan2((word.polygon[1].y - word.polygon[0].y + word.polygon[2].y - word.polygon[3].y) / 2.0, 
                                    (word.polygon[1].x - word.polygon[0].x + word.polygon[2].x - word.polygon[3].x) / 2.0)
            text.setFont(default_font, font_size)
            text.setTextTransform(math.cos(text_angle), -math.sin(text_angle), math.sin(text_angle), math.cos(text_angle), word.polygon[3].x * scale, page_height - word.polygon[3].y * scale)
            text.setHorizScale(desired_text_width / actual_text_width * 100)
            text.textOut(word.content + " ")

        pdf_canvas.drawText(text)
        pdf_canvas.save()

        # Move to the beginning of the buffer
        ocr_overlay.seek(0)

        # Create a new PDF page
        new_pdf_page = PdfReader(ocr_overlay)
        output.add_page(new_pdf_page.pages[0])

    # Save output searchable PDF file
    with open(output_file, "wb") as outputStream:
        output.write(outputStream)

    print(f"Searchable PDF is created: {output_file}")
