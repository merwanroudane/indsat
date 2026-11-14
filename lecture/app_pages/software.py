import pandas as pd
import streamlit as st

from lib import ui

ui.hero("الأدوات", "البرمجيات والأوامر", "Software: Stata, R and OxMetrics",
        "ثلاث بيئات رئيسية لتطبيق التشبع. هنا تجد كيف تثبّت كل أداة، وجدولًا يقابل الأوامر ببعضها، "
        "وأمثلة جاهزة للنسخ تبدأ بها مباشرة.", "gray")
c1, c2, c3 = st.columns(3)
with c1:
    with ui.box("def", "Stata: مكتبة indsat"):
        st.markdown("أمر مركزي واحد `indsat` تحته كل الأنواع (بما فيها أنواع OxMetrics غير الموجودة في R) والاختبارات والرسوم، "
                    "ويعمل **بعد** regress وnewey وardl مباشرة.")
with c2:
    with ui.box("def", "R: حزمة gets"):
        st.markdown("مجانية ومفتوحة المصدر (Pretis, Reade & Sucarrat 2018). الدالة `isat()` تغطي IIS وSIS وTIS وUIS، "
                    "مع اختبارات القيم الشاذة ومسار المعامل.")
with c3:
    with ui.box("def", "OxMetrics: Autometrics"):
        st.markdown("البرنامج التجاري الأصلي (Doornik). خوارزمية بحث شجري مع اختبارات تشخيصية؛ وحزمة OxRegimes لـ MIS والأنظمة.")
st.markdown("## 🔄 جدول مقابلة الأوامر")

df = pd.DataFrame(
    [
        ["IIS", "iis", "iis = TRUE", "Autometrics: IIS"],
        ["SIS", "sis", "sis = TRUE", "Autometrics: SIS"],
        ["TIS", "tis", "tis = TRUE", "TIS"],
        ["Super / Ultra", "super / ultra", "iis+sis(+tis)", "IIS+SIS(+TIS)"],
        ["MIS", "mis(x)", "uis = x*sim(y)", "MIS"],
        ["BIS", "bis(volcanic|tc|ramp|, shape())", "uis = مصفوفة مصممة", "مؤشرات مستخدم"],
        ["DIS / PIS / QIS / CIS", "dis, pis(#), qis, cis", "uis", "مؤشرات مستخدم"],
        ["اختبارات القيم الشاذة", "indsat outlier / distort", "outliertest(), distorttest()", "—"],
        ["حلقة α", "indsat loop", "isatloop()", "—"],
        ["مسار المعامل واختباره", "indsat path / test", "isatvar(), isattest()", "—"],
        ["تصحيح التحيز", "indsat biascorr", "biascorr()", "—"],
        ["ARDL + اختبار الحدود", "indsat ardl / ardl ثم indsat", "—", "—"],
        ["بعد انحدارك", "regress ... ثم indsat, sis", "isat(lm_object)", "—"],
    ],
    columns=["الوظيفة", "Stata: indsat", "R: gets", "OxMetrics/PcGive"],
)
st.dataframe(df, hide_index=True)

st.markdown("## 💻 أمثلة جاهزة للنسخ")
t1, t2, t3 = st.tabs(["Stata (indsat)", "R (gets)", "OxMetrics (Ox)"])
with t1:
    st.code(
        """* التثبيت من GitHub
net install indsat, from("https://raw.githubusercontent.com/merwanroudane/indsat/main/") replace
indsat                         // القائمة الرئيسية للمكتبة
help indsat_types              // متى نستخدم كل نوع

use indsat_nile, clear
indsat flow, super tpval(0.01)
indsat dates                   // التواريخ والأنظمة
indsat plot                    // لوحة الرسوم
indsat test, hnull(1000) biascorr graph

regress y x1 x2                // نموذجك المعتاد...
indsat, sis mis(x1) common     // ...ثم شبّعه مباشرة

indsat gauge, t(100)           // نظرية: القيم الحرجة والعدد الزائف المتوقع
indsat sim, sizes(0 1 2 3 4)   // مونت كارلو للـ gauge والقوة""", language="stata")
with t2:
    st.code(
        """install.packages("gets"); library(gets)
m <- isat(Nile, iis = TRUE, sis = TRUE, t.pval = 0.01)
print(m); plot(m)
isatdates(m)
isattest(m, hnull = 1000, biascorr = TRUE, plot = TRUE)
outliertest(isat(Nile, iis = TRUE, sis = FALSE))
lp <- isatloop(num = 20:1, y = Nile); outlierscaletest(lp)""", language="r")
with t3:
    st.code(
        """#include <oxstd.oxh>
#import <packages/PcGive/pcgive_ects>
// OxRegimes (Ox package)
decl r = new Regimes();
r.Load("data.in7");
r.Model("y", {"Constant", "x"});
decl res = r.Saturation("SIS+MIS+IIS", 0.01, {{"vars", {"x"}}});
res.Print();""", language="cpp")
st.link_button("مستودع مكتبة indsat على GitHub", "https://github.com/merwanroudane/indsat",
               icon=":material/code:", type="primary")
with ui.box("tip", "هل تتطابق النتائج بين البرامج؟"):
    st.markdown("النتائج متطابقة رقميًا بين indsat (الإعداد الافتراضي) وgets::isat في R. أما Autometrics فخوارزمية "
                "مختلفة (بحث شجري مع اختبارات تشخيصية)، فقد تختلف النتائج في الحالات الحدّية. اذكر دائمًا في ورقتك "
                "البرنامج والخوارزمية ومستوى الدلالة.")
with ui.box("tip", "ملف تعليمي كامل"):
    st.markdown("مع المكتبة ملف `indsat_guide.do`: دليل من الصفر ببيانات حقيقية (النيل، حزام الأمان، الاستهلاك البريطاني)، "
                "يشرح كل متغير بالعربية والإنجليزية ويطبق التشبع قبل التقدير وبعده، مع جداول Excel ورسوم.")
ui.nav_hint("قاموس المصطلحات")
