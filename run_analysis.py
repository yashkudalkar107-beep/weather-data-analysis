"""End-to-end pipeline:  python run_analysis.py"""
import json

from src import analysis, cleaning, config, data_loader, visualize


def main():
    for d in (config.PROCESSED_DIR, config.FIG_DIR, config.TABLE_DIR, config.REPORT_DIR):
        d.mkdir(parents=True, exist_ok=True)

    print("[1/5] Loading raw data ...")
    raw = data_loader.load_raw()
    print(f"      {len(raw)} raw rows")

    print("[2/5] Cleaning ...")
    df, audit = cleaning.clean(raw)
    df.to_csv(config.CLEAN_FILE, index=False)
    (config.TABLE_DIR / "cleaning_audit.json").write_text(json.dumps(audit, indent=2))
    print(f"      {audit['rows_clean']} clean rows | {audit['invalid_count']} invalid values fixed | "
          f"{audit['duplicate_dates_removed']} duplicate date removed")

    print("[3/5] Analysing ...")
    results = analysis.run_all(df)
    for name, table in results["tables"].items():
        table.to_csv(config.TABLE_DIR / f"{name}.csv")
    (config.TABLE_DIR / "key_findings.json").write_text(json.dumps(results["findings"], indent=2))

    print("[4/5] Plotting ...")
    paths = visualize.make_all(raw, df, results)
    print(f"      {len(paths)} charts saved to {config.FIG_DIR}")

    print("[5/5] Done. Findings:")
    print(json.dumps(results["findings"], indent=2))


if __name__ == "__main__":
    main()
