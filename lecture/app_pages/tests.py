import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from lib import figs, sim, ui

ui.hero("ما بعد التقدير 1", "اختبارات القيم الشاذة", "Outlier proportion, count and distortion tests",
        "وجدت الخوارزمية بعض المؤشرات. لكن هل هي أحداث حقيقية أم مجرد صدفة؟ وهل غيّرت نتائجك فعلًا؟ "
        "ثلاثة اختبارات رسمية تجيب عن هذين السؤالين، وستتعلم هنا كيف تقرأها وتكتبها في ورقتك.", "red")
ui.objectives([
    "لماذا لا يكفي أن تجد مؤشرات لتقول إن هناك قيمًا شاذة",
    "اختبار النسبة واختبار العدد: هل الشذوذ أكثر من الصدفة؟",
    "اختبار التشويه: هل غيّرت القيم الشاذة معاملاتك الاقتصادية؟",
    "كيف تحسب الاختبار وتقرأ قيمته الاحتمالية",
], minutes=15)

st.markdown("## ❓ السؤال الذي تجيب عنه الاختبارات")
st.markdown(
    """
تعلمت أن IIS يحتفظ في المتوسط بـ **αT** نبضة زائفة حتى لو كانت البيانات نظيفة تمامًا. فإذا وجدت 3 نبضات في عينة من 100
مشاهدة بـ α = 0.01، هل هذا كثير؟ العدد المتوقع بالصدفة هو 1، فالثلاث أكثر قليلًا، لكن هل الفرق **معنوي**؟

اقترح Jiao وPretis (2022) اختبارات رسمية تقارن ما وجدته بما تتوقعه الصدفة، واختبارًا ثالثًا يسأل سؤالًا مختلفًا: حتى لو كانت
القيم الشاذة حقيقية، هل **غيّرت** نتائجك الاقتصادية؟
"""
)
with ui.box("analogy", "جرس الإنذار"):
    st.markdown("جرس إنذار الحريق في مبنى كبير يرن بالخطأ مرة في الشهر (بخار، غبار). إذا رن مرة هذا الشهر فلا داعي للقلق. "
                "إذا رن **عشر مرات** فهناك شيء حقيقي. اختبار العدد يقارن عدد الرنات بالمعدل المعتاد للإنذارات الكاذبة.")
c1, c2, c3 = st.columns(3)
with c1:
    with ui.box("def", "اختبار النسبة"):
        st.markdown("يقارن **نسبة** المؤشرات المكتشفة n/T بـ α، باستخدام التوزيع الطبيعي للمقياس (Johansen-Nielsen). "
                    "مناسب حين تكون العينة كبيرة.")
        st.latex(r"z=\frac{n/T-\alpha}{sd(\hat g)}")
with c2:
    with ui.box("def", "اختبار العدد"):
        st.markdown("اختبار **Poisson** دقيق للعدد n مقابل المتوسط αT. أفضل حين يكون α صغيرًا (وهي الحالة المعتادة).")
        st.latex(r"n\sim \text{Poisson}(\alpha T)")
with c3:
    with ui.box("def", "اختبار التشويه"):
        st.markdown("هل تختلف المعاملات بعد إزالة القيم الشاذة عن معاملات OLS؟ إذا رُفض، فالقيم الشاذة **كانت تشوه** نتائجك.")
        st.latex(r"H=T\,(\tilde\beta-\hat\beta)'\,\hat\Sigma^{-1}(\tilde\beta-\hat\beta)\sim\chi^2_k")

st.markdown("## 🧮 احسب الاختبار بنفسك")
st.markdown("أدخل حجم عينتك ومستوى الدلالة وعدد النبضات التي وجدتها، واقرأ القرار:")
a1, a2, a3 = st.columns(3)
T = a1.number_input("T (عدد المشاهدات)", 20, 2000, 100, key="ot_T")
alpha = a2.select_slider("α", [0.001, 0.005, 0.01, 0.025, 0.05], 0.01, key="ot_a")
n = a3.number_input("عدد النبضات المكتشفة", 0, 200, 4, key="ot_n")
sd = np.sqrt(sim.vargauge(alpha, int(T)))
z = (n / T - alpha) / sd
p_z = 2 * stats.norm.sf(abs(z))
lam = alpha * T
p_pois = stats.poisson.sf(n - 1, lam) if n > lam else stats.poisson.cdf(n, lam)
m1, m2, m3 = st.columns(3)
m1.metric("العدد المتوقع αT", f"{lam:.2f}")
m2.metric("إحصاءة z (النسبة)", f"{z:.2f}", help=f"p-value ثنائي = {p_z:.4f}")
m3.metric("p-value (Poisson، أحادي)", f"{p_pois:.4f}")
if p_pois < 0.05:
    with ui.box("warn", "القرار: نرفض الفرضية العدمية"):
        st.markdown(f"وجدت {n} نبضة بينما تتوقع الصدفة {lam:.2f} فقط. احتمال الحصول على هذا العدد أو أكثر بالصدفة "
                    f"هو {p_pois:.4f}، فالبيانات تحتوي **قيمًا شاذة حقيقية**.")
else:
    with ui.box("tip", "القرار: لا نرفض الفرضية العدمية"):
        st.markdown(f"وجدت {n} نبضة والعدد المتوقع بالصدفة {lam:.2f}. الفرق ليس معنويًا (p = {p_pois:.4f})، "
                    "فالمؤشرات المكتشفة **قد تكون زائفة**؛ لا تبنِ عليها تفسيرات تاريخية قوية.")

xs = np.arange(0, max(int(lam * 4 + 6), n + 3))
fig = go.Figure()
fig.add_trace(go.Bar(x=xs, y=stats.poisson.pmf(xs, lam), marker_color=["#e8590c" if v == n else "#a5d8ff" for v in xs],
                     name="Poisson(αT)"))
fig.update_xaxes(title="عدد النبضات الزائفة")
st.plotly_chart(figs._base_layout(fig, "توزيع العدد تحت الفرضية العدمية؛ العمود البرتقالي هو ما وجدته", 360))

st.markdown("## 🎲 التلوث يرفع العدد المكتشف")
st.markdown("محاكاة: نلوّث نسبة من المشاهدات بصدمات حجمها ±5σ ونعد النبضات المكتشفة. كلما زاد التلوث ابتعد العدد عن αT، وهذا ما تلتقطه الاختبارات.")


@st.cache_data(max_entries=20, show_spinner=False)
def contamination_curve(alpha: float, reps: int):
    T = 100
    fracs = [0.0, 0.02, 0.05, 0.1]
    rng = np.random.default_rng(3)
    X = np.ones((T, 1))
    D, taus = sim.impulses(T)
    out = []
    for f in fracs:
        cnt = []
        for _ in range(reps):
            y = rng.normal(size=T)
            m = int(f * T)
            idx = rng.choice(T, m, replace=False)
            y[idx] += rng.choice([-1, 1], m) * 5
            cnt.append(len(sim.saturate(y, X, [("IIS", D, taus)], alpha=alpha, nblocks=2).selected))
        out.append(np.mean(cnt))
    return fracs, out


if st.button("شغّل المحاكاة", icon=":material/play_arrow:", type="primary", key="ot_run"):
    with st.spinner("جارٍ المحاكاة..."):
        fr, cnt = contamination_curve(alpha, 40)
    f2 = go.Figure(go.Bar(x=[f"{int(100 * f)}%" for f in fr], y=cnt, marker_color="#ae3ec9",
                          text=[f"{c:.1f}" for c in cnt], textposition="outside"))
    f2.add_hline(y=alpha * 100, line_dash="dash", line_color="#e03131", annotation_text="αT")
    f2.update_xaxes(title="نسبة المشاهدات الملوثة (صدمة ±5σ)")
    f2.update_yaxes(title="متوسط عدد النبضات المكتشفة")
    st.plotly_chart(figs._base_layout(f2, "كلما زاد التلوث زاد العدد فوق αT — وهذا ما تلتقطه الاختبارات", 380))

st.markdown("## 📊 اختبارات عبر عدة مستويات α")
st.markdown("يمكن تكرار IIS على عدة قيم لـ α ثم اختبار المسار كله معًا: اختبار **المجموع** (sum) واختبار **الأعلى** (sup). "
            "في Stata: `indsat loop`، وفي R: `isatloop` ثم `outlierscaletest`.")
st.code("indsat y x, iis tpval(0.01)\nindsat outlier\nindsat distort, boot(199) seed(1)\nindsat loop y x, nums(20(-1)1) graph",
        language="stata")
with ui.box("example", "كيف تكتب النتيجة في الورقة"):
    st.markdown("> *IIS at α = 0.01 retains 7 impulses against an expected 1.9 under the null (T = 192). "
                "The Jiao–Pretis count test rejects the null of no outliers (p < 0.001), and the distortion test "
                "indicates that the outliers significantly affect the estimated coefficients (p = 0.02).*")
ui.check("T = 200 وα = 0.005 ووجدت نبضة واحدة. ماذا تستنتج؟",
         ["قيم شاذة حقيقية مؤكدة", "العدد متسق مع الصدفة (المتوقع 1)", "يجب رفض النموذج", "α خاطئ"], 1,
         "αT = 1؛ نبضة واحدة هي بالضبط ما تتوقعه الصدفة.", "ot_q1")
ui.check("ماذا يعني رفض اختبار التشويه؟",
         ["أن القيم الشاذة زائفة", "أن القيم الشاذة كانت تغير المعاملات الاقتصادية معنويًا", "أن α كبير", "أن النموذج سليم"], 1,
         "التشويه يقارن β قبل إزالة القيم الشاذة وبعدها.", "ot_q2")
ui.summary([
    "وجود مؤشرات لا يعني وجود قيم شاذة: قارن العدد بـ αT.",
    "اختبار العدد (Poisson) والنسبة (طبيعي) يحسمان هل الشذوذ أكثر من الصدفة.",
    "اختبار التشويه يسأل: هل غيّرت القيم الشاذة معاملاتك؟",
    "اذكر الاختبارات وقيمها الاحتمالية في ورقتك.",
])
ui.nav_hint("تصحيح التحيز ومسار المعامل")
