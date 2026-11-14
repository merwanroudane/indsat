* =============================================================================
*  indsat_guide.do  --  A COMPLETE GUIDE FOR RESEARCHERS (REAL DATA)
*  دليل الباحث الكامل لمكتبة indsat: تشبع المؤشرات ببيانات حقيقية
*
*  Dr Merwan Roudane  |  merwanroudane920@gmail.com  |  github.com/merwanroudane/indsat
*
*  EVERY EXAMPLE FOLLOWS THE SAME SIX STEPS   /   كل مثال يتبع نفس الخطوات الست
*    A. Data dictionary: dependent variable, regressors, units      قاموس البيانات: التابع والمستقلة والوحدات
*    B. Look at the data (describe, summarize, graph)               النظر إلى البيانات
*    C. BEFORE estimation: saturate each variable on its own         قبل التقدير: تشبيع كل متغير بمفرده
*       -> outliers and breaks in each series                        القيم الشاذة والكسور في كل سلسلة
*    D. Estimation: the economic model                               التقدير: النموذج الاقتصادي
*    E. AFTER estimation: saturate the estimated model               بعد التقدير: تشبيع النموذج المقدَّر
*       -> robust coefficients, break dates, tests, graphs           معاملات قوية، تواريخ الكسور، اختبارات، رسوم
*    F. Interpretation                                               التفسير
*
*  CONTENTS / المحتويات
*    PART 0  Setup                                                   الإعداد
*    PART 1  Theory before data                                      النظرية قبل البيانات
*    PART 2  Nile river flow       (one variable, no regressors)     نهر النيل: متغير واحد بلا متغيرات مستقلة
*    PART 3  US life expectancy    (one variable + time trend)       أمد الحياة: متغير واحد مع اتجاه زمني
*    PART 4  UK road casualties    (regression with regressors)      ضحايا الطرق: انحدار بمتغيرات مستقلة
*    PART 5  UK consumption (DHSY) (ARDL + bounds test)              الاستهلاك البريطاني: ARDL واختبار الحدود
*    PART 6  Robustness                                              المتانة
*    PART 7  Checklist for your paper                                قائمة التحقق لورقتك
*
*  Outputs / المخرجات: folder indsat_guide_output (log, PNG graphs, Excel tables).
*  Run time about 4-5 minutes.  مدة التشغيل من 4 إلى 5 دقائق تقريبًا
* =============================================================================

version 14.0
clear
set more off
set linesize 120
capture log close
local out "indsat_guide_output"
capture mkdir "`out'"
log using "`out'/indsat_guide.log", replace text

* -----------------------------------------------------------------------------
* PART 0. SETUP  /  الإعداد
* -----------------------------------------------------------------------------
* The data are Stata files (.dta), NOT Excel and NOT inside this do-file.
* Put indsat_nile.dta, indsat_seatbelts.dta and indsat_dhsy.dta in the working
* directory (cd), or let the lines below download them from GitHub.
* US life expectancy is built into Stata (sysuse uslifeexp): no file needed.
* البيانات ملفات Stata بصيغة dta وليست Excel ولا داخل هذا الملف. ضع الملفات الثلاثة في مجلد العمل
* أو دع الأوامر التالية تنزّلها من GitHub. بيانات أمد الحياة مدمجة في Stata.
local gh "https://raw.githubusercontent.com/merwanroudane/indsat/main/"
* If the library files sit in the folder indsat_package next to this do-file,
* use them directly (no internet needed).
* إذا كانت ملفات المكتبة في المجلد indsat_package بجانب هذا الملف فستُستخدم مباشرة دون إنترنت
capture confirm file "indsat_package/indsat.ado"
if !_rc adopath ++ "`c(pwd)'/indsat_package"
capture which indsat
if _rc {
    net install indsat, from("`gh'") replace
}
capture confirm file indsat_nile.dta
if _rc {
    net get indsat, from("`gh'") replace
}
capture which ardl
if _rc {
    ssc install ardl, replace
}

* Helper 1: save any named graph as PNG (works in the GUI and in batch mode).
* أداة 1: حفظ الرسوم بصيغة PNG
capture program drop guide_png
program define guide_png
    args gname fname
    capture graph display `gname'
    if (_rc == 0) quietly graph export "`fname'", replace width(1600)
end

* Helper 2: write the table of retained indicators (e(breaks)) to Excel, one
* sheet per example, with readable columns for your paper.
* أداة 2: حفظ جدول المؤشرات المحتفظ بها في Excel
capture program drop guide_xls
program define guide_xls
    args file sheet mode
    if (e(nret) == 0) exit
    tempname B
    matrix `B' = e(breaks)
    local rn : rownames `B'
    local tf "`e(tsfmt)'"
    preserve
    quietly {
        clear
        svmat double `B', names(col)
        generate str32 indicator = ""
        local i 0
        foreach r of local rn {
            local ++i
            replace indicator = "`r'" in `i'
        }
        generate str16 date = string(time, "`tf'")
        label define guide_ty 1 "IIS" 2 "SIS" 3 "TIS" 4 "MIS" 5 "UIS" 6 "BIS" 7 "QIS" 8 "CIS" 9 "DIS" 10 "PIS", replace
        label values type guide_ty
        decode type, generate(kind)
        drop type obs time
        order indicator kind date coef se t p
        format coef se t p %9.4f
    }
    if ("`mode'" == "new") export excel using "`file'", sheet("`sheet'") firstrow(variables) replace
    else export excel using "`file'", sheet("`sheet'") firstrow(variables) sheetreplace
    restore
end

* The library has ONE central command; typing it alone shows the menu.
* للمكتبة أمر مركزي واحد وكتابته وحده تعرض القائمة
indsat menu
* Help:  help indsat  |  help indsat_types (which type, when)  |  help indsat_methods


* -----------------------------------------------------------------------------
* PART 1. THEORY BEFORE DATA  /  النظرية قبل البيانات
* -----------------------------------------------------------------------------
* Saturation adds one indicator per observation and keeps the significant ones at
* the target size alpha. With NO outliers, about alpha*T are kept by chance.
* التشبع يضيف مؤشرًا لكل مشاهدة ويحتفظ بالمعنوي منها؛ وبلا قيم شاذة يُحتفظ بالصدفة بنحو alpha*T
indsat gauge, t(100)
* T = 100, alpha = 0.01: one false impulse expected; IIS keeps ~93% efficiency.
* Rule of thumb: alpha close to 1/T (smaller for steps and trends).


* =============================================================================
* PART 2. NILE RIVER FLOW 1871-1970  /  نهر النيل
* =============================================================================
* --- A. DATA DICTIONARY / قاموس البيانات -------------------------------------
*  Variable | Role                       | English                          | العربية
*  flow     | DEPENDENT (المتغير التابع) | annual flow at Aswan, 10^8 m^3   | التدفق السنوي لنهر النيل عند أسوان (100 مليون م3)
*  year     | TIME (متغير الزمن)         | calendar year 1871-1970          | السنة
*  Regressors / المتغيرات المستقلة: NONE (a "location model": y = constant + indicators)
*  لا توجد متغيرات مستقلة: نموذج موقع (ثابت + مؤشرات) لدراسة السلسلة نفسها
use indsat_nile, clear
label variable flow "annual Nile flow at Aswan (10^8 m^3)"
tsset year

* --- B. LOOK AT THE DATA / النظر إلى البيانات ---------------------------------
describe
summarize flow
tsline flow, title("Nile flow at Aswan, 1871-1970") ytitle("10^8 m^3") ///
    graphregion(color(white)) name(nile_raw, replace)
guide_png nile_raw "`out'/01_nile_data.png"

* --- C. BEFORE ESTIMATION: the series on its own / قبل التقدير: السلسلة بمفردها --
* With one variable, "before" and the model coincide: we saturate flow itself.
* 1) IIS: impulses -> outliers                    النبضات للقيم الشاذة
indsat flow, iis tpval(0.01)
* 2) SIS: steps -> level shifts                    الدرجات لتحولات المستوى
indsat flow, sis tpval(0.01)
* 3) SUPER = IIS + SIS: both together (recommended default)   الاثنان معًا (الافتراضي الموصى به)
indsat flow, super tpval(0.01)

* --- E. AFTER ESTIMATION: postestimation tools / أدوات ما بعد التقدير -----------
indsat dates                      // dates, sizes, REGIMES (level in each regime)  التواريخ والأنظمة
indsat biascorr                   // post-selection bias correction                 تصحيح التحيز
indsat outlier                    // Jiao-Pretis: more outliers than alpha*T?       اختبار وجود قيم شاذة
indsat diag                       // AR, ARCH, normality, RESET tests              اختبارات التشخيص
indsat test, hnull(1000) biascorr graph name(nile_test)
guide_png nile_test "`out'/02_nile_pathtest.png"
indsat plot, name(nile_dash)
guide_png nile_dash "`out'/03_nile_dashboard.png"
guide_xls "`out'/indsat_tables.xlsx" "Nile" new
estimates store nile_sat
quietly regress flow
estimates store nile_ols
estimates table nile_ols nile_sat, b(%9.2f) se stats(N r2) title("OLS mean vs saturated model")
estimates restore nile_sat
indsat forecast, h(5) graph name(nile_fc)
guide_png nile_fc "`out'/04_nile_forecast.png"

* --- F. INTERPRETATION / التفسير ----------------------------------------------
* The mean flow falls by about 280 from 1899 (the first Aswan dam, 1898-1902):
* regime 1 (1871-1898) = 1088, last regime (1918-1970) = 852. 1879 and 1913 are
* outlying years. The OLS mean (919) represents neither regime.
* ينخفض المتوسط بنحو 280 ابتداءً من 1899 (سد أسوان). المتوسط العادي 919 لا يمثل أيًّا من النظامين.


* =============================================================================
* PART 3. US LIFE EXPECTANCY 1900-1999  /  أمد الحياة في الولايات المتحدة
* =============================================================================
* --- A. DATA DICTIONARY / قاموس البيانات -------------------------------------
*  Variable  | Role                   | English                          | العربية
*  le        | DEPENDENT (التابع)     | life expectancy at birth, years  | العمر المتوقع عند الولادة بالسنوات
*  le_male   | DEPENDENT (2nd series) | life expectancy, males           | العمر المتوقع للذكور
*  le_female | DEPENDENT (3rd series) | life expectancy, females         | العمر المتوقع للإناث
*  year      | TIME and REGRESSOR     | calendar year (linear trend)     | السنة، وتُستخدم اتجاهًا زمنيًا خطيًا (متغير مستقل)
*  Regressors / المتغيرات المستقلة: a linear time trend (year) or the lag L.le (dynamics)
sysuse uslifeexp, clear
tsset year

* --- B. LOOK AT THE DATA / النظر إلى البيانات ---------------------------------
describe le le_male le_female
summarize le le_male le_female
tsline le le_male le_female, title("US life expectancy at birth, 1900-1999") ///
    graphregion(color(white)) name(le_raw, replace)
guide_png le_raw "`out'/05_life_data.png"

* --- C. BEFORE ESTIMATION: each series on its own / كل سلسلة بمفردها ---------
* C.1 A WRONG specification: a trending series around a constant only.
*     مواصفة خاطئة: سلسلة ذات اتجاه حول ثابت فقط
indsat le, iis tpval(0.01) nodates notable
display as text "Retained impulses in the WRONG model: " as result e(nret)
* Dozens of "outliers" = the omitted trend. LESSON: specify the model, then saturate.
* عشرات «القيم الشاذة» هي في الحقيقة الاتجاه المهمل. الدرس: حدّد النموذج أولًا ثم شبّعه

* C.2 Each series with its own dynamics (AR(1)) + impulses.  كل سلسلة مع ديناميكيتها
foreach v in le le_male le_female {
    display as text _n "{bf:Variable `v'}"
    quietly indsat `v', ar(1) iis tpval(0.01) nograph
    display as text "  retained: " as result "`e(retained)'"
}
* All three series show 1918 (influenza pandemic): a common shock to men and women.
* السلاسل الثلاث تُظهر 1918 (جائحة الإنفلونزا): صدمة مشتركة للذكور والإناث

* --- D. ESTIMATION: trend model / التقدير: نموذج الاتجاه ---------------------
regress le year

* --- E. AFTER ESTIMATION: saturate the trend model / تشبيع نموذج الاتجاه -----
* ULTRA = impulses + steps + broken trends (for trending series).
* التشبع الأقصى = نبضات + درجات + اتجاهات منكسرة (للسلاسل ذات الاتجاه)
indsat, ultra tpval(0.001)
guide_png indsat_dash "`out'/06_life_dashboard.png"
guide_png indsat_compare "`out'/07_life_compare.png"
indsat dates
guide_xls "`out'/indsat_tables.xlsx" "LifeExpectancy"

* --- F. INTERPRETATION / التفسير ----------------------------------------------
* 1918: a fall of about 15 years (pandemic); 1921: a permanent step up; 1955: a
* broken trend of about -0.16 years per year: gains in life expectancy slow down.
* The trend slope in the comparison table rises from 0.30 to 0.35 years per year once
* the breaks are modelled (before 1955), because the pandemic and the later slowdown
* had pulled the single OLS trend down.
* 1918 انخفاض بنحو 15 سنة؛ 1921 درجة صاعدة؛ 1955 تباطؤ نمو العمر المتوقع بنحو 0.16 سنة كل عام


* =============================================================================
* PART 4. UK ROAD CASUALTIES 1969-1984  /  ضحايا الطرق في بريطانيا
* =============================================================================
* --- A. DATA DICTIONARY / قاموس البيانات -------------------------------------
*  Variable        | Role                       | English                        | العربية
*  ldriverskilled  | DEPENDENT (التابع)         | log of car drivers killed      | لوغاريتم عدد السائقين القتلى شهريًا
*  lkms            | REGRESSOR (مستقل)          | log of distance driven         | لوغاريتم المسافة المقطوعة بالسيارات
*  lpetrol         | REGRESSOR (مستقل)          | log of real petrol price       | لوغاريتم السعر الحقيقي للبنزين
*  i.month         | CONTROLS (متغيرات ضابطة)   | 11 seasonal (monthly) dummies  | متغيرات وهمية للأشهر (الموسمية)
*  law             | KNOWN EVENT (للمقارنة)     | seat-belt law, 1 from 1983m2   | قانون حزام الأمان (1 من فبراير 1983)
*  mdate           | TIME                       | month 1969m1-1984m12           | الشهر
*  We do NOT put law in the model: we let saturation find the change by itself,
*  and use law only as an independent check.
*  لا نضع متغير القانون في النموذج: نترك التشبع يكتشف التغيّر بنفسه، ثم نقارن
use indsat_seatbelts, clear
tsset mdate
generate byte month = month(dofm(mdate))
label variable month "calendar month"
label variable ldriverskilled "log of car drivers killed"
label variable lkms "log of distance driven"
label variable lpetrol "log of real petrol price"

* --- B. LOOK AT THE DATA / النظر إلى البيانات ---------------------------------
describe ldriverskilled lkms lpetrol law
summarize ldriverskilled lkms lpetrol
tsline ldriverskilled, xline(`=tm(1983m2)', lpattern(dash)) title("Log car drivers killed (law: 1983m2)") ///
    graphregion(color(white)) name(roads_raw, replace)
guide_png roads_raw "`out'/08_roads_data.png"

* --- C. BEFORE ESTIMATION: each variable on its own / كل متغير بمفرده --------
* Each series with seasonal dummies + super saturation: what happened to EACH variable?
* كل سلسلة مع المتغيرات الموسمية والتشبع الفائق: ماذا حدث لكل متغير؟
foreach v in ldriverskilled lkms lpetrol {
    display as text _n "{bf:Variable `v': `: variable label `v''}"
    quietly indsat `v' i.month, super tpval(0.005) nograph
    indsat dates, compact
}
* ldriverskilled: a step EXACTLY in 1983m2 (the seat-belt law), size -0.18 (about -16%),
*                 + an outlier in 1981m12.
* lpetrol: steps in 1974m2 and 1979m6 (the two oil shocks).
* lkms: shifts in traffic, including 1983m2.
* المتغير التابع: درجة بالضبط في 1983m2 (قانون الحزام). سعر البنزين: درجتا 1974m2 و1979m6 (صدمتا النفط)

* --- D. ESTIMATION: the researcher's usual regression / الانحدار المعتاد للباحث --
regress ldriverskilled lkms lpetrol i.month

* --- E. AFTER ESTIMATION: saturate the model in memory / تشبيع النموذج المقدَّر ---
* One line: indsat reads y, x, factor variables, constant and sample from e(),
* re-estimates the SAME model with indicators, and draws the dashboard and the
* comparison of original vs robust coefficients.
* سطر واحد: يقرأ النموذج من الذاكرة ويعيد تقديره مع المؤشرات ويرسم المقارنة
indsat, super tpval(0.005)
guide_png indsat_dash "`out'/09_roads_dashboard.png"
guide_png indsat_compare "`out'/10_roads_compare.png"
indsat dates, compact
indsat diag

* E.2 Independent check with the KNOWN law dummy.  تحقق مستقل بمتغير القانون المعروف
regress ldriverskilled lkms lpetrol i.month law

* E.3 Coefficient breaks (MIS): does the petrol effect change, at common dates?
*     كسور المعاملات: هل يتغير أثر سعر البنزين، وبتواريخ مشتركة مع المستوى؟
indsat ldriverskilled lkms lpetrol i.month, sis mis(lpetrol) common tpval(0.005)
* With common dates each DATE is kept by a joint F-test of its block; individual
* t-ratios can be small (level and slope shifts are collinear): read the PATH.
* مع التواريخ المشتركة يُختار التاريخ باختبار F مشترك؛ اقرأ مسار المعامل لا قيم t المنفردة
indsat path
indsat plot, name(roads_mis)
guide_png roads_mis "`out'/11_roads_mis_paths.png"
guide_xls "`out'/indsat_tables.xlsx" "RoadCasualties"

* --- F. INTERPRETATION / التفسير ----------------------------------------------
* Before estimation the fatalities series shifts exactly at the law (1983m2).
* In the regression the shift is dated 1983m7 because traffic and petrol prices
* explain part of the fall. The law dummy gives -0.15 (about -14%).
* The petrol elasticity falls from -0.54 to -0.33 once breaks are modelled: the
* original regression attributed part of the level shifts to petrol prices.
* قبل التقدير ينكسر المتغير التابع في 1983m2 تمامًا؛ وبعد إدخال المتغيرات المستقلة يُؤرَّخ الكسر 1983m7
* لأن الحركة المرورية والأسعار تفسر جزءًا من الانخفاض. ومرونة سعر البنزين تنخفض من 0.54- إلى 0.33-


* =============================================================================
* PART 5. UK CONSUMPTION FUNCTION (DHSY 1978)  /  دالة الاستهلاك البريطانية
* =============================================================================
* --- A. DATA DICTIONARY / قاموس البيانات -------------------------------------
*  Variable | Role                | English                                   | العربية
*  c        | DEPENDENT (التابع)  | log real non-durable consumption          | لوغاريتم الاستهلاك الحقيقي غير المعمّر
*  y        | REGRESSOR (مستقل)   | log real personal disposable income       | لوغاريتم الدخل الشخصي المتاح الحقيقي
*  D4p      | REGRESSOR (مستقل)   | annual inflation (4th diff. of log prices) | التضخم السنوي
*  D6812    | KNOWN EVENT         | budget dummy +1 1968q1, -1 1968q2         | متغير ميزانية 1968 (+1 ثم -1)
*  D7312    | KNOWN EVENT         | VAT dummy +1 1973q1, -1 1973q2            | متغير ضريبة القيمة المضافة 1973
*  qdate    | TIME                | quarter 1957q1-1976q2                     | الربع
*  Note: D6812 and D7312 are +1/-1 pairs = the shape searched by DIS (differenced
*  impulses): spending brought forward before a tax change.
*  ملاحظة: D6812 وD7312 أزواج (+1، -1) وهي نفس شكل النبضات المفرَّقة DIS
use indsat_dhsy, clear
tsset qdate
generate D4c = c - L4.c
generate D4y = y - L4.y
label variable D4c "annual growth of consumption"
label variable D4y "annual growth of income"

* --- B. LOOK AT THE DATA / النظر إلى البيانات ---------------------------------
describe
summarize c y D4p
tsline D4c D4y D4p, title("Annual growth of consumption, income and prices") ///
    graphregion(color(white)) name(dhsy_raw, replace)
guide_png dhsy_raw "`out'/12_dhsy_data.png"

* --- C. BEFORE ESTIMATION: each variable on its own / كل متغير بمفرده --------
* Levels trend upwards, so we use growth rates (or ultra with a trend).
* المستويات ذات اتجاه، لذا نستخدم معدلات النمو
foreach v in D4c D4y D4p {
    display as text _n "{bf:Variable `v': `: variable label `v''}"
    quietly indsat `v', super tpval(0.01) nograph
    display as text "  super saturation, retained: " as result "`e(retained)'"
}
* D4p (inflation) shows a RUN of impulses in 1974-1976: a run of impulses is the
* signature of a level shift -> use SIS for this variable:
* سلسلة نبضات متتالية في التضخم 1974-1976 = علامة تحول مستوى، فنستخدم SIS
indsat D4p, sis tpval(0.01)
* Inflation regimes: 1964q2, 1970q4, 1974q1 (oil shock) ... 1976q2.

* --- D. ESTIMATION: the researcher's usual ARDL / نموذج ARDL المعتاد ---------
ardl c y D4p, lags(2 2 1)

* --- E. AFTER ESTIMATION: saturate the ARDL in memory / تشبيع ARDL المقدَّر ---
*  -> saturated ARDL regression + dashboard
*  -> long-run coefficients and adjustment speed WITHOUT vs WITH indicators
*  -> Pesaran-Shin-Smith bounds test with the indicators as unrestricted terms
indsat, sis tpval(0.01)
guide_png indsat_dash "`out'/13_dhsy_dashboard.png"
guide_png indsat_compare "`out'/14_dhsy_longrun_compare.png"
describe _I*
* The same in one command, with automatic lag selection (BIC):  نفس الشيء بأمر واحد
indsat ardl c y D4p, maxlags(4) super tpval(0.01) nograph

* --- F. INTERPRETATION / التفسير ----------------------------------------------
* ARDL(2,2,1): steps in 1966q2 and 1972q1; adjustment speed -1.37 -> -1.54;
* long-run income elasticity 0.81 -> 0.77; bounds test rejects "no level
* relationship" at 1% (F = 28.0). With automatic lags the adjustment speed moves
* from -0.34 to -0.71: ignoring shifts can badly understate error correction.
* يرفض اختبار الحدود عدم وجود علاقة طويلة الأجل؛ وتتضاعف سرعة التعديل عند نمذجة الكسور


* =============================================================================
* PART 6. ROBUSTNESS  /  المتانة
* =============================================================================
* 6.1 Stability across target sizes (Nile).  الاستقرار عبر مستويات الدلالة
use indsat_nile, clear
tsset year
indsat loop flow, nums(10(-1)1) seed(2026) graph name(nile_loop)
guide_png nile_loop "`out'/15_nile_loop.png"
* 6.2 Monte Carlo: how often does SIS find a shift of a given size (T = 100)?
*     محاكاة: كم مرة يكتشف SIS تحولًا بحجم معين؟
indsat sim, t(100) reps(40) sizes(0 1 2 3) tpval(0.01) seed(2026)


* =============================================================================
* PART 7. CHECKLIST FOR YOUR PAPER  /  قائمة التحقق لورقتك البحثية
* =============================================================================
*  1. Write the data dictionary: dependent variable, regressors, units, sources.
*     اكتب قاموس البيانات: المتغير التابع، المستقلة، الوحدات، المصادر
*  2. BEFORE estimation: saturate each variable (with its trend/seasonals) to know
*     the events in each series.   قبل التقدير: شبّع كل متغير لمعرفة أحداثه
*  3. Specify the economic model (trend, lags, seasonals), then saturate it
*     (indsat after regress / newey / ardl).   حدّد النموذج ثم شبّعه
*  4. alpha close to 1/T (smaller for SIS/TIS); justify with indsat gauge.
*  5. super by default; ultra for trending series; mis() for slope breaks.
*  6. Report dates and regimes (indsat dates), bias-corrected sizes (indsat biascorr),
*     diagnostics (indsat diag), outlier tests (indsat outlier), and the comparison
*     of original vs robust coefficients.
*  7. Robustness: indsat loop over alpha; results with and without saturation.
*  8. Interpret every date with real events (policies, crises, laws, shocks).
*     فسّر كل تاريخ بأحداث حقيقية
*  9. Cite Hendry, Johansen & Santos (2008); Castle et al. (2015); Pretis, Reade &
*     Sucarrat (2018); and indsat (github.com/merwanroudane/indsat).

display as text _n "{hline 70}"
display as text "Guide finished. Outputs are in the folder: " as result "`out'"
display as text "  - indsat_guide.log      full log"
display as text "  - indsat_tables.xlsx    break tables (one sheet per example)"
display as text "  - *.png                 data, dashboards, comparisons, path test, forecast"
display as text "{hline 70}"
log close
