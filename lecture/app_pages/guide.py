import streamlit as st

from lib import ui

ui.header("دليل اختيار نوع التشبع", "Which indicator saturation should I use?",
          "أجب عن الأسئلة فيقترح عليك الدليل الأنواع والأمر المناسب", "green")

q1 = st.radio("1. ما شكل السلسلة؟", ["مستقرة حول متوسط", "ذات اتجاه (تنمو عبر الزمن)", "لا أعرف"], key="gd1")
q2 = st.multiselect("2. ما الذي تتوقعه؟ (اختر ما ينطبق)",
                    ["قيم شاذة لمرة واحدة", "تغيّر في المستوى يستمر", "تغيّر في معدل النمو",
                     "تغيّر في أثر متغير (معامل)", "صدمة بشكل معروف (تعافٍ تدريجي)", "قفزة تنعكس فورًا",
                     "شذوذ في فترتين متتاليتين", "لا أعرف"], default=["لا أعرف"], key="gd2")
q3 = st.radio("3. هل في النموذج متأخرات للمتغير التابع؟", ["لا", "نعم"], horizontal=True, key="gd3")
q4 = st.radio("4. ما هدفك الأساسي؟", ["تقدير قوي للمعاملات", "تأريخ الأحداث وقياسها", "التنبؤ",
                                      "اختبار علاقة طويلة الأجل (ARDL)"], key="gd4")
T = st.number_input("5. عدد المشاهدات T", 20, 5000, 100, key="gd5")

opts: list[str] = []
why: list[str] = []
if "قيم شاذة لمرة واحدة" in q2:
    opts.append("iis")
    why.append("**IIS** للقيم الشاذة")
if "تغيّر في المستوى يستمر" in q2:
    opts.append("sis")
    why.append("**SIS** لتحولات المستوى")
if "تغيّر في معدل النمو" in q2 or (q1 == "ذات اتجاه (تنمو عبر الزمن)" and "لا أعرف" in q2):
    opts.append("tis")
    why.append("**TIS** لانكسار الاتجاه")
if "تغيّر في أثر متغير (معامل)" in q2:
    opts.append("mis(x)")
    why.append("**MIS** لكسور المعاملات (ضع اسم المتغير مكان x)")
if "صدمة بشكل معروف (تعافٍ تدريجي)" in q2:
    opts.append("bis(volcanic)")
    why.append("**BIS** للصدمات ذات الشكل المعروف")
if "قفزة تنعكس فورًا" in q2:
    opts.append("dis")
    why.append("**DIS** للقفزات المنعكسة")
if "شذوذ في فترتين متتاليتين" in q2 or q3 == "نعم":
    if "شذوذ في فترتين متتاليتين" in q2:
        opts.append("pis(1)")
        why.append("**PIS(1)** للشذوذ المزدوج")
if "لا أعرف" in q2 or not q2:
    if q1 == "ذات اتجاه (تنمو عبر الزمن)":
        opts = ["ultra"]
        why = ["**ultra** (IIS+SIS+TIS) الخيار الآمن للسلاسل ذات الاتجاه"]
    else:
        opts = ["super"]
        why = ["**super** (IIS+SIS) الخيار الآمن الافتراضي"]
if {"iis", "sis"} <= set(opts):
    opts = ["super"] + [o for o in opts if o not in ("iis", "sis")]
alpha = round(min(0.01, 1 / T), 4) if T >= 100 else 0.01
nsets = len(opts) + (1 if "super" in opts else 0) + (2 if "ultra" in opts else 0)
alpha = max(round(alpha / max(nsets, 1) * (1 if nsets <= 1 else 1.5), 4), 0.001)

st.divider()
st.markdown("## :material/assistant: التوصية")
with st.container(border=True):
    st.markdown("\n".join(f"- {w}" for w in why))
    st.markdown(f"- مستوى الدلالة المقترح: **α = {alpha}** (قريب من 1/T مع تشديد لعدة مجموعات)")
    if q3 == "نعم":
        st.markdown("- أدخل المتأخرات في النموذج قبل التشبع (الخيار ar() أو L.y)، وإلا كثرت المؤشرات الزائفة.")
    cmd = "indsat y x, " + " ".join(opts) + f" tpval({alpha})"
    if q4 == "اختبار علاقة طويلة الأجل (ARDL)":
        cmd = "ardl y x, lags(p q)\nindsat, " + " ".join(opts) + f" tpval({alpha})"
    elif q4 == "التنبؤ":
        cmd += "\nindsat forecast, h(8) graph"
    elif q4 == "تقدير قوي للمعاملات":
        cmd += "\nindsat distort        // هل غيّرت القيم الشاذة المعاملات؟"
    else:
        cmd += "\nindsat dates\nindsat plot"
    st.code(cmd, language="stata")
ui.warn("هذا دليل تعليمي. القرار النهائي يعتمد على فهمك للبيانات والنظرية الاقتصادية، "
        "ويُستحسن مقارنة أكثر من خيار (indsat loop لفحص الحساسية لـ α).")
ui.nav_hint("البرمجيات والأوامر")
