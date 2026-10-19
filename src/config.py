"""Central configuration: paths, validity limits, season definitions."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
FIG_DIR = ROOT / "outputs" / "figures"
TABLE_DIR = ROOT / "outputs" / "tables"
REPORT_DIR = ROOT / "reports"

RAW_FILES = ["DailyDelhiClimateTrain.csv", "DailyDelhiClimateTest.csv"]
CLEAN_FILE = PROCESSED_DIR / "delhi_weather_clean.csv"

# Physically plausible daily-mean ranges for Delhi (used to flag incorrect records).
VALID_RANGES = {
    "meantemp": (-5.0, 50.0),         # deg C
    "humidity": (0.0, 100.0),         # %
    "wind_speed": (0.0, 60.0),        # km/h
    "meanpressure": (980.0, 1050.0),  # hPa (surface pressure)
}

# India Meteorological Department (IMD) seasons.
SEASON_MAP = {
    12: "Winter", 1: "Winter", 2: "Winter",
    3: "Summer", 4: "Summer", 5: "Summer",
    6: "Monsoon", 7: "Monsoon", 8: "Monsoon", 9: "Monsoon",
    10: "Post-monsoon", 11: "Post-monsoon",
}
SEASON_ORDER = ["Winter", "Summer", "Monsoon", "Post-monsoon"]
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# The dataset has NO rainfall column. As a clearly labelled proxy for rain-bearing
# (monsoon-type) conditions we count "warm & humid" days: humidity >= 70% AND mean
# temperature >= 25 C. The temperature condition excludes cold, foggy winter days,
# which are humid but not rainy.
HUMID_THRESHOLD = 70.0
WARM_THRESHOLD = 25.0
