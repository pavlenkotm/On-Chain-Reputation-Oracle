"""Shared Pydantic models."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ScoreResponse(BaseModel):
    """API response for a reputation score request."""

    address: str = Field(..., description="Wallet address")
    score: int = Field(..., ge=0, le=1000, description="Reputation score")
    details: dict[str, float | int] | None = Field(
        default=None, description="Optional metric breakdown"
    )
