# =============================================================================
#  indsat_guide.R  --  A COMPLETE GUIDE FOR RESEARCHERS (REAL DATA), R VERSION
#  دليل الباحث الكامل لتشبع المؤشرات في R ببيانات حقيقية (نظير indsat_guide.do في Stata)
#
#  Dr Merwan Roudane  |  merwanroudane920@gmail.com  |  github.com/merwanroudane/indsat
#
#  Engine: the R package 'gets' (Pretis, Reade & Sucarrat 2018), function isat().
#  المحرك: حزمة gets في R والدالة isat()
#
#  EVERY EXAMPLE FOLLOWS THE SAME SIX STEPS   /   كل مثال يتبع نفس الخطوات الست
#    A. Data dictionary: dependent variable, regressors, units      قاموس البيانات: التابع والمستقلة والوحدات
#    B. Look at the data (summary, graph)                           النظر إلى البيانات
#    C. BEFORE estimation: saturate each variable on its own         قبل التقدير: تشبيع كل متغير بمفرده
#       -> outliers and breaks in each series                        القيم الشاذة والكسور في كل سلسلة
#    D. Estimation: the economic model (lm / ARDL)                   التقدير: النموذج الاقتصادي
#    E. AFTER estimation: saturate the estimated model               بعد التقدير: تشبيع النموذج المقدَّر
#       -> robust coefficients, break dates, tests, graphs           معاملات قوية، تواريخ الكسور، اختبارات، رسوم
#    F. Interpretation                                               التفسير
#
#  CONTENTS / المحتويات
#    PART 0  Setup and helper functions                              الإعداد والدوال المساعدة
#    PART 1  Theory before data                                      النظرية قبل البيانات
#    PART 2  Nile river flow       (one variable, no regressors)     نهر النيل: متغير واحد بلا متغيرات مستقلة
#    PART 3  US life expectancy    (one variable + time trend)       أمد الحياة: متغير واحد مع اتجاه زمني
#    PART 4  UK road casualties    (regression with regressors)      ضحايا الطرق: انحدار بمتغيرات مستقلة
#    PART 5  UK consumption (DHSY) (ARDL + bounds test)              الاستهلاك البريطاني: ARDL واختبار الحدود
#    PART 6  Robustness                                              المتانة
#    PART 7  Checklist for your paper                                قائمة التحقق لورقتك
#
#  HOW TO RUN / طريقة التشغيل
#    Open the file in RStudio and run it section by section (Ctrl+Enter), or run
#    everything with  source("indsat_guide.R", echo = TRUE).
#    افتح الملف في RStudio وشغّله جزءًا جزءًا، أو شغّله كاملًا بالأمر source
#  Outputs / المخرجات: folder indsat_guide_R_output (log, PNG graphs, Excel tables).
#  Run time about 3-4 minutes (PART 6 is the slowest).  مدة التشغيل 3 إلى 4 دقائق تقريبًا
# =============================================================================


# -----------------------------------------------------------------------------
# PART 0. SETUP  /  الإعداد
# -----------------------------------------------------------------------------
# Packages: gets (saturation), ARDL (ARDL models and the bounds test),
# haven (read the Stata .dta file of PART 5), openxlsx (Excel tables).
# الحزم: gets للتشبع، ARDL لنماذج ARDL واختبار الحدود، haven لقراءة ملف Stata، openxlsx لجداول Excel
for (p in c("gets", "ARDL", "haven", "openxlsx")) {
  if (!requireNamespace(p, quietly = TRUE)) install.packages(p)
}
library(gets)
library(ARDL)

# English month names in the indicator labels (sisFeb 1983, not sisfévr. 1983).
# أسماء الأشهر بالإنجليزية في أسماء المؤشرات
invisible(Sys.setlocale("LC_TIME", "C"))
set.seed(2026)

out <- "indsat_guide_R_output"
dir.create(out, showWarnings = FALSE)
wb <- openxlsx::createWorkbook()               # one Excel sheet per example  ورقة Excel لكل مثال

# THE DATA / البيانات
#  - Nile and UK Seatbelts are built into R (package 'datasets'): no file needed.
#  - US life expectancy is typed below (public CDC data, PART 3).
#  - DHSY (PART 5) is the Stata file indsat_dhsy.dta: put it in the working
#    directory, or the line in PART 5 downloads it from GitHub.
#  النيل وحزام الأمان مدمجة في R؛ أمد الحياة مكتوب داخل الملف؛ ملف DHSY يُقرأ محليًا أو يُنزَّل من GitHub
gh <- "https://raw.githubusercontent.com/merwanroudane/indsat/main/"

# ---- Helper 1: save a graph as PNG (and also draw it on screen) ------------
# أداة 1: حفظ الرسم بصيغة PNG وعرضه على الشاشة
save_png <- function(file, draw) {
  if (interactive()) draw()
  png(file.path(out, file), width = 1600, height = 1000, res = 150)
  on.exit(dev.off())
  draw()
}

# ---- Helper 2: table of retained indicators (name, type, date, coef, se, t, p)
# أداة 2: جدول المؤشرات المحتفظ بها: الاسم، النوع، التاريخ، المعامل، الخطأ المعياري، t، p
breaks_table <- function(m) {
  if (length(m$ISnames) == 0) return(data.frame(indicator = character(0)))
  r <- m$mean.results[m$ISnames, , drop = FALSE]
  kind <- toupper(sub("^(iis|sis|tis|mis)?.*$", "\\1", m$ISnames))
  kind[kind == ""] <- "UIS"
  data.frame(indicator = m$ISnames, kind = kind,
             date = sub("^(iis|sis|tis|mis[._a-z]*)", "", m$ISnames),
             coef = round(r[, 1], 4), se = round(r[, 2], 4),
             t = round(r[, 3], 2), p = signif(r[, 4], 3), row.names = NULL)
}

# ---- Helper 3: write a table to its own Excel sheet --------------------------
# أداة 3: كتابة الجدول في ورقة Excel خاصة به
to_excel <- function(df, sheet) {
  openxlsx::addWorksheet(wb, sheet)
  openxlsx::writeData(wb, sheet, df)
}

# ---- Helper 4: regimes of the intercept (level in each period) ---------------
# أداة 4: الأنظمة: مستوى الثابت في كل فترة بين كسرين
regimes <- function(m, y) {
  path <- round(isatvar(m)[, "const.path"], 4)
  tt <- time(y)
  lab <- if (frequency(y) == 1) as.character(tt) else
    paste0(floor(tt + 1e-8), ifelse(frequency(y) == 12, "m", "q"),
           round((tt - floor(tt + 1e-8)) * frequency(y)) + 1)
  r <- rle(as.numeric(path))
  end <- cumsum(r$lengths); start <- end - r$lengths + 1
  data.frame(from = lab[start], to = lab[end], level = r$values, n_obs = r$lengths)
}

# ---- Helper 5: saturate a model you have ALREADY estimated with lm() ---------
# Equivalent of "regress ... ; indsat, super" in Stata: the regressors of YOUR
# model stay fixed in every search path; only the indicators are selected.
# أداة 5: تشبيع نموذج قدّرته مسبقًا بـ lm: متغيراتك تبقى ثابتة، والمؤشرات وحدها تُختار
saturate <- function(fit, end, frequency, ...) {
  y <- ts(model.response(model.frame(fit)), end = end, frequency = frequency)
  X <- model.matrix(fit)
  X <- X[, colnames(X) != "(Intercept)", drop = FALSE]
  X <- if (ncol(X) > 0) ts(X, end = end, frequency = frequency) else NULL
  m <- isat(y, mxreg = X, print.searchinfo = FALSE, plot = FALSE, ...)
  m$y_ts <- y
  m
}

# ---- Helper 6: original (OLS) versus robust (saturated) coefficients ---------
# أداة 6: مقارنة المعاملات الأصلية بالمعاملات بعد التشبع
compare <- function(fit, m) {
  b0 <- summary(fit)$coefficients
  rn <- setdiff(rownames(b0), "(Intercept)")
  rn <- rn[rn %in% names(coef(m))]
  data.frame(term = rn,
             b_original = round(b0[rn, 1], 4), se_original = round(b0[rn, 2], 4),
             b_saturated = round(coef(m)[rn], 4),
             se_saturated = round(sqrt(diag(vcov(m)))[rn], 4),
             change = round(coef(m)[rn] - b0[rn, 1], 4), row.names = NULL)
}


# -----------------------------------------------------------------------------
# PART 1. THEORY BEFORE DATA  /  النظرية قبل البيانات
# -----------------------------------------------------------------------------
# Saturation adds one indicator per observation and keeps the significant ones at
# the target size alpha. With NO outliers, about alpha*T are kept by chance
# (Hendry, Johansen & Santos 2008). IIS is a Huber-skip estimator (Johansen &
# Nielsen 2009): consistency factor xi for sigma, efficiency 1/eta^2 versus OLS.
# التشبع يضيف مؤشرًا لكل مشاهدة ويحتفظ بالمعنوي منها؛ وبلا قيم شاذة يُحتفظ بالصدفة بنحو alpha*T
gauge_theory <- function(T, alphas = c(0.05, 0.01, 0.005, 0.001)) {
  do.call(rbind, lapply(alphas, function(a) {
    c0 <- qnorm(1 - a / 2); psi <- 1 - a
    tau <- psi - 2 * c0 * dnorm(c0); rho <- 2 * c0 * dnorm(c0) / psi
    eta2 <- (1 / psi^2 + 2 * rho / psi) * tau + rho^2
    data.frame(T = T, alpha = a, critical_value = round(c0, 3),
               expected_false = a * T, P_none = round(dpois(0, a * T), 3),
               P_3_or_more = round(1 - ppois(2, a * T), 3),
               xi_sigma = round(sqrt(psi / tau), 4), efficiency = round(1 / eta2, 3))
  }))
}
print(gauge_theory(100))
# T = 100, alpha = 0.01: one false impulse expected; IIS keeps ~93% efficiency.
# Rule of thumb: alpha close to 1/T (smaller for steps and trends).
# القاعدة: alpha قريب من 1/T، وأصغر عند استخدام الدرجات والاتجاهات


# =============================================================================
# PART 2. NILE RIVER FLOW 1871-1970  /  نهر النيل
# =============================================================================
# --- A. DATA DICTIONARY / قاموس البيانات -------------------------------------
#  Variable | Role                       | English                          | العربية
#  Nile     | DEPENDENT (المتغير التابع) | annual flow at Aswan, 10^8 m^3   | التدفق السنوي لنهر النيل عند أسوان (100 مليون م3)
#  time     | TIME (متغير الزمن)         | calendar year 1871-1970          | السنة
#  Regressors / المتغيرات المستقلة: NONE (a "location model": y = constant + indicators)
#  لا توجد متغيرات مستقلة: نموذج موقع (ثابت + مؤشرات) لدراسة السلسلة نفسها
flow <- datasets::Nile

# --- B. LOOK AT THE DATA / النظر إلى البيانات ---------------------------------
print(summary(as.numeric(flow)))
save_png("01_nile_data.png", function()
  plot(flow, main = "Nile flow at Aswan, 1871-1970", ylab = "10^8 m^3", col = "steelblue", lwd = 2))

# --- C. BEFORE ESTIMATION: the series on its own / قبل التقدير: السلسلة بمفردها --
# With one variable, "before" and the model coincide: we saturate the flow itself.
# 1) IIS: impulses -> outliers                    النبضات للقيم الشاذة
nile_iis <- isat(flow, iis = TRUE, sis = FALSE, t.pval = 0.01, plot = FALSE)
# 2) SIS: steps -> level shifts                    الدرجات لتحولات المستوى
nile_sis <- isat(flow, iis = FALSE, sis = TRUE, t.pval = 0.01, plot = FALSE)
# 3) SUPER = IIS + SIS: both together (recommended default)   الاثنان معًا (الافتراضي الموصى به)
nile <- isat(flow, iis = TRUE, sis = TRUE, t.pval = 0.01, plot = FALSE)
print(nile)

# --- E. AFTER ESTIMATION: postestimation tools / أدوات ما بعد التقدير -----------
print(isatdates(nile))                            # dates and sizes           التواريخ والأحجام
print(regimes(nile, flow))                        # level in each regime      مستوى كل نظام
# A "regime" of one year (1879, 1913) is an impulse = an outlier, not a new level.
# النظام الذي طوله سنة واحدة (1879، 1913) هو قيمة شاذة وليس مستوى جديدًا
nile_tab <- breaks_table(nile); print(nile_tab)
to_excel(nile_tab, "Nile")
# Post-selection bias correction (Hendry & Krolzig 2005; Pretis 2018)   تصحيح التحيز بعد الاختيار
print(round(biascorr(b = coef(nile)[nile$ISnames],
                     b.se = sqrt(diag(vcov(nile)))[nile$ISnames],
                     p.alpha = 0.01, T = length(flow)), 1))
# Jiao-Pretis tests: more outliers than alpha*T? (run on an IIS model)
# اختبارات Jiao-Pretis: هل عدد القيم الشاذة أكبر مما تتوقعه الصدفة؟
nile_iis05 <- isat(flow, iis = TRUE, sis = FALSE, t.pval = 0.05, plot = FALSE, print.searchinfo = FALSE)
print(outliertest(nile_iis05))
print(distorttest(nile_iis05, coef = "all"))      # did the outliers change the mean?  هل غيّرت القيم الشاذة المتوسط؟
# Path test: in which years does the level differ from 1000?   اختبار المسار: متى يختلف المستوى عن 1000؟
save_png("02_nile_pathtest.png", function()
  isattest(nile, hnull = 1000, biascorr = TRUE, plot = TRUE))
save_png("03_nile_fit.png", function() plot(nile))
# OLS mean versus the saturated model   المتوسط العادي مقابل النموذج المشبَّع
cat("OLS mean of the whole sample:", round(mean(flow), 1), "\n")
# Forecast the next 5 years with the LAST regime   التنبؤ بالسنوات الخمس التالية بالنظام الأخير
print(predict(nile, n.ahead = 5, plot = FALSE))

# --- F. INTERPRETATION / التفسير ----------------------------------------------
# The mean flow falls by about 280 from 1899 (the first Aswan dam, 1898-1902):
# regime 1 (1871-1898) = 1088, last regime (1918-1970) = 852. 1879 and 1913 are
# outlying years. The OLS mean (919) represents neither regime. Bias correction
# shrinks the weak step of 1908 from 205.9 to 122.6 but leaves 1899 (t = -6.6) intact.
# ينخفض المتوسط بنحو 280 ابتداءً من 1899 (سد أسوان). المتوسط العادي 919 لا يمثل أيًّا من النظامين.
# Identical to Stata: indsat flow, super tpval(0.01)   النتائج مطابقة لمكتبة indsat في Stata


# =============================================================================
# PART 3. US LIFE EXPECTANCY 1900-1999  /  أمد الحياة في الولايات المتحدة
# =============================================================================
# --- A. DATA DICTIONARY / قاموس البيانات -------------------------------------
#  Variable  | Role                   | English                          | العربية
#  le        | DEPENDENT (التابع)     | life expectancy at birth, years  | العمر المتوقع عند الولادة بالسنوات
#  le_male   | DEPENDENT (2nd series) | life expectancy, males           | العمر المتوقع للذكور
#  le_female | DEPENDENT (3rd series) | life expectancy, females         | العمر المتوقع للإناث
#  year      | TIME and REGRESSOR     | calendar year (linear trend)     | السنة، وتُستخدم اتجاهًا زمنيًا خطيًا (متغير مستقل)
#  Regressors / المتغيرات المستقلة: a linear time trend (year) or the lag (AR(1) dynamics)
#  Source: National Vital Statistics Reports 50(6), Table 12, CDC (2002), public data.
#  https://www.cdc.gov/nchs/data/nvsr/nvsr50/nvsr50_06.pdf
life <- data.frame(
  year = 1900:1999,
  le = c(47.3, 49.1, 51.5, 50.5, 47.6, 48.7, 48.7, 47.6, 51.1, 52.1, 50, 52.6, 53.5, 52.5, 54.2, 54.5, 51.7,
         50.9, 39.1, 54.7, 54.1, 60.8, 59.6, 57.2, 59.7, 59, 56.7, 60.4, 56.8, 57.1, 59.7, 61.1, 62.1, 63.3,
         61.1, 61.7, 58.5, 60, 63.5, 63.7, 62.9, 64.8, 66.2, 63.3, 65.2, 65.9, 66.7, 66.8, 67.2, 68, 68.2,
         68.4, 68.6, 68.8, 69.6, 69.6, 69.7, 69.5, 69.6, 69.9, 69.7, 70.2, 70.1, 69.9, 70.2, 70.2, 70.2, 70.5,
         70.2, 70.5, 70.8, 71.1, 71.2, 71.4, 72, 72.6, 72.9, 73.3, 73.5, 73.9, 73.7, 74.1, 74.5, 74.6, 74.7,
         74.7, 74.7, 74.9, 74.9, 75.1, 75.4, 75.5, 75.8, 75.5, 75.7, 75.8, 76.1, 76.5, 76.7, 76.7),
  le_male = c(46.3, 47.6, 49.8, 49.1, 46.2, 47.3, 46.9, 45.6, 49.5, 50.5, 48.4, 50.9, 51.5, 50.3, 52, 52.5,
              49.6, 48.4, 36.6, 53.5, 53.6, 60, 58.4, 56.1, 58.1, 57.6, 55.5, 59, 55.6, 55.8, 58.1, 59.4, 61,
              61.7, 59.3, 59.9, 56.6, 58, 61.9, 62.1, 60.8, 63.1, 64.7, 62.4, 63.6, 63.6, 64.4, 64.4, 64.6,
              65.2, 65.6, 65.6, 65.8, 66, 66.7, 66.7, 66.7, 66.4, 66.6, 66.8, 66.6, 67.1, 66.9, 66.6, 66.8,
              66.8, 66.7, 67, 66.6, 66.8, 67.1, 67.4, 67.4, 67.6, 68.2, 68.8, 69.1, 69.5, 69.6, 70, 70, 70.4,
              70.8, 71, 71.1, 71.1, 71.2, 71.4, 71.4, 71.7, 71.8, 72, 72.3, 72.2, 72.4, 72.5, 73.1, 73.6,
              73.8, 73.9),
  le_female = c(48.3, 50.6, 53.4, 52, 49.1, 50.2, 50.8, 49.9, 52.8, 53.8, 51.8, 54.4, 55.9, 55, 56.8, 56.8,
                54.3, 54, 42.2, 56, 54.6, 61.8, 61, 58.5, 61.5, 60.6, 58, 62.1, 58.3, 58.7, 61.6, 63.1, 63.5,
                65.1, 63.3, 63.9, 60.6, 62.4, 65.3, 65.4, 65.2, 66.8, 67.9, 64.4, 66.8, 67.9, 69.4, 69.7, 69.9,
                70.7, 71.1, 71.4, 71.6, 72, 72.8, 72.8, 72.9, 72.7, 72.9, 73.2, 73.1, 73.6, 73.5, 73.4, 73.7,
                73.8, 73.9, 74.3, 74.1, 74.4, 74.7, 75, 75.1, 75.3, 75.9, 76.6, 76.8, 77.2, 77.3, 77.8, 77.4,
                77.8, 78.1, 78.1, 78.2, 78.2, 78.2, 78.3, 78.3, 78.5, 78.8, 78.9, 79.1, 78.8, 79, 78.9, 79.1,
                79.4, 79.5, 79.4))
le <- ts(life$le, start = 1900)

# --- B. LOOK AT THE DATA / النظر إلى البيانات ---------------------------------
print(summary(life[, -1]))
save_png("04_life_data.png", function() {
  matplot(life$year, life[, -1], type = "l", lty = 1, lwd = 2, col = c("black", "steelblue", "firebrick"),
          main = "US life expectancy at birth, 1900-1999", xlab = "year", ylab = "years")
  legend("bottomright", c("all", "male", "female"), col = c("black", "steelblue", "firebrick"), lwd = 2)
})

# --- C. BEFORE ESTIMATION: each series on its own / كل سلسلة بمفردها ---------
# C.1 A WRONG specification: a trending series around a constant only.
#     مواصفة خاطئة: سلسلة ذات اتجاه حول ثابت فقط
wrong <- isat(le, iis = TRUE, sis = FALSE, t.pval = 0.01, plot = FALSE, print.searchinfo = FALSE)
cat("Retained impulses in the WRONG model:", length(wrong$ISnames), "\n")
# Dozens of "outliers" = the omitted trend. LESSON: specify the model, then saturate.
# عشرات «القيم الشاذة» هي في الحقيقة الاتجاه المهمل. الدرس: حدّد النموذج أولًا ثم شبّعه

# C.2 Each series with its own dynamics (AR(1)) + impulses.  كل سلسلة مع ديناميكيتها
for (v in c("le", "le_male", "le_female")) {
  m <- isat(ts(life[[v]], start = 1900), ar = 1, iis = TRUE, sis = FALSE, t.pval = 0.01,
            plot = FALSE, print.searchinfo = FALSE)
  cat(sprintf("%-10s retained: %s\n", v, paste(m$ISnames, collapse = " ")))
}
# All three series show 1918 (influenza pandemic): a common shock to men and women
# (in an AR(1) model a one-off fall also appears as 1919, the bounce back).
# السلاسل الثلاث تُظهر 1918 (جائحة الإنفلونزا): صدمة مشتركة للذكور والإناث

# --- D. ESTIMATION: trend model / التقدير: نموذج الاتجاه ---------------------
life_ols <- lm(le ~ year, data = life)
print(summary(life_ols))

# --- E. AFTER ESTIMATION: saturate the trend model / تشبيع نموذج الاتجاه -----
# ULTRA = impulses + steps + broken trends (for trending series).
# التشبع الأقصى = نبضات + درجات + اتجاهات منكسرة (للسلاسل ذات الاتجاه)
life_sat <- saturate(life_ols, end = 1999, frequency = 1,
                     iis = TRUE, sis = TRUE, tis = TRUE, t.pval = 0.001)
print(life_sat)
print(compare(life_ols, life_sat))
life_tab <- breaks_table(life_sat); print(life_tab)
to_excel(life_tab, "LifeExpectancy")
save_png("05_life_fit.png", function() plot(life_sat))

# --- F. INTERPRETATION / التفسير ----------------------------------------------
# 1918: a fall of about 15 years (pandemic); 1921: a permanent step up; 1955: a
# broken trend of about -0.16 years per year: gains in life expectancy slow down.
# The trend slope rises from 0.30 to 0.35 years per year once the breaks are
# modelled, because the pandemic and the later slowdown pulled the OLS trend down.
# 1918 انخفاض بنحو 15 سنة؛ 1921 درجة صاعدة؛ 1955 تباطؤ نمو العمر المتوقع بنحو 0.16 سنة كل عام


# =============================================================================
# PART 4. UK ROAD CASUALTIES 1969-1984  /  ضحايا الطرق في بريطانيا
# =============================================================================
# --- A. DATA DICTIONARY / قاموس البيانات -------------------------------------
#  Variable        | Role                       | English                        | العربية
#  ldriverskilled  | DEPENDENT (التابع)         | log of car drivers killed      | لوغاريتم عدد السائقين القتلى شهريًا
#  lkms            | REGRESSOR (مستقل)          | log of distance driven         | لوغاريتم المسافة المقطوعة بالسيارات
#  lpetrol         | REGRESSOR (مستقل)          | log of real petrol price       | لوغاريتم السعر الحقيقي للبنزين
#  month2..month12 | CONTROLS (متغيرات ضابطة)   | 11 seasonal (monthly) dummies  | متغيرات وهمية للأشهر (الموسمية)
#  law             | KNOWN EVENT (للمقارنة)     | seat-belt law, 1 from 1983m2   | قانون حزام الأمان (1 من فبراير 1983)
#  time            | TIME                       | month 1969m1-1984m12           | الشهر
#  We do NOT put law in the model: we let saturation find the change by itself,
#  and use law only as an independent check.
#  لا نضع متغير القانون في النموذج: نترك التشبع يكتشف التغيّر بنفسه، ثم نقارن
SB <- datasets::Seatbelts
roads <- data.frame(ldriverskilled = log(as.numeric(SB[, "DriversKilled"])),
                    lkms = log(as.numeric(SB[, "kms"])),
                    lpetrol = log(as.numeric(SB[, "PetrolPrice"])),
                    month = factor(cycle(SB[, "DriversKilled"])),
                    law = as.numeric(SB[, "law"]))
months <- model.matrix(~ month, roads)[, -1]          # 11 dummies, January = base   يناير هو الشهر المرجعي
ts12 <- function(x) ts(x, start = c(1969, 1), frequency = 12)

# --- B. LOOK AT THE DATA / النظر إلى البيانات ---------------------------------
print(summary(roads[, c("ldriverskilled", "lkms", "lpetrol")]))
save_png("06_roads_data.png", function() {
  plot(ts12(roads$ldriverskilled), main = "Log car drivers killed (law: 1983m2)", ylab = "log", col = "steelblue")
  abline(v = 1983 + 1 / 12, lty = 2, col = "firebrick")
})

# --- C. BEFORE ESTIMATION: each variable on its own / كل متغير بمفرده --------
# Each series with seasonal dummies + super saturation: what happened to EACH variable?
# كل سلسلة مع المتغيرات الموسمية والتشبع الفائق: ماذا حدث لكل متغير؟
for (v in c("ldriverskilled", "lkms", "lpetrol")) {
  m <- isat(ts12(roads[[v]]), mxreg = ts12(months), iis = TRUE, sis = TRUE, t.pval = 0.005,
            plot = FALSE, print.searchinfo = FALSE)
  cat("\nVariable", v, "\n"); print(breaks_table(m))
}
# ldriverskilled: a step EXACTLY in 1983m2 (the seat-belt law), size -0.18 (about -16%),
#                 + an outlier in 1981m12.
# lpetrol: steps in 1974m2 and 1979m6 (the two oil shocks).
# lkms: shifts in traffic, including 1983m2.
# المتغير التابع: درجة بالضبط في 1983m2 (قانون الحزام). سعر البنزين: درجتا 1974m2 و1979m6 (صدمتا النفط)

# --- D. ESTIMATION: the researcher's usual regression / الانحدار المعتاد للباحث --
roads_ols <- lm(ldriverskilled ~ lkms + lpetrol + month, data = roads)
print(summary(roads_ols))

# --- E. AFTER ESTIMATION: saturate the model you estimated / تشبيع النموذج المقدَّر ---
# saturate() keeps lkms, lpetrol and the months in every path and searches the
# impulses and steps only. (One-line alternative without dates: isat(roads_ols, ...).)
# تبقى متغيراتك في كل المسارات، والبحث يجري على النبضات والدرجات فقط
roads_sat <- saturate(roads_ols, end = c(1984, 12), frequency = 12,
                      iis = TRUE, sis = TRUE, t.pval = 0.005)
print(roads_sat)                                    # includes AR, ARCH and normality diagnostics  يتضمن الاختبارات التشخيصية
print(compare(roads_ols, roads_sat)[1:2, ])
save_png("07_roads_fit.png", function() plot(roads_sat))

# E.2 Independent check with the KNOWN law dummy.  تحقق مستقل بمتغير القانون المعروف
print(coef(summary(lm(ldriverskilled ~ lkms + lpetrol + month + law, data = roads)))["law", ])

# E.3 Coefficient breaks (MIS): does the petrol effect change over time?
#     MIS = steps multiplied by the regressor, passed to isat() through uis.
#     كسور المعاملات: هل يتغير أثر سعر البنزين؟ MIS = الدرجات مضروبة في المتغير، تُمرَّر عبر uis
S <- sim(ts12(roads$lpetrol))                       # step indicators  مؤشرات الدرجة
MIS <- S * roads$lpetrol
colnames(MIS) <- sub("\\((\\d+)\\)$", "m\\1", sub("^sis", "mis.lpetrol", colnames(S)))  # mis.lpetrol1975m4
roads_mis <- isat(roads_sat$y_ts, mxreg = ts12(cbind(lkms = roads$lkms, lpetrol = roads$lpetrol, months)),
                  iis = TRUE, sis = TRUE, uis = MIS, t.pval = 0.005, plot = FALSE, print.searchinfo = FALSE)
roads_tab <- breaks_table(roads_mis); print(roads_tab)
# MIS keeps mis.lpetrol1975m4 (+0.057): the petrol elasticity moves from about -0.36
# to -0.30 in April 1975, the same date as the step sisApr 1975 of E. Because log
# petrol is almost constant, a level shift and a slope shift are nearly collinear:
# read them together, as one change in the petrol-casualties relation in 1975.
# MIS يجد تغيّرًا في معامل سعر البنزين في أبريل 1975، وهو تاريخ الدرجة نفسها: اقرأهما معًا
to_excel(breaks_table(roads_sat), "RoadCasualties")
to_excel(roads_tab, "RoadCasualties_MIS")

# --- F. INTERPRETATION / التفسير ----------------------------------------------
# Before estimation the fatalities series shifts exactly at the law (1983m2).
# In the regression the shift is dated 1983m7 because traffic and petrol prices
# explain part of the fall. The law dummy gives -0.15 (about -14%).
# The petrol elasticity falls from -0.54 to -0.33 once breaks are modelled: the
# original regression attributed part of the level shifts to petrol prices.
# قبل التقدير ينكسر المتغير التابع في 1983m2 تمامًا؛ وبعد إدخال المتغيرات المستقلة يُؤرَّخ الكسر 1983m7
# لأن الحركة المرورية والأسعار تفسر جزءًا من الانخفاض. ومرونة سعر البنزين تنخفض من 0.54- إلى 0.33-


# =============================================================================
# PART 5. UK CONSUMPTION FUNCTION (DHSY 1978)  /  دالة الاستهلاك البريطانية
# =============================================================================
# --- A. DATA DICTIONARY / قاموس البيانات -------------------------------------
#  Variable | Role                | English                                   | العربية
#  c        | DEPENDENT (التابع)  | log real non-durable consumption          | لوغاريتم الاستهلاك الحقيقي غير المعمّر
#  y        | REGRESSOR (مستقل)   | log real personal disposable income       | لوغاريتم الدخل الشخصي المتاح الحقيقي
#  D4p      | REGRESSOR (مستقل)   | annual inflation (4th diff. of log prices) | التضخم السنوي
#  D6812    | KNOWN EVENT         | budget dummy +1 1968q1, -1 1968q2         | متغير ميزانية 1968 (+1 ثم -1)
#  D7312    | KNOWN EVENT         | VAT dummy +1 1973q1, -1 1973q2            | متغير ضريبة القيمة المضافة 1973
#  time     | TIME                | quarter 1957q1-1976q2                     | الربع
#  The data are a Stata file (.dta), read with haven.  البيانات ملف Stata يُقرأ بالحزمة haven
f <- "indsat_dhsy.dta"
if (!file.exists(f)) download.file(paste0(gh, f), f, mode = "wb")
dhsy <- as.data.frame(haven::read_dta(f))
D <- ts(dhsy[, c("c", "y", "D4p", "D6812", "D7312")], start = c(1957, 1), frequency = 4)
D <- window(D, start = c(1958, 1))                  # D4p starts in 1958q1  التضخم يبدأ في الربع الأول 1958
D4c <- diff(D[, "c"], lag = 4); D4y <- diff(D[, "y"], lag = 4)

# --- B. LOOK AT THE DATA / النظر إلى البيانات ---------------------------------
print(summary(D[, c("c", "y", "D4p")]))
save_png("08_dhsy_data.png", function() {
  ts.plot(D4c, D4y, D[, "D4p"], col = c("black", "steelblue", "firebrick"), lwd = 2,
          main = "Annual growth of consumption, income and prices")
  legend("topleft", c("D4c", "D4y", "D4p"), col = c("black", "steelblue", "firebrick"), lwd = 2)
})

# --- C. BEFORE ESTIMATION: each variable on its own / كل متغير بمفرده --------
# Levels trend upwards, so we use growth rates (or ultra with a trend).
# المستويات ذات اتجاه، لذا نستخدم معدلات النمو
for (v in list(D4c = D4c, D4y = D4y, D4p = D[, "D4p"])) {
  m <- isat(v, iis = TRUE, sis = TRUE, t.pval = 0.01, plot = FALSE, print.searchinfo = FALSE)
  cat("super saturation, retained:", m$ISnames, "\n")
}
# A RUN of impulses (inflation 1974-1976) is the signature of a level shift ->
# use SIS for this variable.  سلسلة نبضات متتالية في التضخم = علامة تحول مستوى، فنستخدم SIS
infl <- isat(D[, "D4p"], iis = FALSE, sis = TRUE, t.pval = 0.01, plot = FALSE, print.searchinfo = FALSE)
print(regimes(infl, D[, "D4p"]))                    # inflation regimes  أنظمة التضخم

# --- D. ESTIMATION: the researcher's usual ARDL / نموذج ARDL المعتاد ---------
ardl0 <- ardl(c ~ y + D4p, data = D, order = c(2, 2, 1))
print(summary(ardl0))
print(multipliers(ardl0))                           # long-run coefficients  المعاملات طويلة الأجل
print(bounds_f_test(ardl0, case = 3))               # PSS bounds test  اختبار الحدود

# --- E. AFTER ESTIMATION: saturate the ARDL / تشبيع نموذج ARDL ---------------
# E.1 Search the indicators with every ARDL term fixed.  البحث في المؤشرات مع تثبيت حدود ARDL
ardl_sat <- saturate(ardl0, end = c(1976, 2), frequency = 4, iis = FALSE, sis = TRUE, t.pval = 0.01)
print(ardl_sat)
dhsy_tab <- breaks_table(ardl_sat); print(dhsy_tab)
to_excel(dhsy_tab, "DHSY")

# E.2 Put the retained steps back into the ARDL as UNRESTRICTED terms (after "|"),
#     then compare long run, adjustment speed and the bounds test.
#     نعيد الدرجات المحتفظ بها إلى ARDL كحدود غير مقيدة ثم نقارن الأجل الطويل وسرعة التعديل واختبار الحدود
steps <- sim(D[, "c"])
keep <- sub(" ", "", ardl_sat$ISnames)                      # e.g. "sis1966Q2"
colnames(steps) <- sub("\\((\\d)\\)$", "Q\\1", colnames(steps))   # "sis1966(2)" -> "sis1966Q2"
D_sat <- cbind(D, ts(as.matrix(steps)[, keep, drop = FALSE], start = start(D), frequency = 4))
colnames(D_sat) <- c(colnames(D), keep)
ardl1 <- ardl(as.formula(paste("c ~ y + D4p |", paste(keep, collapse = " + "))),
              data = D_sat, order = c(2, 2, 1))
speed <- function(mod) unname(coef(uecm(mod))[2])           # coefficient of L(c,1) in the ECM  سرعة التعديل
lr <- function(mod) { mu <- multipliers(mod); setNames(mu$Estimate, mu$Term) }
dhsy_cmp <- data.frame(
  model = c("ARDL(2,2,1)", "ARDL(2,2,1) + steps"),
  adjustment_speed = round(c(speed(ardl0), speed(ardl1)), 3),
  longrun_income = round(c(lr(ardl0)["y"], lr(ardl1)["y"]), 3),
  longrun_inflation = round(c(lr(ardl0)["D4p"], lr(ardl1)["D4p"]), 3),
  bounds_F = round(c(bounds_f_test(ardl0, case = 3)$statistic, bounds_f_test(ardl1, case = 3)$statistic), 2))
print(dhsy_cmp)
to_excel(dhsy_cmp, "DHSY_compare")

# E.3 Automatic lag selection (BIC), then super saturation.  اختيار الفجوات آليًا ثم التشبع الفائق
auto <- auto_ardl(c ~ y + D4p, data = D, max_order = 4, selection = "BIC")
print(auto$best_order)
auto_sat <- saturate(auto$best_model, end = c(1976, 2), frequency = 4,
                     iis = TRUE, sis = TRUE, t.pval = 0.01)
lag_c <- grep("^L\\(c", names(coef(auto_sat)), value = TRUE)
cat("Adjustment speed, automatic lags: before", round(speed(auto$best_model), 3),
    " after", round(sum(coef(auto_sat)[lag_c]) - 1, 3), "\n")

# --- F. INTERPRETATION / التفسير ----------------------------------------------
# ARDL(2,2,1): steps in 1966q2 and 1972q1; adjustment speed -1.36 -> -1.53;
# long-run income elasticity 0.81 -> 0.76; the bounds F rises from 17.7 to 27.4,
# rejecting "no level relationship" at 1%. With automatic lags (BIC) the adjustment
# speed moves from -0.36 to -0.41: ignoring shifts understates error correction.
# (Stata gives the same dates; small differences in F come from sample handling.)
# يرفض اختبار الحدود عدم وجود علاقة طويلة الأجل؛ وتزداد سرعة التعديل عند نمذجة الكسور


# =============================================================================
# PART 6. ROBUSTNESS  /  المتانة
# =============================================================================
# 6.1 Stability across target sizes (Nile): isatloop + outlier scaling tests.
#     الاستقرار عبر مستويات الدلالة
loop <- isatloop(num = 10:1, t.pval.spec = FALSE, y = flow, iis = TRUE, sis = FALSE, print = FALSE)
print(outlierscaletest(loop))
for (a in c(0.05, 0.01, 0.001)) {                  # do the big dates survive?  هل تبقى التواريخ الكبيرة؟
  m <- isat(flow, iis = TRUE, sis = TRUE, t.pval = a, plot = FALSE, print.searchinfo = FALSE)
  cat("alpha =", a, ":", m$ISnames, "\n")
}

# 6.2 Monte Carlo: how often does SIS find a shift of a given size (T = 100)?
#     محاكاة: كم مرة يكتشف SIS تحولًا بحجم معين؟ (gauge = الزائف، potency = القوة)
mc <- function(size, reps = 40, T = 100, tau = 51, alpha = 0.01) {
  res <- t(replicate(reps, {
    y <- rnorm(T) + size * (seq_len(T) >= tau)
    m <- isat(y, iis = FALSE, sis = TRUE, t.pval = alpha, plot = FALSE, print.searchinfo = FALSE)
    dates <- as.numeric(sub("sis", "", m$ISnames))
    hit <- any(abs(dates - tau) <= 2)
    c(potency = hit, false = sum(abs(dates - tau) > 2))
  }))
  data.frame(size = size, potency = mean(res[, "potency"]), gauge = mean(res[, "false"]) / (T - 1))
}
mc_res <- do.call(rbind, lapply(0:3, mc))
mc_res$potency[mc_res$size == 0] <- NA              # no true break when size = 0  لا يوجد كسر حقيقي
print(mc_res)
to_excel(mc_res, "MonteCarlo")
# Potency rises with the size of the shift (about 0.6 at 1 sigma, 0.9 at 2, 1.0 at 3).
# The SIS gauge is about 1-2% at alpha = 0.01: larger and more variable than for IIS
# (Nielsen & Qian 2025), which is why a small alpha is advised for steps.
# القوة تزداد مع حجم الكسر؛ ومقياس SIS أكبر قليلًا من alpha، لذا يُنصح بـ alpha صغير للدرجات


# =============================================================================
# PART 7. CHECKLIST FOR YOUR PAPER  /  قائمة التحقق لورقتك البحثية
# =============================================================================
#  1. Write the data dictionary: dependent variable, regressors, units, sources.
#     اكتب قاموس البيانات: المتغير التابع، المستقلة، الوحدات، المصادر
#  2. BEFORE estimation: saturate each variable (with its trend/seasonals) to know
#     the events in each series.   قبل التقدير: شبّع كل متغير لمعرفة أحداثه
#  3. Specify the economic model (trend, lags, seasonals), then saturate it
#     (saturate() after lm / ardl, or isat(y, mxreg = X)).   حدّد النموذج ثم شبّعه
#  4. alpha close to 1/T (smaller for SIS/TIS); justify with gauge_theory().
#  5. iis + sis by default; add tis for trending series; uis = steps * x for slope breaks.
#  6. Report dates and regimes (isatdates, regimes), bias-corrected sizes (biascorr),
#     diagnostics (print), outlier tests (outliertest, distorttest), and the comparison
#     of original vs robust coefficients (compare).
#  7. Robustness: isatloop over alpha; results with and without saturation.
#  8. Interpret every date with real events (policies, crises, laws, shocks).
#     فسّر كل تاريخ بأحداث حقيقية
#  9. Cite Hendry, Johansen & Santos (2008); Castle et al. (2015); Pretis, Reade &
#     Sucarrat (2018, gets); and indsat (github.com/merwanroudane/indsat) for Stata.

openxlsx::saveWorkbook(wb, file.path(out, "indsat_tables_R.xlsx"), overwrite = TRUE)
cat(strrep("-", 70), "\n",
    "Guide finished. Outputs are in the folder: ", out, "\n",
    "  - indsat_tables_R.xlsx  break tables (one sheet per example)\n",
    "  - *.png                 data, fitted models, path test\n", strrep("-", 70), "\n", sep = "")
