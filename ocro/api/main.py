"""FastAPI application exposing reputation scores."""
from __future__ import annotations

import logging
import re
from fastapi import FastAPI, HTTPException

from ..models import ScoreResponse
from ..scoring import ScoringEngine

logger = logging.getLogger(__name__)
ADDRESS_REGEX = re.compile(r"^0x[a-fA-F0-9]{40}$")

app = FastAPI(title="On-Chain Reputation Oracle", version="0.1.0")
engine = ScoringEngine()


@app.get("/health")
def health() -> dict[str, str]:
    """Return health information."""

    return {"status": "ok"}


@app.get("/score/{address}", response_model=ScoreResponse)
def get_score(address: str) -> ScoreResponse:
    """Return the reputation score for an address."""

    if not ADDRESS_REGEX.match(address):
        logger.debug("Invalid address requested: %s", address)
        raise HTTPException(status_code=400, detail="Invalid Ethereum address")

    details = engine.calculate(address)
    return ScoreResponse(address=address, score=details.score, details=details.to_dict())
