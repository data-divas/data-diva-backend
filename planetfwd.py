from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
import httpx, json
from dotenv import load_dotenv
import os
import requests

router = APIRouter()

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
audience = os.getenv("AUDIENCE")
grant_type = os.getenv("GRANT_TYPE")

@router.get("/get-token/")
async def get_token():
    url = "https://planetfwd.us.auth0.com/oauth/token"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "audience": audience,
        "grant_type": grant_type
    }

    try:
        # Make the POST request
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
        
        # Check for errors
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error from Auth0: {response.text}"
            )

        # Return the token
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
class FootprintRequest(BaseModel):
    name: str
    amount: float
    unit: str

@router.post("/footprint-info/")
async def get_info(request_data: FootprintRequest):
    token_response = await get_token()
    token = token_response["access_token"]
    url = "https://app.planetfwd.com/api/lca/generate"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",  
        "Content-Type": "application/json",
    }

    # Prepare the payload for the external API
    payload = {
        "name": request_data.name,
        "mass": {
            "amount": request_data.amount,
            "unit": request_data.unit
        }
    }

    try:
        # Forward the request to the external API
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)

        # Handle non-200 responses from the external API
        if response.status_code != 200 and response.status_code != 201:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error from PlanetFWD API: {response.text}",
            )

        # Return the response from the external API
        id_response = response.json()
        id = id_response["id"]

        get_url = https://app.planetfwd.com/api/lca/{id}/generation_status 
        ## continue later w get request
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))