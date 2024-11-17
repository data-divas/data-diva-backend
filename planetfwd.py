from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
import httpx, json
from dotenv import load_dotenv
import os
import requests
import asyncio

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
        print(id)

        get_url = f"https://app.planetfwd.com/api/lca/{id}/generation_status" 

        get_headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {token}"
        }

        max_retries = 5  # Maximum number of retries
        retry_delay = 2  # Delay in seconds between retries

        for _ in range(max_retries):
            async with httpx.AsyncClient() as client:
                get_response = await client.get(get_url, headers=get_headers)

            if get_response.status_code != 200 and get_response.status_code != 201:
                raise HTTPException(
                    status_code=get_response.status_code,
                    detail=f"Error from PlanetFWD API for get request: {get_response.text}",
                )

            get_response = get_response.json()

            # Check if "complete" is true
            if get_response.get("complete", False):  # Use .get() to handle missing key gracefully
                res = {
                    "emissionFactor": get_response["emissionFactor"],
                    "emissionFactorUnit": get_response["emissionFactorUnit"]
                }
                return res

            # If "complete" is false, wait and retry
            await asyncio.sleep(retry_delay)

        # If the loop ends without finding "complete": true
        raise HTTPException(
            status_code=504,
            detail="The operation did not complete within the allowed retries."
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))