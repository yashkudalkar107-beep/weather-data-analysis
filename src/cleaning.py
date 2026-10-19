"""Tasks 2 & 3 - Clean the data, handle missing values and incorrect records."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config

NUMERIC_COLS = list(config.VALID_RANGES)


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return (clean_df, audit) where ``audit`` documents every fix that was made."""
    df = raw.copy()
    audit: dict = {"rows_raw": int(len(df))}

    # 1. Types ---------------------------------------------------------------
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    audit["unparseable_dates_dropped"] = int(df["date"].isna().sum())
    df = df.dropna(subset=["date"])

    # 2. Duplicate dates: keep the LAST record (the later file holds the complete
    #    daily record; the earlier one is a partial-day placeholder).
    dup_mask = df.duplicated(subset="date", keep="last")
    audit["duplicate_dates_removed"] = int(dup_mask.sum())
    audit["duplicate_dates"] = [d.strftime("%Y-%m-%d") for d in df.loc[dup_mask, "date"]]
    df = df.loc[~dup_mask].sort_values("date").set_index("date")

    # 3. Pre-existing missing values ----------------------------------------
    audit["missing_before"] = {c: int(df[c].isna().sum()) for c in NUMERIC_COLS}

    # 4. Incorrect records: values outside physically plausible ranges -> NaN
    invalid_log = []
    for col, (lo, hi) in config.VALID_RANGES.items():
        bad = df[col].notna() & ~df[col].between(lo, hi)
        for d, v in df.loc[bad, col].items():
            invalid_log.append({"date": d.strftime("%Y-%m-%d"), "column": col, "value": round(float(v), 2)})
        df.loc[bad, col] = np.nan
    audit["invalid_values"] = invalid_log
    audit["invalid_count"] = len(invalid_log)

    # 5. Fill gaps in the daily calendar so the series is continuous
    full_index = pd.date_range(df.index.min(), df.index.max(), freq="D")
    audit["missing_dates_added"] = int(len(full_index.difference(df.index)))
    df = df.reindex(full_index)
    df.index.name = "date"

    # 6. Impute remaining gaps: time interpolation (weather is smooth day to day)
    audit["missing_after_flagging"] = {c: int(df[c].isna().sum()) for c in NUMERIC_COLS}
    df[NUMERIC_COLS] = df[NUMERIC_COLS].interpolate(method="time", limit_direction="both")
    audit["missing_after_imputation"] = {c: int(df[c].isna().sum()) for c in NUMERIC_COLS}

    # 7. Feature engineering --------------------------------------------------
    df["year"] = df.index.year
    df["month"] = df.index.month
    df["month_name"] = df["month"].map(lambda m: config.MONTH_LABELS[m - 1])
    df["season"] = pd.Categorical(df["month"].map(config.SEASON_MAP),
                                  categories=config.SEASON_ORDER, ordered=True)
    df["warm_humid_day"] = ((df["humidity"] >= config.HUMID_THRESHOLD) &
                            (df["meantemp"] >= config.WARM_THRESHOLD)).astype(int)
    df = df.drop(columns=["source_file"], errors="ignore")

    audit["rows_clean"] = int(len(df))
    audit["date_min"] = df.index.min().strftime("%Y-%m-%d")
    audit["date_max"] = df.index.max().strftime("%Y-%m-%d")
    return df.reset_index(), audit
