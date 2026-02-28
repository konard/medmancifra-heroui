"""
Viral Demand Model — FastAPI Service
======================================
Run with:
    uvicorn fastapi_service:app --reload --port 8000

API Endpoints:
    POST /predict          → Predict virality score for an idea
    GET  /health           → Health check
    GET  /criteria         → Return the 10 virality criteria
"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Viral Demand Model API",
    description="Predict future virality of ideas across time horizons (0.1 – ∞ years)",
    version="0.1.0",
)

class IdeaRequest(BaseModel):
    title: str
    domain: str
    description: str
    author_profession: Optional[str] = "unknown"
    author_city: Optional[str] = "unknown"
    virality_horizon_years: Optional[float] = 10.0
    # Optional raw metrics (if available from parser)
    citation_count: Optional[int] = 0
    patent_count: Optional[int] = 0
    publication_year: Optional[int] = 2025

class VirtualityResponse(BaseModel):
    virality_composite_score: float
    virality_label: str          # "viral" | "promising" | "niche" | "declining"
    k_factor_estimate: float
    temporal_decay_factor: float
    shock_amplification_factor: float
    virality_horizon_years: float
    criteria_scores: dict        # Q1–Q10
    idea_chain: list[str]        # Causal chain of virality factors
    confidence: float

@app.post("/predict", response_model=VirtualityResponse)
async def predict_virality(request: IdeaRequest):
    """
    Predict virality score for an idea.
    In production: loads the trained model and runs inference.
    For MVP: returns a mock response.
    """
    # TODO: load actual trained model here
    mock_score = 0.72
    return VirtualityResponse(
        virality_composite_score=mock_score,
        virality_label="promising" if mock_score > 0.5 else "niche",
        k_factor_estimate=1.3,
        temporal_decay_factor=0.85,
        shock_amplification_factor=0.6,
        virality_horizon_years=request.virality_horizon_years,
        criteria_scores={
            "q1_universal_pain": 0.8, "q2_emotion_trigger": 0.7,
            "q3_low_friction": 0.6, "q4_network_effect": 0.75,
            "q5_scalable_economics": 0.65, "q6_cultural_resonance": 0.7,
            "q7_structural_readiness": 0.8, "q8_capital_alignment": 0.7,
            "q9_timing_window": 0.75, "q10_author_credibility": 0.8,
        },
        idea_chain=[
            "Universal Pain Point → High Global Demand",
            "High Emotional Trigger → Social Sharing Intent",
            "Low Friction → Fast Viral Cycle Time",
            "Network Effects → Exponential K-Factor",
            "Capital Alignment → Structural Readiness",
            "SAF = 0.6 → Horizon compressed to ~8 years",
        ],
        confidence=0.78,
    )

@app.get("/health")
async def health():
    return {"status": "ok", "model_version": "0.1.0"}

@app.get("/criteria")
async def get_criteria():
    return {
        "criteria": [
            {"id": "Q1", "name": "Universal Pain", "description": "Solves a globally felt problem"},
            {"id": "Q2", "name": "Emotion Trigger", "description": "Evokes awe, fear, or belonging"},
            {"id": "Q3", "name": "Low Friction", "description": "First value felt in under 60 seconds"},
            {"id": "Q4", "name": "Network Effect", "description": "Value grows with each new user"},
            {"id": "Q5", "name": "Scalable Economics", "description": "Near-zero marginal cost growth"},
            {"id": "Q6", "name": "Cultural Resonance", "description": "Aligns with emerging cultural megatrend"},
            {"id": "Q7", "name": "Structural Readiness", "description": "Infrastructure available now"},
            {"id": "Q8", "name": "Capital Alignment", "description": "VCs and governments fund this category"},
            {"id": "Q9", "name": "Timing Window", "description": "Regulatory or tech unlock in horizon"},
            {"id": "Q10", "name": "Author Credibility", "description": "Originator is a recognized expert"},
        ]
    }
