# indsat — Indicator saturation for Stata

**indsat** is a Stata library for detecting outliers, location shifts, trend breaks and coefficient
breaks by general-to-specific indicator saturation, under one central command.

- **All indicator types:** IIS (impulses), SIS (steps), TIS / QIS / CIS (broken linear, quadratic,
  cubic trends), DIS (differenced impulses), PIS (pairwise impulses), MIS (coefficient breaks, with
  common break dates), BIS (designed breaks: volcanic, transitory change, ramp, user shape), UIS
  (user indicators), plus `super` (IIS+SIS) and `ultra` (IIS+SIS+TIS).
- **Faithful algorithm:** the default multi-path block search reproduces R `gets::isat`
  numerically. Split-half (Johansen–Nielsen; Nielsen–Qian) and m-step Huber-skip estimators are
  also provided.
- **After your own model:** run `regress`, `newey` or `ardl`, then `indsat, sis …`. The library
  saturates the model in memory and returns break tables, a dashboard of graphs, and a comparison
  of original versus robust estimates.
- **ARDL:** saturation of ARDL / error-correction models with the Pesaran–Shin–Smith bounds test.
- **Inference:** Jiao–Pretis outlier tests, distortion test, bias correction, coefficient paths,
  path test, forecasting, diagnostics, gauge theory and Monte Carlo tools.

## Installation

```stata
net install indsat, from("https://raw.githubusercontent.com/merwanroudane/indsat/main/") replace
net get indsat, from("https://raw.githubusercontent.com/merwanroudane/indsat/main/")   // example data and do-files
```

`indsat ardl` additionally requires `ssc install ardl`.

## Quick start

```stata
indsat                                   // menu of the library
help indsat_types                        // which indicator type to use, and when

use indsat_nile, clear
indsat flow, super tpval(0.01)           // outliers + level shifts
indsat dates                             // dates, sizes and regimes
indsat plot                              // four-panel dashboard
indsat test, hnull(1000) biascorr graph

regress y x1 x2                          // your usual model ...
indsat, sis mis(x1) common tpval(0.01)   // ... then saturate it

ardl c y D4p, lags(2 2 1)
indsat, sis tpval(0.01)                  // saturated ARDL + bounds test + long-run comparison
```

| Subcommand | Purpose |
|---|---|
| `indsat ardl` | ARDL / EC model with saturation and the PSS bounds test |
| `indsat loop` | results over a grid of target sizes; Jiao–Pretis scaling tests |
| `indsat gauge` | null theory: cut-offs, expected false indicators, efficiency |
| `indsat sim` | Monte Carlo gauge and potency |
| `indsat dates / path / plot / test` | break tables, coefficient paths, dashboard, path test |
| `indsat outlier / distort / biascorr / bias` | outlier tests, distortion test, bias correction, constancy test |
| `indsat forecast / diag` | forecasting with persistent shifts, misspecification tests |

## Complete guide with real data

`indsat_guide.do` is a step-by-step guide for researchers (comments in English and Arabic) using real
data only: the Nile flow, US life expectancy (built into Stata), UK road casualties and the DHSY
consumption function. It covers every main command, saves 12 graphs and an Excel table of breaks, and
runs in about 3-4 minutes:

```stata
net get indsat, from("https://raw.githubusercontent.com/merwanroudane/indsat/main/")
do indsat_guide.do
```

## The same examples in R

- `indsat_simple.R` + `indsat_data.xlsx`: a short beginner script with the R package `gets`
  (four examples, comments in English and Arabic). All data are in the Excel file, with a README
  sheet describing every variable. Put both files in one folder and run the script line by line.
- `indsat_guide.R`: the full guide (ARDL bounds test, MIS, robustness, Excel tables and graphs).

```r
install.packages(c("gets", "readxl"))
source("indsat_simple.R", echo = TRUE)
```

## Interactive lecture (Streamlit)

The folder [`lecture/`](lecture) contains a bilingual (Arabic / English terms) interactive lecture on
indicator saturation from zero. It covers history, concepts, every indicator type and post-estimation
tools, with animated Play / Pause demonstrations, a lab, a quiz and a glossary.

Run locally:

```bash
pip install -r lecture/requirements.txt
streamlit run lecture/streamlit_app.py
```

Deploy on Streamlit Community Cloud: repository `merwanroudane/indsat`, branch `main`,
main file path `lecture/streamlit_app.py`.

## محاضرة تفاعلية بالعربية

يحتوي المجلد `lecture/` على منصة Streamlit لتعليم تشبع المؤشرات من الصفر. فيها التاريخ والمفاهيم وكل
أنواع التشبع وأدوات ما بعد التقدير، مع رسوم متحركة بزر تشغيل، ومختبر تفاعلي، واختبار ذاتي، وقاموس
للمصطلحات بالعربية والإنجليزية.

## References

- Hendry, D.F., S. Johansen and C. Santos (2008). Automatic selection of indicators in a fully saturated regression. *Computational Statistics* 23: 317–335.
- Johansen, S. and B. Nielsen (2016). Asymptotic theory of outlier detection algorithms for linear time series regression models. *Scandinavian Journal of Statistics* 43: 321–348.
- Castle, J.L., J.A. Doornik, D.F. Hendry and F. Pretis (2015). Detecting location shifts during model selection by step-indicator saturation. *Econometrics* 3: 240–264.
- Pretis, F., J.J. Reade and G. Sucarrat (2018). Automated general-to-specific regression modeling and indicator saturation for outliers and structural breaks. *Journal of Statistical Software* 86(3).

## Author

Dr Merwan Roudane — merwanroudane920@gmail.com — [github.com/merwanroudane](https://github.com/merwanroudane)
