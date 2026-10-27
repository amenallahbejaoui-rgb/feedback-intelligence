# tests/test_clean.py
from feedback.ingest.clean import detect_script, mask_pii


def test_mask_phone_and_email():
    out = mask_pii("appelez 22 333 444 ou a@b.com")
    assert "<PHONE>" in out and "<EMAIL>" in out


def test_script_detection():
    assert detect_script("التطبيق ما يخدمش") == "arabic_script"
    assert detect_script("l'application mouch behi 3andi mochkla") == "latin_arabizi_candidate"
    assert detect_script("great app") == "latin"