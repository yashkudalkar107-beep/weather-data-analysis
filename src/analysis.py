"""Tasks 4 & 6 - Analyse temperature, humidity, rainfall-proxy and monthly/seasonal patterns."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config

VARS = ["meantemp", "humidity", "wind_speed", "meanpressure"]


def full_years(df: pd.DataFrame) -> pd.DataFrame:
    """Calendar years with all 12 months of data (2017 is only Jan-Apr)."""
    months_per_year = df.groupby("year")["month"].nunique()
    keep = months_per_year[months_per_year == 12].index
    return df[df["year"].isin(keep)]


def summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    return df[VARS].describe().T.round(2)


def yearly_table(df: pd.DataFrame) -> pd.DataFrame:
    fy = full_years(df)
    t = fy.groupby("year").agg(
        mean_temp=("meantemp", "mean"), max_temp=("meantemp", "max"), min_temp=("meantemp", "min"),
        mean_humidity=("humidity", "mean"), mean_wind=("wind_speed", "mean"),
        warm_humid_days=("warm_humid_day", "sum"))
    return t.round(2)


def monthly_table(df: pd.DataFrame) -> pd.DataFrame:
    """Month-of-year climatology across all years (Task 6)."""
    t = df.groupby("month").agg(
        mean_temp=("meantemp", "mean"), std_temp=("meantemp", "std"),
        max_temp=("meantemp", "max"), min_temp=("meantemp", "min"),
        mean_humidity=("humidity", "mean"), mean_wind=("wind_speed", "mean"),
        mean_pressure=("meanpressure", "mean"), warm_humid_day_pct=("warm_humid_day", "mean"))
    t["warm_humid_day_pct"] *= 100
    t.insert(0, "month_name", config.MONTH_LABELS)
    return t.round(2)


def seasonal_table(df: pd.DataFrame) -> pd.DataFrame:
    t = df.groupby("season", observed=True).agg(
        days=("meantemp", "size"), mean_temp=("meantemp", "mean"),
        mean_humidity=("humidity", "mean"), mean_wind=("wind_speed", "mean"),
        mean_pressure=("meanpressure", "mean"), warm_humid_day_pct=("warm_humid_day", "mean"))
    t["warm_humid_day_pct"] *= 100
    return t.round(2)


def month_year_pivot(df: pd.DataFrame, col: str = "meantemp") -> pd.DataFrame:
    p = df.pivot_table(index="year", columns="month", values=col, aggfunc="mean")
    p.columns = [config.MONTH_LABELS[m - 1] for m in p.columns]
    return p.round(2)


def correlations(df: pd.DataFrame) -> pd.DataFrame:
    return df[VARS].corr().round(2)


def deseasonalised_trend(df: pd.DataFrame, col: str = "meantemp") -> dict:
    """Linear trend of monthly anomalies (month mean minus its climatology), in units/year."""
    m = df.set_index("date")[col].resample("MS").mean()
    anomaly = m - m.groupby(m.index.month).transform("mean")
    x = (m.index.year + (m.index.month - 1) / 12).to_numpy()
    slope, intercept = np.polyfit(x, anomaly.to_numpy(), 1)
    r = np.corrcoef(x, anomaly.to_numpy())[0, 1]
    return {"slope_per_year": round(float(slope), 3), "r": round(float(r), 3),
            "n_months": int(len(m))}


def extremes(df: pd.DataFrame) -> dict:
    def row(idx, col):
        r = df.loc[idx]
        return {"date": r["date"].strftime("%Y-%m-%d"), "value": round(float(r[col]), 2)}
    return {
        "hottest_day": row(df["meantemp"].idxmax(), "meantemp"),
        "coldest_day": row(df["meantemp"].idxmin(), "meantemp"),
        "most_humid_day": row(df["humidity"].idxmax(), "humidity"),
        "driest_day": row(df["humidity"].idxmin(), "humidity"),
        "windiest_day": row(df["wind_speed"].idxmax(), "wind_speed"),
    }


def run_all(df: pd.DataFrame) -> dict:
    """Run every analysis; returns tables (DataFrames) and key findings (JSON-safe)."""
    monthly, seasonal, yearly = monthly_table(df), seasonal_table(df), yearly_table(df)
    corr = correlations(df)
    ms = monthly.set_index("month_name")

    findings = {
        "temp_trend": deseasonalised_trend(df, "meantemp"),
        "humidity_trend": deseasonalised_trend(df, "humidity"),
        "hottest_month": ms["mean_temp"].idxmax(), "hottest_month_temp": float(ms["mean_temp"].max()),
        "coolest_month": ms["mean_temp"].idxmin(), "coolest_month_temp": float(ms["mean_temp"].min()),
        "most_humid_month": ms["mean_humidity"].idxmax(), "most_humid_month_val": float(ms["mean_humidity"].max()),
        "driest_month": ms["mean_humidity"].idxmin(), "driest_month_val": float(ms["mean_humidity"].min()),
        "windiest_month": ms["mean_wind"].idxmax(), "windiest_month_val": float(ms["mean_wind"].max()),
        "temp_humidity_corr": float(corr.loc["meantemp", "humidity"]),
        "temp_pressure_corr": float(corr.loc["meantemp", "meanpressure"]),
        "humidity_pressure_corr": float(corr.loc["humidity", "meanpressure"]),
        "temp_wind_corr": float(corr.loc["meantemp", "wind_speed"]),
        "annual_range_temp": round(float(ms["mean_temp"].max() - ms["mean_temp"].min()), 2),
        "extremes": extremes(df),
        "full_years": [int(y) for y in yearly.index],
        "warmest_year": int(yearly["mean_temp"].idxmax()),
        "coolest_year": int(yearly["mean_temp"].idxmin()),
        "warm_humid_day_pct_by_season": seasonal["warm_humid_day_pct"].to_dict(),
        "overall": {
            "mean_temp": round(float(df["meantemp"].mean()), 2),
            "mean_humidity": round(float(df["humidity"].mean()), 2),
            "mean_wind": round(float(df["wind_speed"].mean()), 2),
        },
    }
    tables = {"summary_stats": summary_stats(df), "yearly_summary": yearly,
              "monthly_summary": monthly, "seasonal_summary": seasonal,
              "month_year_mean_temp": month_year_pivot(df), "correlations": corr}
    return {"tables": tables, "findings": findings}
