"""Task 1 - Collect / load the dataset.

Dataset: "Daily Climate time series data" (Delhi, India, 2013-01-01 to 2017-04-24)
Kaggle: https://www.kaggle.com/datasets/sumanthvrao/daily-climate-time-series-data
The two raw files (train + test split published on Kaggle) are kept untouched in
``data/raw`` and are concatenated here into one continuous time series.
"""
from __future__ import annotations

import urllib.request

import pandas as pd

from . import config

# Public GitHub mirror of the Kaggle files (used only if data/raw is empty).
MIRROR = "https://raw.githubusercontent.com/amrutha007/Daily-Delhi-Climate/main/"


def download_if_missing() -> None:
    """Download the raw CSVs from the mirror when they are not present locally."""
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    for name in config.RAW_FILES:
        target = config.RAW_DIR / name
        if not target.exists():
            print(f"Downloading {name} ...")
            urllib.request.urlretrieve(MIRROR + name, target)


def load_raw() -> pd.DataFrame:
    """Load and concatenate the raw files exactly as published (no cleaning)."""
    download_if_missing()
    frames = []
    for name in config.RAW_FILES:
        part = pd.read_csv(config.RAW_DIR / name)
        part["source_file"] = name
        frames.append(part)
    df = pd.concat(frames, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df
