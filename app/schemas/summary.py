from pydantic import BaseModel
from typing import List

class SummaryRequest(BaseModel):
    text: str
    type: str = "extractive"

class Analysis(BaseModel):
    originalWords: int
    summaryWords: int
    originalChars: int
    summaryChars: int
    readingTime: int
    summaryReadingTime: int

class SummaryResponse(BaseModel):
    topics: List[str]
    summary: str
    conclusion: str
    analysis: Analysis
