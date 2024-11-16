from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64

app = FastAPI()

# Configure CORS: enable requests coming from a separate frontend (in this case, we run it locally)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
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