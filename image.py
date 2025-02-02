import cv2
import pytesseract
import numpy as np
from PIL import Image
import io

def detect_product_from_image(image_file):
    """
    Takes an image file as input (not a file path), processes the image, 
    and uses Tesseract OCR to extract the product name from the image.
    
    :param image_file: Image file object (e.g., from Flask or FastAPI).
    :return: Product name (if detected) and full extracted text.
    """
    # Load the image from the file object using PIL
    image = Image.open(image_file)
    
    # Convert the PIL image to a format that OpenCV can work with (numpy array)
    opencv_image = np.array(image)

    # Convert RGB to BGR (OpenCV uses BGR format by default)
    opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2BGR)
    
    # Preprocess the image to improve OCR results
    preprocessed_image = preprocess_image(opencv_image)
    
    # Use Tesseract to perform OCR and extract text from the image
    extracted_text = pytesseract.image_to_string(preprocessed_image)
    
    # Extract the product name from the OCR output
    product_name = extract_product_name(extracted_text)
    
    return product_name, extracted_text


def preprocess_image(image):
    """
    Preprocesses the image to improve OCR accuracy:
    - Convert to grayscale
    - Apply thresholding to make the text stand out more clearly
    - Optionally, apply noise reduction or other filters
    """
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to make the text stand out more clearly
    _, thresholded_image = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)
    
    # Optional: Apply median blur to reduce noise (helps improve text recognition)
    # thresholded_image = cv2.medianBlur(thresholded_image, 3)
    
    return thresholded_image


def extract_product_name(text):
    """
    Extract the product name from the OCR result.
    This function may need to be customized depending on the format of your product names.
    
    :param text: Full text extracted by OCR
    :return: The detected product name (first relevant text line)
    """
    # Split the extracted text into lines and process them
    lines = text.split('\n')
    
    # Simple extraction: return the first non-empty line as the product name
    for line in lines:
        if line.strip():  # Skip empty lines
            return line.strip()  # Return the first non-empty line as product name
    
    return "Product not found"


# # Example usage (assuming `image_file` is a file object):
# # If you're using Flask or FastAPI, the `image_file` might come from an uploaded file.

# # Example with file reading (for testing purposes):
# with open('path_to_image.jpg', 'rb') as f:
#     image_file = io.BytesIO(f.read())

# product_name, extracted_text = detect_product_from_image(image_file)

# print(f"Detected Product: {product_name}")
# print(f"Extracted Text:\n{extracted_text}")
