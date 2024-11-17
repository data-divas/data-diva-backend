import re
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
import io
import numpy as np
import cv2
import easyocr
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import numpy as np
import base64
from PIL import Image
import torch

# Initialize FastAPI app
app = FastAPI()

reader = easyocr.Reader(['en'], gpu=True)
# Configure CORS: enable requests coming from a separate frontend (in this case, we run it locally)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ocr/")
async def extract_text(file: UploadFile = File(...)):
    try:
        # Ensure the file is an image (check MIME type)
        if not file.content_type.startswith("image/"):
            raise ValueError("Uploaded file is not an image.")
        
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)

        result = reader.readtext(image_np)
        
        filtered_result = [
            item for item in result
            if item[2] > 0.4 and len(item[1].strip()) > 1 and is_valid_text(item[1])
        ]

        # Sort the results based on bounding box coordinates
        sorted_result = sorted(filtered_result, key=lambda x: (x[0][0][1], x[0][0][0]))
        
        extracted_text = []
        for item in sorted_result:
            text = clean_text(item[1])  # Extracted text
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
    
def is_valid_text(text):
    """
    Filter out meaningless or irrelevant text.
    """
    # Example: remove single-character texts or random numbers (like '1', 'A', 'O')
    return not re.match(r'^[0-9A-Za-z]{1,2}$', text)


def clean_text(text):
    """
    Post-process the text to fix common OCR mistakes and clean unwanted characters.
    """
    # Common post-processing fixes (e.g., fix '1' to 'I', '0' to 'O')
    replacements = {
        '1': 'I',
        '0': 'O',
        'l': 'I',  # Lowercase 'l' often misread as 'I'
        'O': '0',  # Sometimes 'O' is read as '0' in receipts
        # Add more replacements as needed
    }

    # Replace characters based on the dictionary
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Optionally, remove unwanted characters (e.g., punctuation)
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)

    return text.strip()  # Clean up leading/trailing spaces
    

class ImageData(BaseModel):
    image: str

# Load the YOLO model (e.g., YOLOv5)
model = torch.hub.load("ultralytics/yolov5", "yolov5s")

@app.post("/detect-product")
async def detect_objects(data: ImageData):
    try:
        # Decode the base64 image
        image_data = data.image.split(",")[1]
        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Use PIL to open the image for YOLO
        pil_img = Image.fromarray(img_rgb)

        # Perform object detection with YOLO
        results = model(pil_img)

       
        boxes = []
        labels = []
        confidences = []
        
        for *xyxy, conf, cls_idx in results.xyxy[0]:  
            x1, y1, x2, y2 = map(int, xyxy)  
            boxes.append({
                "x": x1,
                "y": y1,
                "w": x2 - x1,
                "h": y2 - y1
            })
            
            label = results.names[int(cls_idx)]
            labels.append(label)
            confidences.append(float(conf))

        
        return {
            "success": True,
            "boxes": boxes,
            "labels": labels,
            "confidences": confidences
        }

    except Exception as e:
        print(f"Error details: {str(e)}") 
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")
    

# # Endpoint to parse product data from the detected text
@app.post("/parse-product-data")
async def parse_product_data(data: str):
    return {
        "success": True,
        "product_data": data
    }
    


