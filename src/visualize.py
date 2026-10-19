"""Task 5 - Charts (Matplotlib + Seaborn). Every function saves a PNG and returns its path."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from . import config

SEASON_COLORS = {"Winter": "#3b82c4", "Summer": "#e8742a",
                 "Monsoon": "#2e9e6b", "Post-monsoon": "#8a63b8"}
sns.set_theme(style="whitegrid", context="notebook", font_scale=1.0)
plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 160, "axes.titleweight": "bold",
                     "axes.titlesize": 13, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid.axis": "y"})
MONTHS = config.MONTH_LABELS


def _year_axis(ax):
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, axis="x", alpha=.4)


def _save(fig, name: str):
    config.FIG_DIR.mkdir(parents=True, exist_ok=True)
    path = config.FIG_DIR / name
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def fig_cleaning_pressure(raw: pd.DataFrame, clean: pd.DataFrame):
    """Before/after view of the atmospheric-pressure fix (Task 3)."""
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.2))
    r = raw.drop_duplicates("date", keep="last").sort_values("date")
    ax[0].plot(r["date"], r["meanpressure"], lw=0.8, color="#c0392b")
    ax[0].set_title("Before cleaning: raw pressure (hPa)")
    ax[0].set_ylabel("hPa")
    _year_axis(ax[0])
    ax[1].plot(clean["date"], clean["meanpressure"], lw=0.8, color="#2e9e6b")
    ax[1].set_title("After cleaning: invalid records interpolated")
    ax[1].set_ylabel("hPa")
    _year_axis(ax[1])
    return _save(fig, "01_cleaning_pressure_before_after.png")


def fig_temp_timeseries(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(13, 4.5))
    ax.plot(df["date"], df["meantemp"], lw=0.7, color="#f0a37a", label="Daily mean temp")
    ax.plot(df["date"], df["meantemp"].rolling(30, center=True).mean(), lw=2.2,
            color="#c0392b", label="30-day rolling mean")
    ax.set_title("Daily Mean Temperature, Delhi (2013-2017)")
    ax.set_ylabel("Temperature (\u00b0C)")
    ax.legend(frameon=False, loc="upper left")
    _year_axis(ax)
    return _save(fig, "02_temperature_timeseries.png")


def fig_monthly_temp(monthly: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 4.8))
    x = np.arange(12)
    ax.fill_between(x, monthly["mean_temp"] - monthly["std_temp"],
                    monthly["mean_temp"] + monthly["std_temp"], color="#f6c9b0", alpha=.6,
                    label="\u00b11 std dev")
    ax.plot(x, monthly["mean_temp"], marker="o", color="#c0392b", lw=2.5, label="Mean temperature")
    hot, cold = monthly["mean_temp"].idxmax() - 1, monthly["mean_temp"].idxmin() - 1
    for i, c in ((hot, "#c0392b"), (cold, "#3b82c4")):
        ax.annotate(f"{monthly['mean_temp'].iloc[i]:.1f}\u00b0C", (i, monthly['mean_temp'].iloc[i]),
                    textcoords="offset points", xytext=(0, 12 if i == hot else -20), ha="center", fontweight="bold", color=c)
    ax.set_xticks(x, MONTHS)
    ax.set_xlim(-0.4, 11.4)
    ax.set_title("Average Temperature by Month")
    ax.set_ylabel("Temperature (\u00b0C)")
    ax.legend(frameon=False)
    return _save(fig, "03_monthly_temperature.png")


def fig_monthly_humidity(monthly: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 4.8))
    colors = [SEASON_COLORS[config.SEASON_MAP[m]] for m in monthly.index]
    ax.bar(MONTHS, monthly["mean_humidity"], color=colors)
    for i, v in enumerate(monthly["mean_humidity"]):
        ax.text(i, v + 1, f"{v:.0f}", ha="center", fontsize=9)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Relative humidity (%)")
    ax.set_title("Average Humidity by Month (coloured by season)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in SEASON_COLORS.values()]
    ax.legend(handles, SEASON_COLORS, frameon=False, ncol=4, loc="upper center",
              bbox_to_anchor=(0.5, 1.0))
    return _save(fig, "04_monthly_humidity.png")


def fig_temp_vs_humidity(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(data=df, x="meantemp", y="humidity", hue="season", palette=SEASON_COLORS,
                    alpha=.65, s=22, edgecolor=None, ax=ax, hue_order=config.SEASON_ORDER)
    sns.regplot(data=df, x="meantemp", y="humidity", scatter=False, color="black",
                line_kws={"lw": 1.5, "ls": "--"}, ax=ax)
    r = df["meantemp"].corr(df["humidity"])
    ax.grid(True, axis="both")
    ax.set_title(f"Temperature vs Humidity (r = {r:.2f})")
    ax.set_xlabel("Mean temperature (\u00b0C)")
    ax.set_ylabel("Relative humidity (%)")
    ax.legend(title="Season", frameon=False)
    return _save(fig, "05_temp_vs_humidity_scatter.png")


def fig_heatmap_year_month(pivot: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(11, 4.2))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdYlBu_r", linewidths=.5,
                cbar_kws={"label": "\u00b0C"}, ax=ax)
    ax.set_title("Mean Temperature: Year \u00d7 Month")
    ax.set_xlabel("")
    ax.set_ylabel("")
    return _save(fig, "06_heatmap_year_month_temp.png")


def fig_box_by_month(df: pd.DataFrame):
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True)
    order = MONTHS
    sns.boxplot(data=df, x="month_name", y="meantemp", order=order, color="#f0a37a",
                fliersize=2, ax=axes[0])
    axes[0].set_title("Monthly Distribution of Temperature")
    axes[0].set_ylabel("Temperature (\u00b0C)")
    axes[0].set_xlabel("")
    sns.boxplot(data=df, x="month_name", y="humidity", order=order, color="#7fb5d9",
                fliersize=2, ax=axes[1])
    axes[1].set_title("Monthly Distribution of Humidity")
    axes[1].set_ylabel("Humidity (%)")
    axes[1].set_xlabel("")
    return _save(fig, "07_monthly_boxplots.png")


def fig_seasonal(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    for ax, col, title, unit in zip(axes, ["meantemp", "humidity", "wind_speed"],
                                    ["Temperature", "Humidity", "Wind speed"],
                                    ["\u00b0C", "%", "km/h"]):
        sns.violinplot(data=df, x="season", y=col, order=config.SEASON_ORDER,
                       palette=SEASON_COLORS, hue="season", legend=False, inner="quartile",
                       cut=0, ax=ax)
        ax.set_title(f"{title} by Season")
        ax.set_xlabel("")
        ax.set_ylabel(unit)
        ax.tick_params(axis="x", rotation=15)
    return _save(fig, "08_seasonal_comparison.png")


def fig_correlation(corr: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(6.2, 5))
    labels = ["Temperature", "Humidity", "Wind speed", "Pressure"]
    sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, square=True, linewidths=.5,
                xticklabels=labels, yticklabels=labels, ax=ax)
    ax.set_title("Correlation Matrix")
    return _save(fig, "09_correlation_matrix.png")


def fig_humid_days(monthly: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 4.6))
    colors = [SEASON_COLORS[config.SEASON_MAP[m]] for m in monthly.index]
    ax.bar(MONTHS, monthly["warm_humid_day_pct"], color=colors)
    ax.set_ylabel("% of days")
    ax.set_title(f"Warm & Humid Days by Month (rainfall proxy: humidity \u2265 {config.HUMID_THRESHOLD:.0f}% and temp \u2265 {config.WARM_THRESHOLD:.0f}\u00b0C)", fontsize=11)
    ax.set_ylim(0, max(30, monthly["warm_humid_day_pct"].max() * 1.15))
    return _save(fig, "10_warm_humid_days_rainfall_proxy.png")


def fig_year_comparison(df: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8))
    p = df.pivot_table(index="month", columns="year", values="meantemp", aggfunc="mean")
    q = df.pivot_table(index="month", columns="year", values="humidity", aggfunc="mean")
    pal = sns.color_palette("viridis", p.shape[1])
    for (yr, c) in zip(p.columns, pal):
        axes[0].plot(MONTHS, p[yr].values, marker="o", ms=4, color=c, label=str(yr))
        axes[1].plot(MONTHS, q[yr].values, marker="o", ms=4, color=c, label=str(yr))
    axes[0].set_title("Monthly Mean Temperature by Year")
    axes[0].set_ylabel("\u00b0C")
    axes[1].set_title("Monthly Mean Humidity by Year")
    axes[1].set_ylabel("%")
    axes[1].legend(title="Year", frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1))
    return _save(fig, "11_year_over_year_comparison.png")


def fig_wind_pressure(monthly: pd.DataFrame):
    fig, ax = plt.subplots(1, 2, figsize=(13, 4.4))
    ax[0].plot(MONTHS, monthly["mean_wind"], marker="o", color="#2e86ab", lw=2.2)
    ax[0].set_title("Average Wind Speed by Month")
    ax[0].set_ylabel("km/h")
    ax[1].plot(MONTHS, monthly["mean_pressure"], marker="o", color="#8a63b8", lw=2.2)
    ax[1].set_title("Average Atmospheric Pressure by Month")
    ax[1].set_ylabel("hPa")
    return _save(fig, "12_wind_and_pressure_by_month.png")


def make_all(raw, df, results) -> list:
    t = results["tables"]
    return [fig_cleaning_pressure(raw, df), fig_temp_timeseries(df),
            fig_monthly_temp(t["monthly_summary"]),
            fig_monthly_humidity(t["monthly_summary"]), fig_temp_vs_humidity(df),
            fig_heatmap_year_month(t["month_year_mean_temp"]), fig_box_by_month(df),
            fig_seasonal(df), fig_correlation(t["correlations"]),
            fig_humid_days(t["monthly_summary"]), fig_year_comparison(df),
            fig_wind_pressure(t["monthly_summary"])]
