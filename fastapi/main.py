from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

from prediction_service import PredictionService
from config import settings

app = FastAPI(
    title="Text Summarization API",
    description="API for generating text summaries using transformer models",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prediction_service = PredictionService()


class TextInput(BaseModel):
    model_config = {"protected_namespaces": ()}

    text: str = Field(..., description="Text to summarize")
    model_name: Optional[str] = Field(
        default=settings.DEFAULT_MODEL,
        description="Model name to use for summarization"
    )
    max_source_tokens: Optional[int] = Field(
        default=600,
        description="Maximum number of source tokens"
    )


class SummaryResponse(BaseModel):
    model_config = {"protected_namespaces": ()}

    summary: str
    model_used: str


@app.get("/")
async def root():
    return {
        "message": "Text Summarization API",
        "version": "1.0.0",
        "endpoints": {
            "summarize": "/api/v1/summarize",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/v1/summarize", response_model=SummaryResponse)
async def summarize_text(input_data: TextInput):
    try:
        model_name = input_data.model_name or settings.DEFAULT_MODEL
        max_tokens = input_data.max_source_tokens or settings.MAX_SOURCE_TOKENS

        summary = await prediction_service.predict_single(
            text=input_data.text,
            model_name=model_name,
            max_source_tokens=max_tokens
        )

        return SummaryResponse(
            summary=summary,
            model_used=model_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
