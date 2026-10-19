// Builds reports/Weather_Data_Analysis_Report.docx from the pipeline outputs.
const fs = require("fs");
const path = require("path");
const d = require("docx");
const { Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, HeadingLevel,
  AlignmentType, WidthType, ShadingType, BorderStyle, LevelFormat, Footer, PageNumber } = d;

const OUT = "outputs", FIG = path.join(OUT, "figures"), TAB = path.join(OUT, "tables");
const F = JSON.parse(fs.readFileSync(path.join(TAB, "key_findings.json")));
const A = JSON.parse(fs.readFileSync(path.join(TAB, "cleaning_audit.json")));
const csv = (f) => { const [h, ...r] = fs.readFileSync(path.join(TAB, f), "utf8").trim().split("\n").map(l => l.split(",")); return r.map(x => Object.fromEntries(h.map((k, i) => [k, x[i]]))); };
const monthly = csv("monthly_summary.csv"), yearly = csv("yearly_summary.csv"), seasonal = csv("seasonal_summary.csv");
const n1 = (x) => Number(x).toFixed(1);

const FONT = "Arial", INK = "1F2937", ACCENT = "1F5C8B", GREY = "6B7280";
const W = 9026; // A4 content width (1" margins)
const run = (t, o = {}) => new TextRun({ text: t, font: FONT, size: 22, color: INK, ...o });
const p = (children, o = {}) => new Paragraph({ spacing: { after: 140, line: 300 }, children: Array.isArray(children) ? children : [run(children)], ...o });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 320, after: 140 }, children: [new TextRun({ text: t, font: FONT, size: 30, bold: true, color: ACCENT })] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 }, children: [new TextRun({ text: t, font: FONT, size: 24, bold: true, color: INK })] });
const bullet = (parts) => new Paragraph({ numbering: { reference: "b", level: 0 }, spacing: { after: 90, line: 290 }, children: Array.isArray(parts) ? parts : [run(parts)] });
const bold = (t) => run(t, { bold: true });

function pngSize(file) { const b = fs.readFileSync(file); return [b.readUInt32BE(16), b.readUInt32BE(20)]; }
function figure(file, caption, widthPx = 560) {
  const full = path.join(FIG, file), [w, h] = pngSize(full);
  return [
    new Paragraph({ alignment: AlignmentType.CENTER, keepNext: true, spacing: { before: 120, after: 60 },
      children: [new ImageRun({ type: "png", data: fs.readFileSync(full), transformation: { width: widthPx, height: Math.round(widthPx * h / w) },
        altText: { title: caption, description: caption, name: file } })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [run(caption, { italics: true, size: 18, color: GREY })] }),
  ];
}

const bd = { style: BorderStyle.SINGLE, size: 4, color: "D1D5DB" };
const borders = { top: bd, bottom: bd, left: bd, right: bd };
function table(headers, rows, widths, numeric = true) {
  const cell = (t, w, hdr, right) => new TableCell({
    width: { size: w, type: WidthType.DXA }, borders,
    shading: hdr ? { fill: ACCENT, type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 70, bottom: 70, left: 110, right: 110 },
    children: [new Paragraph({ keepNext: true, alignment: right ? AlignmentType.RIGHT : AlignmentType.LEFT,
      children: [new TextRun({ text: String(t), font: FONT, size: 19, bold: hdr, color: hdr ? "FFFFFF" : INK })] })] });
  return new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, widths[i], true, numeric && i > 0 && !isNaN(parseFloat(rows[0][i])))) }),
      ...rows.map(r => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, widths[i], false, numeric && i > 0 && !isNaN(parseFloat(c)))) }))] });
}

const m = Object.fromEntries(monthly.map(r => [r.month_name, r]));
const seas = Object.fromEntries(seasonal.map(r => [r.season, r]));
const y13 = yearly[0], y16 = yearly[yearly.length - 1];
const ex = F.extremes;
const invalidDates = A.invalid_values.map(v => v.date);

const children = [
  // ---- Title block
  new Paragraph({ spacing: { before: 600, after: 80 }, children: [new TextRun({ text: "Weather Data Analysis", font: FONT, size: 56, bold: true, color: ACCENT })] }),
  new Paragraph({ spacing: { after: 80 }, children: [new TextRun({ text: "Temperature, humidity and seasonal trends in Delhi, 2013\u20132017", font: FONT, size: 28, color: INK })] }),
  new Paragraph({ border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: ACCENT, space: 6 } }, spacing: { after: 240 },
    children: [new TextRun({ text: "Project report  |  Prepared by Yash, MCA, Karnatak University, Dharwad  |  Python, Pandas, Matplotlib, Seaborn", font: FONT, size: 19, color: GREY })] }),

  h1("1. Summary"),
  p(`This project analyses ${A.rows_clean.toLocaleString()} days of daily weather observations for Delhi (${A.date_min} to ${A.date_max}). After cleaning the data, it measures how temperature, humidity, wind and pressure change through the year and compares months, seasons and years.`),
  bullet([bold("Strong seasonality. "), run(`June is the hottest month (${n1(F.hottest_month_temp)}\u00b0C on average) and January the coolest (${n1(F.coolest_month_temp)}\u00b0C), an annual swing of ${n1(F.annual_range_temp)}\u00b0C.`)]),
  bullet([bold("Hot and dry before the monsoon, humid during it. "), run(`Average humidity falls to ${n1(m.May.mean_humidity)}% in May and recovers to about ${n1(m.Jul.mean_humidity)}% in July\u2013August. Temperature and humidity are negatively correlated (r = ${F.temp_humidity_corr}).`)]),
  bullet([bold("Rain-bearing conditions are concentrated in July and August. "), run(`About ${Math.round(m.Jul.warm_humid_day_pct)}% of July days and ${Math.round(m.Aug.warm_humid_day_pct)}% of August days were warm and humid, against 0% from November to April (a proxy, because the dataset has no rainfall column).`)]),
  bullet([bold("The record warms across the period. "), run(`2016 was the warmest full year (${y16.mean_temp}\u00b0C vs ${y13.mean_temp}\u00b0C in 2013), but four years is too short to call this a climate trend.`)]),

  h1("2. Data"),
  p([run("Source: "), bold("Daily Climate time series data"), run(" (Kaggle, by Sumanth Vrao), daily means for Delhi. The Kaggle train and test files were combined into one continuous series. Variables: mean temperature (\u00b0C), relative humidity (%), wind speed (km/h) and mean atmospheric pressure (hPa).")]),
  p([bold("Important limitation: "), run("the dataset contains no rainfall measurements. To still address rainfall, the project counts \u201cwarm and humid days\u201d (humidity \u2265 70% and temperature \u2265 25\u00b0C) as a rain-bearing proxy. The temperature condition removes cold, foggy winter days, which are humid but not rainy. Treat it as an indicator of monsoon-type conditions, not as millimetres of rain.")]),

  h1("3. Cleaning and quality checks"),
  p("All fixes are performed by code (src/cleaning.py) and logged to outputs/tables/cleaning_audit.json, so the process is reproducible."),
  table(["Check", "Result", "Action taken"], [
    ["Missing values", "None in any column", "Interpolation logic kept in the pipeline"],
    ["Gaps in the daily calendar", `${A.missing_dates_added} missing dates`, "None needed"],
    ["Duplicate dates", `${A.duplicate_dates_removed} (${A.duplicate_dates[0]})`, "Kept the later, complete record"],
    ["Incorrect records", `${A.invalid_count} pressure values outside 980\u20131050 hPa`, "Set to missing, then time-interpolated"],
    ["Rows", `${A.rows_raw.toLocaleString()} raw to ${A.rows_clean.toLocaleString()} clean`, "Saved to data/processed/"],
  ], [2400, 3200, 3426], false),
  p([run("")], { spacing: { after: 60 } }),
  p(`The invalid pressure readings include impossible values such as 7,679 hPa (${invalidDates[0]}) and \u22123 hPa (${invalidDates[5]}); nine of the ten fall in 2016. Temperature, humidity and wind were within plausible ranges, so no other values were changed.`),
  ...figure("01_cleaning_pressure_before_after.png", "Figure 1. Pressure before and after removing invalid records.", 520),

  h1("4. Findings"),
  h2("4.1 Temperature"),
  p(`Temperature follows a clear annual cycle. It rises from ${n1(m.Jan.mean_temp)}\u00b0C in January to a May\u2013June peak (${n1(m.May.mean_temp)}\u00b0C and ${n1(m.Jun.mean_temp)}\u00b0C), eases through the monsoon months (about ${n1(m.Aug.mean_temp)}\u00b0C in August) and drops again from October. The hottest recorded day was ${ex.hottest_day.date} (${ex.hottest_day.value}\u00b0C) and the coldest was ${ex.coldest_day.date} (${ex.coldest_day.value}\u00b0C).`),
  ...figure("02_temperature_timeseries.png", "Figure 2. Daily mean temperature with a 30-day rolling mean.", 500),
  ...figure("03_monthly_temperature.png", "Figure 3. Average temperature by month (shaded band = \u00b11 standard deviation).", 430),
  h2("4.2 Humidity"),
  p(`Humidity moves opposite to temperature. The driest months are April and May (${n1(m.Apr.mean_humidity)}% and ${n1(m.May.mean_humidity)}%). January has the highest average (${n1(m.Jan.mean_humidity)}%) which is consistent with cool winter air and fog, followed by December (${n1(m.Dec.mean_humidity)}%) and the monsoon months July and August (about ${n1(m.Jul.mean_humidity)}%). The overall temperature\u2013humidity correlation is ${F.temp_humidity_corr}.`),
  ...figure("04_monthly_humidity.png", "Figure 4. Average humidity by month, coloured by season.", 430),
  ...figure("05_temp_vs_humidity_scatter.png", "Figure 5. Temperature vs humidity. Monsoon days form a warm and humid cluster.", 340),
  h2("4.3 Rainfall proxy"),
  p(`Warm and humid days are almost absent from November to May. They jump to ${n1(m.Jun.warm_humid_day_pct)}% of days in June, peak in July (${n1(m.Jul.warm_humid_day_pct)}%) and August (${n1(m.Aug.warm_humid_day_pct)}%), and fade through September (${n1(m.Sep.warm_humid_day_pct)}%). Across the monsoon season as defined by the IMD (June\u2013September), ${n1(seas.Monsoon.warm_humid_day_pct)}% of days met the condition.`),
  ...figure("10_warm_humid_days_rainfall_proxy.png", "Figure 6. Share of warm and humid days by month (rainfall proxy).", 430),
  h2("4.4 Month and season comparison"),
  table(["Month", "Temp (\u00b0C)", "Humidity (%)", "Wind (km/h)", "Pressure (hPa)", "Warm & humid days (%)"],
    monthly.map(r => [r.month_name, n1(r.mean_temp), n1(r.mean_humidity), n1(r.mean_wind), n1(r.mean_pressure), n1(r.warm_humid_day_pct)]),
    [1300, 1400, 1500, 1500, 1626, 1700]),
  p([run("")], { spacing: { after: 60 } }),
  p(`Wind is strongest in June (${n1(F.windiest_month_val)} km/h) and weakest in November (${n1(m.Nov.mean_wind)} km/h). Pressure moves with temperature (r = ${F.temp_pressure_corr}): about ${n1(m.Jan.mean_pressure)} hPa in January against ${n1(m.Jun.mean_pressure)} hPa in June. By season, winter averages ${n1(seas.Winter.mean_temp)}\u00b0C, the pre-monsoon summer ${n1(seas.Summer.mean_temp)}\u00b0C, the monsoon ${n1(seas.Monsoon.mean_temp)}\u00b0C and the post-monsoon ${n1(seas["Post-monsoon"].mean_temp)}\u00b0C. The monsoon block averages hotter than summer because June, the hottest month, belongs to it.`),
  ...figure("06_heatmap_year_month_temp.png", "Figure 7. Mean temperature by year and month.", 480),
  ...figure("08_seasonal_comparison.png", "Figure 8. Temperature, humidity and wind speed distributions by season.", 520),
  h2("4.5 Year-over-year change"),
  p(`Among the four complete years, mean temperature rose from ${y13.mean_temp}\u00b0C (2013) to ${y16.mean_temp}\u00b0C (2016) and mean humidity fell from ${y13.mean_humidity}% to ${y16.mean_humidity}%. After removing the seasonal cycle, monthly temperature anomalies increase by about ${F.temp_trend.slope_per_year}\u00b0C per year (r = ${F.temp_trend.r}, ${F.temp_trend.n_months} months) and humidity anomalies fall by about ${Math.abs(F.humidity_trend.slope_per_year)} percentage points per year. These slopes describe this short record only. They should not be read as a long-term climate trend, and part of the shift may reflect changes in how the data were collected.`),

  h1("5. Limitations"),
  bullet("No rainfall column: the warm-and-humid-day measure is a proxy and cannot give rainfall amounts."),
  bullet("One location and a short record (about 4.3 years); 2017 covers January to April only, so year comparisons use 2013\u20132016."),
  bullet("Daily means hide extremes; the dataset has no daily minimum or maximum temperature."),
  bullet("Pressure values were repaired by interpolation, so pressure statistics are approximate for the ten affected days."),

  h1("6. Conclusion and next steps"),
  p("The data shows a pronounced hot, dry pre-monsoon (April to June), a humid monsoon peak in July and August, and a cool, foggy and humid winter. Temperature, humidity and pressure are tightly linked through the seasonal cycle. Natural extensions are adding a dataset with real rainfall, forecasting temperature with a time-series model (for example SARIMA or Prophet), and repeating the pipeline for other Indian cities."),
];

const doc = new Document({
  creator: "Yash", title: "Weather Data Analysis Report",
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  numbering: { config: [{ reference: "b", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1200, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: "Weather Data Analysis  |  Page ", font: FONT, size: 17, color: GREY }),
        new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 17, color: GREY })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync("reports/Weather_Data_Analysis_Report.docx", b); console.log("report written"); });
