# Stock Market Analysis: Golden Cross Signals in SQL

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://stock-market-analysis-229qtwamqcqb4zh7nqshc8.streamlit.app/)

**Live dashboard:** https://stock-market-analysis-229qtwamqcqb4zh7nqshc8.streamlit.app/

SQL and Streamlit analysis of six NSE stocks using golden-cross (20-day / 50-day moving average) signals, including a data-quality fix for bonus issues that reverses the conclusion for TCS and Infosys.

## About the project

This project studies six NSE-listed stocks from **1 Jan 2015 to 31 Jul 2018** (889 trading days each): Bajaj Auto, Eicher Motors, Hero Motocorp, TVS Motors, Infosys and TCS.

The question: does the **golden cross** rule give useful Buy and Sell signals?

- **Buy:** the 20-day moving average of the close crosses *above* the 50-day average.
- **Sell:** the 20-day average crosses *below* the 50-day average.

A second question matters just as much: *can the data be trusted?* It cannot, without checking.

## Key findings

**1. A data trap changes the answer.** Infosys (15 Jun 2015) and TCS (31 May 2018) show one-day price drops of about 50%. These are 1:1 bonus issues, where the share count doubles and the price halves with no loss of value. Dividing earlier prices by 2 fixes the series.

| Stock | Raw change | Adjusted change |
|---|---|---|
| TVS Motors | +86.9% | +86.9% |
| Eicher Motors | +82.6% | +82.6% |
| **TCS** | −23.8% | **+52.4%** |
| **Infosys** | −30.9% | **+38.2%** |
| Bajaj Auto | +10.0% | +10.0% |
| Hero Motocorp | +6.0% | +6.0% |

**2. Signals change too.** The TCS Sell on 5 Jun 2018 was caused purely by the price cliff. After adjustment, TCS's latest signal is a **Buy** (20 Apr 2018). Total signals across the six stocks go from 56 Buys / 57 Sells to 57 / 57.

| Stock | Buys / Sells (adjusted) | Latest signal |
|---|---|---|
| Bajaj Auto | 12 / 11 | Buy, 21 Jun 2018 |
| Eicher Motors | 6 / 7 | Sell, 6 Jun 2018 |
| Hero Motocorp | 9 / 9 | Sell, 22 May 2018 |
| Infosys | 10 / 10 | Buy, 7 May 2018 |
| TCS | 12 / 12 | Buy, 20 Apr 2018 |
| TVS Motors | 8 / 8 | Sell, 17 May 2018 |

**3. The rule lagged and whipsawed.** In a simple long-only test (buy on each Buy, sell on the next Sell, no costs), following the signals trailed buy-and-hold on all six stocks. Bajaj Auto produced 23 signals, 11 of them within 30 days of the previous one.

## Dashboard

The Streamlit app has five tabs:

| Tab | What it shows |
|---|---|
| Overview | Best and weakest stock, signal totals, summary table, raw vs adjusted returns, rebased price comparison |
| Price & signals | Price, 20/50-day averages and Buy/Sell markers for any stock and date range, plus a day lookup |
| Data trap | Each stock's worst day, and raw vs adjusted prices side by side |
| Strategy test | Following the signals vs buy-and-hold, with an adjustable trading cost |
| Insights & recommendations | Summary of findings |

The sidebar can switch the bonus-issue adjustment on and off and edit the event dates and factors. The signals are computed with the same SQL window-function logic as the MySQL script.

## Tech stack

- **SQL (MySQL 8):** window functions (`AVG() OVER`, `LAG`, `ROW_NUMBER`), CTEs, `PARTITION BY`, `JOIN`, `UNION ALL`, `CASE`
- **Python:** pandas, Streamlit, Plotly
- **SQLite:** runs the dashboard's queries in memory
- **pandas / matplotlib:** used to cross-check results and draw the report charts

## Project structure

```
.
├── app.py                         # Streamlit dashboard
├── requirements.txt               # Python dependencies
├── stock_market_analysis.sql      # MySQL script: load, clean, analyse (tasks 1-14)
├── stock_market_insights.pdf      # Written report with charts
├── data/                          # Six NSE CSV files
└── README.md
```

## How to run

**Dashboard (local)**

```bash
git clone https://github.com/Ankit-604/Stock-Market-Analysis.git
cd Stock-Market-Analysis
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

On macOS or Linux, use `python3` in place of `py`. The app reads the CSVs from the `data/` folder; you can also upload them from the sidebar.

**SQL script (MySQL 8+)**

1. Enable local file loading: `SET GLOBAL local_infile = 1;`
2. In `stock_market_analysis.sql`, change `/path/to/` in the `LOAD DATA` lines to the folder that holds the CSVs.
3. Run the script top to bottom. Every table starts with `DROP TABLE IF EXISTS`, so it can be re-run safely.

## ETL summary

- **Extract:** six CSV files, 13 columns each.
- **Transform:** dates like `31-July-2018` converted to real `DATE` values with `STR_TO_DATE`; empty cells turned into `NULL`; stray spaces trimmed.
- **Load:** typed MySQL tables with `LOAD DATA LOCAL INFILE`, followed by checks (889 rows per table, date range, matching trading days across stocks).

The only data gap is a missing `deliverable_qty` value on two dates (9 Dec 2015 and 31 Aug 2017), which looks like an exchange reporting gap and does not affect any price result.

## Limitations

- The two bonus-issue dates were identified from the price pattern; confirm them against exchange corporate-action records.
- No dividends, brokerage, taxes, news, or market-index data are included.
- Four of the six stocks are auto companies, so results are correlated.
- Results cover 3.5 years and one path of history: they describe what happened, not what will happen.

This project is for learning purposes and is not investment advice.

## Author

**Ankit**: MBA (Finance & Business Analytics) | B.Tech, Electrical & Electronics Engineering

GitHub: [Ankit-604](https://github.com/Ankit-604)
