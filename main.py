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
from ultralytics import YOLO

# Initialize FastAPI app
app = FastAPI()

reader = easyocr.Reader(['en'], gpu=False)
# Configure CORS: enable requests coming from a separate frontend (in this case, we run it locally)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    

class ImageData(BaseModel):
    image: str

# Load the YOLO model (e.g., YOLOv5)
# model = torch.hub.load("ultralytics/yolov5", "yolov5s")

model = YOLO("trained_yolo_model.pt")

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
        results = model.predict("dasani.jpg", )
        names = model.names

        for result in results:
            for c in result.boxes.cls:
                print(names[int(c)])
        
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


