# backend/routes/vapi_config.py
from fastapi import APIRouter, HTTPException
import os
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

router = APIRouter()

VAPI_PUBLIC_KEY = os.getenv("VAPI_PUBLIC_KEY")
VAPI_ASSISTANT_ID = os.getenv("VAPI_ASSISTANT_ID")

class VapiConfigResponse(BaseModel):
    publicKey: str
    assistantId: str

@router.get("/api/vapi-config", response_model=VapiConfigResponse)
async def get_vapi_config():
    if not VAPI_PUBLIC_KEY or not VAPI_ASSISTANT_ID:
        raise HTTPException(status_code=500, detail="Missing Vapi credentials.")
    return VapiConfigResponse(publicKey=VAPI_PUBLIC_KEY, assistantId=VAPI_ASSISTANT_ID)
