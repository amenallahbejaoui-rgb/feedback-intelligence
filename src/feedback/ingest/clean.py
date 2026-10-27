import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]

ARABIC = re.compile(r"[\u0600-\u06FF]")
LATIN = re.compile(r"[A-Za-z]")
ARABIZI_DIGITS = re.compile(r"[A-Za-z]*[2356789][A-Za-z]+|[A-Za-z]+[2356789][A-Za-z]*")
PHONE = re.compile(r"(?<!\d)(?:\+?216[\s.-]?)?\d{2}[\s.-]?\d{3}[\s.-]?\d{3}(?!\d)")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


def mask_pii(text: str) -> str:
    return PHONE.sub("<PHONE>", EMAIL.sub("<EMAIL>", text))


def detect_script(text: str) -> str:
    """Rough heuristic. Good enough to stratify; the gold labels are the truth."""
    ar = len(ARABIC.findall(text))
    la = len(LATIN.findall(text))
    if ar + la == 0:
        return "other"
    if ar and la and min(ar, la) / (ar + la) > 0.15:
        return "mixed_script"
    if ar >= la:
        return "arabic_script"
    return "latin_arabizi_candidate" if ARABIZI_DIGITS.search(text) else "latin"


def clean(path: Path) -> Path:
    df = pd.read_json(path, lines=True)
    n0 = len(df)
    df["text"] = df["text"].fillna("").astype(str).str.strip()
    df = df[df["text"].str.len() >= 3]
    df["text_norm"] = df["text"].str.lower().str.replace(r"\s+", " ", regex=True)
    df = df.drop_duplicates(subset=["app", "text_norm"]).drop_duplicates("review_id")
    df["text"] = df["text"].map(mask_pii)
    df["script"] = df["text"].map(detect_script)
    df["n_chars"] = df["text"].str.len()
    df = df.drop(columns=["text_norm"])
    out = ROOT / "data" / "interim" / "reviews_clean.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_json(out, orient="records", lines=True, force_ascii=False)
    print(f"{n0} -> {len(df)} reviews after cleaning")
    print(df["script"].value_counts())
    return out


if __name__ == "__main__":
    latest = sorted((ROOT / "data" / "raw").glob("reviews_*.jsonl"))[-1]
    clean(latest)