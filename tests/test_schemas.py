# tests/test_schemas.py
import pytest
from pydantic import ValidationError

from feedback.schemas import ReviewLabel


def make(**kw):
    base = dict(
        review_id="r1", text="L'application crash au login", language="fr",
        overall_sentiment="negative", annotator_id="a1",
        aspects=[{"aspect": "app_stability", "sentiment": "negative", "evidence": "crash"}],
    )
    base.update(kw)
    return ReviewLabel(**base)


def test_valid_label():
    assert make().aspects[0].aspect == "app_stability"


def test_unknown_aspect_rejected():
    with pytest.raises(ValidationError):
        make(aspects=[{"aspect": "foo", "sentiment": "negative", "evidence": "crash"}])


def test_evidence_must_be_in_text():
    with pytest.raises(ValidationError):
        make(aspects=[{"aspect": "ui_ux", "sentiment": "negative", "evidence": "not there"}])