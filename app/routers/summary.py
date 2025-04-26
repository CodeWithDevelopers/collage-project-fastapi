from fastapi import APIRouter, HTTPException
from app.schemas.summary import SummaryRequest, SummaryResponse
from app.services.summarizer import generate_extractive_summary, generate_abstractive_summary

router = APIRouter()

@router.post("/", response_model=SummaryResponse)
async def summarize_text(payload: SummaryRequest):
    try:
        if len(payload.text) < 100:
            raise HTTPException(status_code=400, detail="Text is too short. Please provide at least 100 characters.")
        
        if payload.type == "abstractive":
            return await generate_abstractive_summary(payload.text)
        else:
            return await generate_extractive_summary(payload.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
