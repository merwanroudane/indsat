# =============================================================================
#  indsat_simple.R  --  Indicator saturation in R, step by step (for beginners)
#  تشبع المؤشرات في R خطوة بخطوة (للمبتدئين)
#
#  Dr Merwan Roudane  |  merwanroudane920@gmail.com  |  github.com/merwanroudane/indsat
#
#  YOU NEED TWO FILES IN THE SAME FOLDER / تحتاج ملفين في نفس المجلد:
#     indsat_simple.R     (this script / هذا السكريبت)
#     indsat_data.xlsx    (the data / البيانات: ورقة لكل مثال، وورقة README تشرح المتغيرات)
#
#  HOW TO RUN / طريقة التشغيل:
#     In RStudio: Session > Set Working Directory > To Source File Location,
#     then run the lines one by one with Ctrl+Enter.
#     في RStudio: اجعل مجلد العمل هو مجلد هذا الملف، ثم شغّل الأسطر واحدًا واحدًا بـ Ctrl+Enter
#
#  THE ONE FUNCTION YOU NEED / الدالة الوحيدة التي تحتاجها:
#     isat(y, mxreg = X, iis = TRUE, sis = TRUE, tis = FALSE, t.pval = 0.01)
#       y       the dependent variable (a time series)       المتغير التابع (سلسلة زمنية)
#       mxreg   the independent variables (optional)         المتغيرات المستقلة (اختياري)
#       iis     impulses  -> outliers                        النبضات: القيم الشاذة
#       sis     steps     -> level shifts                    الدرجات: تحولات المستوى
#       tis     trends    -> changes in the slope            الاتجاهات: تغيّر الميل
#       t.pval  significance level, choose about 1/T         مستوى الدلالة، اختره قريبًا من 1/عدد المشاهدات
# =============================================================================


# -----------------------------------------------------------------------------
# STEP 0. Packages / الحزم   (install only the first time / التثبيت مرة واحدة فقط)
# -----------------------------------------------------------------------------
# install.packages(c("gets", "readxl"))
library(gets)     # indicator saturation: isat()      تشبع المؤشرات
library(readxl)   # read Excel files: read_excel()     قراءة ملفات Excel
Sys.setlocale("LC_TIME", "C")   # English month names in the results (Feb, not févr.)
                                # أسماء الأشهر بالإنجليزية في النتائج
# Note: while isat() runs it prints lines such as "IIS block 1 of 4 ... Searching":
# this is only the progress of the search.  هذه الأسطر تُظهر تقدّم البحث فقط

file <- "indsat_data.xlsx"
excel_sheets(file)          # the sheets of the Excel file   أوراق ملف Excel


# =============================================================================
# EXAMPLE 1. NILE RIVER 1871-1970: ONE VARIABLE, NO REGRESSORS
# المثال 1: نهر النيل، متغير واحد بلا متغيرات مستقلة
# =============================================================================
nile <- read_excel(file, sheet = "Nile")
head(nile)

# Make a time series: first year 1871, one observation per year.
# نحوّل العمود إلى سلسلة زمنية تبدأ في 1871 بمشاهدة واحدة كل سنة
flow <- ts(nile$flow, start = 1871, frequency = 1)
plot(flow, main = "Nile flow", ylab = "10^8 m^3")

# Saturation with impulses AND steps (the safe default).
# التشبع بالنبضات والدرجات معًا (الخيار الآمن)
m1 <- isat(flow, iis = TRUE, sis = TRUE, t.pval = 0.01)
m1                 # full results / النتائج كاملة
isatdates(m1)      # dates and sizes of the breaks / تواريخ الكسور وأحجامها
plot(m1)           # data, fitted path and residuals / البيانات والمسار المقدَّر والبواقي

# READING THE RESULT / قراءة النتيجة:
#   sis1899 = -280.6  -> from 1899 the average flow falls by about 280
#                        (the first Aswan dam).  ابتداءً من 1899 ينخفض المتوسط بنحو 280 (سد أسوان)
#   iis1879, iis1913  -> two outlying years.     سنتان شاذتان
#   (smaller steps 1908-1918 move the level for a few years only)


# =============================================================================
# EXAMPLE 2. US LIFE EXPECTANCY 1900-1999: A VARIABLE WITH A TREND
# المثال 2: أمد الحياة في الولايات المتحدة، متغير له اتجاه زمني
# =============================================================================
life <- read_excel(file, sheet = "LifeExpectancy")
le    <- ts(life$le,   start = 1900)        # dependent variable / المتغير التابع
trend <- ts(life$year, start = 1900)        # time trend / الاتجاه الزمني
plot(le, main = "US life expectancy", ylab = "years")

# MISTAKE TO AVOID: forgetting the trend.  خطأ يجب تجنبه: نسيان الاتجاه
wrong <- isat(le, iis = TRUE, sis = FALSE, t.pval = 0.01)
length(wrong$ISnames)   # 25 "outliers": they only imitate the forgotten trend
                        # 25 «قيمة شاذة» تقلّد الاتجاه المنسي فقط

# CORRECT: put the trend in the model, then saturate (impulses, steps, trends).
# الصحيح: نضع الاتجاه في النموذج ثم نشبّعه
m2 <- isat(le, mxreg = trend, iis = TRUE, sis = TRUE, tis = TRUE, t.pval = 0.001)
m2
isatdates(m2)
plot(m2)
# iis1918 = -15  -> life expectancy fell by 15 years in 1918 (influenza pandemic)
# sis1921        -> a permanent step up from 1921
# tis1955        -> from 1955 the gains slow down (slope -0.16 per year)
# 1918 انخفاض 15 سنة (الجائحة)؛ 1921 درجة صاعدة؛ 1955 تباطؤ تحسّن العمر المتوقع


# =============================================================================
# EXAMPLE 3. UK ROAD CASUALTIES 1969-1984: A REGRESSION
# المثال 3: ضحايا الطرق في بريطانيا، انحدار بمتغيرات مستقلة
#   dependent   : log of drivers killed           التابع: لوغاريتم السائقين القتلى
#   independent : log of distance, log of petrol price, months
#                 المستقلة: لوغاريتم المسافة، لوغاريتم سعر البنزين، الأشهر
# =============================================================================
road <- read_excel(file, sheet = "RoadCasualties")

# Monthly time series starting in January 1969.  سلاسل شهرية تبدأ في يناير 1969
ldrivers <- ts(log(road$drivers_killed), start = c(1969, 1), frequency = 12)
lkms     <- log(road$kms)
lpetrol  <- log(road$petrol_price)
months   <- model.matrix(~ factor(road$month))[, -1]   # 11 month dummies (January = base)
colnames(months) <- paste0("month", 2:12)
months   <- ts(months, start = c(1969, 1), frequency = 12)
# IMPORTANT: in isat(), the independent variables must be time series with the
# SAME dates as y.  مهم: المتغيرات المستقلة يجب أن تكون سلاسل زمنية بنفس تواريخ y
plot(ldrivers, main = "Log drivers killed (seat-belt law: Feb 1983)")

# STEP C. BEFORE estimation: the dependent variable on its own (with months).
# قبل التقدير: المتغير التابع بمفرده (مع الأشهر)
m3a <- isat(ldrivers, mxreg = months, iis = TRUE, sis = TRUE, t.pval = 0.005)
isatdates(m3a)
# sisFeb 1983 = -0.18 -> deaths fall by about 16% exactly when the seat-belt law starts.
# انخفاض بنحو 16% بالضبط عند بدء قانون حزام الأمان (فبراير 1983)

# STEP D. The usual regression (without saturation).  الانحدار المعتاد دون تشبع
X <- ts(cbind(lkms, lpetrol, months), start = c(1969, 1), frequency = 12)
colnames(X) <- c("lkms", "lpetrol", paste0("month", 2:12))
ols <- lm(ldrivers ~ X)
summary(ols)

# STEP E. AFTER estimation: the SAME regression + saturation.
# Your regressors (X) are always kept; only the indicators are selected.
# بعد التقدير: نفس الانحدار مع التشبع؛ متغيراتك تبقى دائمًا والمؤشرات وحدها تُختار
m3 <- isat(ldrivers, mxreg = X, iis = TRUE, sis = TRUE, t.pval = 0.005)
m3
isatdates(m3)

# Compare the coefficients before and after.  مقارنة المعاملات قبل التشبع وبعده
cbind(before = coef(ols)[c("Xlkms", "Xlpetrol")],
      after  = coef(m3)[c("lkms", "lpetrol")])
# The petrol elasticity falls from -0.54 to -0.33: the plain regression gave the
# petrol price part of the effect of the level shifts (including the law).
# مرونة سعر البنزين تنخفض من 0.54- إلى 0.33-: الانحدار العادي نسب إلى السعر جزءًا من أثر الكسور


# =============================================================================
# EXAMPLE 4. UK CONSUMPTION 1957-1976: A DYNAMIC (ARDL) MODEL
# المثال 4: الاستهلاك البريطاني، نموذج ديناميكي (ARDL)
#   dependent   : c  = log consumption                     التابع: لوغاريتم الاستهلاك
#   independent : y  = log income, D4p = inflation, and lags of c, y, D4p
#                 المستقلة: لوغاريتم الدخل، التضخم، وفجواتها الزمنية
# =============================================================================
cons <- read_excel(file, sheet = "Consumption")

# A small helper to create a lag (the value k periods before).
# دالة صغيرة لإنشاء فجوة زمنية (قيمة المتغير قبل k فترات)
lagk <- function(x, k) c(rep(NA, k), head(x, -k))

cons$c_1   <- lagk(cons$c, 1);   cons$c_2 <- lagk(cons$c, 2)
cons$y_1   <- lagk(cons$y, 1);   cons$y_2 <- lagk(cons$y, 2)
cons$D4p_1 <- lagk(cons$D4p, 1)
cons <- na.omit(cons)                     # drop the first rows with missing lags  حذف الصفوف الناقصة
start <- c(cons$year[1], cons$quarter[1]) # first complete quarter  أول ربع كامل
start

cq <- ts(cons$c, start = start, frequency = 4)
Xc <- ts(cbind(c_1 = cons$c_1, c_2 = cons$c_2, y = cons$y, y_1 = cons$y_1, y_2 = cons$y_2,
               D4p = cons$D4p, D4p_1 = cons$D4p_1), start = start, frequency = 4)

# STEP D. The usual ARDL(2,2,1) by OLS.  نموذج ARDL المعتاد
ardl0 <- lm(cq ~ Xc)
# STEP E. The same ARDL + step saturation.  نفس النموذج مع تشبع الدرجات
m4 <- isat(cq, mxreg = Xc, iis = FALSE, sis = TRUE, t.pval = 0.01)
isatdates(m4)
# sis1966 Q2 and sis1972 Q1: two level shifts in consumption.  تحولان في مستوى الاستهلاك

# Speed of adjustment = (coef of c_1 + coef of c_2) - 1.  سرعة التعديل نحو التوازن
b0 <- coef(ardl0); b1 <- coef(m4)
c(before = unname(b0["Xcc_1"] + b0["Xcc_2"] - 1),
  after  = unname(b1["c_1"] + b1["c_2"] - 1))
# -1.37 -> -1.54: modelling the shifts makes the error correction stronger.
# سرعة التعديل تزداد بعد نمذجة الكسور
# (The bounds test for ARDL is in the advanced script, folder "advanced".)


# =============================================================================
# EXTRA. ARE THE OUTLIERS REAL? (Jiao-Pretis test) / هل القيم الشاذة حقيقية؟
# =============================================================================
# With no outliers at all, about alpha * T impulses are kept by chance.
# This test checks whether we found MORE than chance would give.
# حتى بلا قيم شاذة يُحتفظ بالصدفة بنحو alpha*T نبضة؛ الاختبار يقارن ما وجدناه بما تعطيه الصدفة
m5 <- isat(flow, iis = TRUE, sis = FALSE, t.pval = 0.05)
outliertest(m5)
# p-value > 0.05: the impulses of the Nile are compatible with chance;
# the real story of the Nile is the level shift of 1899, not outliers.
# القيمة الاحتمالية أكبر من 0.05: نبضات النيل متوافقة مع الصدفة؛ الحدث الحقيقي هو تحول المستوى 1899


# =============================================================================
# SAVE THE BREAK TABLES TO CSV (open them in Excel) / حفظ جداول الكسور
# =============================================================================
write.csv(isatdates(m1)$sis, "nile_steps.csv", row.names = FALSE)
write.csv(isatdates(m3)$sis, "roads_steps.csv", row.names = FALSE)
# isatdates() gives $iis (impulses), $sis (steps) and $tis (trends).
# isatdates تعطي النبضات والدرجات والاتجاهات كلًّا في جدول
