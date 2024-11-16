from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import pytesseract
from PIL import Image
import io
import numpy as np
import cv2
import easyocr

# Initialize FastAPI app
app = FastAPI()

reader = easyocr.Reader(['en'], gpu=False)

@app.post("/detect-object/")
async def extract_text(file: UploadFile = File(...)):
    try:
        # Ensure the file is an image (check MIME type)
        if not file.content_type.startswith("image/"):
            raise ValueError("Uploaded file is not an image.")
        
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)

        result = reader.readtext(image_np)

        extracted_text = []
        extracted_text = []
        for item in result:
            text = item[1]  # Extracted text
            confidence = item[2]  # Confidence score
            bbox = item[0]  # Bounding box coordinates

            # Convert numpy.int64 to standard Python int for JSON serialization
            bbox = [[int(x), int(y)] for [x, y] in bbox]

            extracted_text.append({
                "text": text,
                "confidence": confidence,
                "bounding_box": bbox
            })

        # Return the extracted text as JSON
        return JSONResponse({"extracted_text": extracted_text})

    except Exception as e:
        # Return error message if the image couldn't be processed
        return JSONResponse({"error": str(e)}, status_code=400)