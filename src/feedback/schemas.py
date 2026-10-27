from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator

_CFG = yaml.safe_load(
    (Path(__file__).resolve().parents[2] / "configs" / "aspects.yaml").read_text(encoding="utf-8")
)
ASPECTS: set[str] = set(_CFG["aspects"])
LANGUAGES: set[str] = set(_CFG["languages"])
SENTIMENTS: set[str] = set(_CFG["sentiments"])


class AspectLabel(BaseModel):
    aspect: str
    sentiment: Literal["positive", "negative", "neutral"]
    evidence: str = Field(min_length=1, description="Exact substring of the review")

    @field_validator("aspect")
    @classmethod
    def aspect_known(cls, v: str) -> str:
        if v not in ASPECTS:
            raise ValueError(f"unknown aspect '{v}', allowed: {sorted(ASPECTS)}")
        return v


class ReviewLabel(BaseModel):
    review_id: str
    text: str
    language: str
    overall_sentiment: str
    aspects: list[AspectLabel] = []
    sarcasm: bool = False
    is_spam_or_irrelevant: bool = False
    annotator_id: str
    notes: str | None = None

    @field_validator("language")
    @classmethod
    def language_known(cls, v: str) -> str:
        if v not in LANGUAGES:
            raise ValueError(f"unknown language '{v}'")
        return v

    @field_validator("overall_sentiment")
    @classmethod
    def sentiment_known(cls, v: str) -> str:
        if v not in SENTIMENTS:
            raise ValueError(f"unknown sentiment '{v}'")
        return v

    @model_validator(mode="after")
    def evidence_in_text(self):
        for a in self.aspects:
            if a.evidence not in self.text:
                raise ValueError(f"evidence not found verbatim in text: {a.evidence!r}")
        return self