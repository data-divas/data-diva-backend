from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import cv2
import numpy as np
import base64
from PIL import Image
import torch

app = FastAPI()

# Configure CORS: enable requests coming from a separate frontend (in this case, we run it locally)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class testResponse(BaseModel):
    message: str

# Test endpoint 
@app.get("/test", response_model=testResponse)
async def testEndPoint():
    try:
        return testResponse(message="Hallo we exist :)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

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


