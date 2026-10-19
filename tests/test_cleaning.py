import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.cleaning import clean  # noqa: E402


def _raw(rows):
    df = pd.DataFrame(rows, columns=["date", "meantemp", "humidity", "wind_speed", "meanpressure"])
    df["date"] = pd.to_datetime(df["date"])
    df["source_file"] = "t.csv"
    return df


def test_outlier_pressure_is_replaced_and_no_nans_remain():
    raw = _raw([("2020-01-01", 10, 80, 3, 1010), ("2020-01-02", 11, 70, 3, 7679),
                ("2020-01-03", 12, 60, 3, 1014)])
    out, audit = clean(raw)
    assert audit["invalid_count"] == 1
    assert out["meanpressure"].isna().sum() == 0
    assert out.loc[1, "meanpressure"] == 1012  # linear interpolation


def test_duplicate_dates_keep_last_and_gaps_are_filled():
    raw = _raw([("2020-01-01", 1, 50, 1, 1000), ("2020-01-01", 2, 50, 1, 1000),
                ("2020-01-04", 5, 50, 1, 1000)])
    out, audit = clean(raw)
    assert audit["duplicate_dates_removed"] == 1
    assert len(out) == 4 and audit["missing_dates_added"] == 2
    assert out.loc[0, "meantemp"] == 2
    assert not out["meantemp"].isna().any()


def test_season_labels():
    raw = _raw([("2020-01-15", 10, 50, 1, 1000), ("2020-07-15", 30, 80, 1, 1000)])
    out, _ = clean(raw)
    assert out.loc[0, "season"] == "Winter" and out.loc[len(out) - 1, "season"] == "Monsoon"
