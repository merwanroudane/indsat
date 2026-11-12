import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from lib import figs, sim, ui

ui.header("اختبارات القيم الشاذة", "Outlier proportion, count and distortion tests",
          "هل توجد قيم شاذة أصلًا؟ وهل غيّرت تقديراتنا؟", "red")

st.markdown(
    f"""
بعد IIS نحصل على عدد من النبضات المحتفظ بها. لكن تحت الفرضية العدمية نتوقع **αT** نبضة زائفة.
فالسؤال: هل العدد الذي وجدناه **أكبر مما تسمح به الصدفة**؟ اقترح Jiao وPretis (2022) ثلاثة اختبارات:
"""
)
c1, c2, c3 = st.columns(3)
with c1:
    ui.card(":red[اختبار النسبة] :gray[(proportion test)]", "يقارن النسبة المكتشفة بـ α باستخدام نظرية Johansen-Nielsen.",
            r"z=\frac{n/T-\alpha}{sd(\hat g)}")
with c2:
    ui.card(":orange[اختبار العدد] :gray[(count test)]", "اختبار Poisson دقيق للعدد مقابل αT؛ أفضل حين يكون α صغيرًا.",
            r"n\sim \text{Poisson}(\alpha T)")
with c3:
    ui.card(":violet[اختبار التشويه] :gray[(distortion test)]", "هل يختلف β بعد إزالة القيم الشاذة عن β بالمربعات الصغرى؟ "
            "(Jiao, Pretis & Schwarz)", r"H=T\,(\tilde\beta-\hat\beta)'\,\hat\Sigma^{-1}(\tilde\beta-\hat\beta)\sim\chi^2_k")

st.markdown("## :material/calculate: احسب الاختبار بنفسك")
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
if p_z < 0.05:
    ui.warn("نرفض الفرضية العدمية: عدد النبضات أكبر مما تفسّره الصدفة، فالبيانات تحتوي قيمًا شاذة حقيقية.")
else:
    ui.good("لا نرفض الفرضية العدمية: العدد المكتشف متسق مع النبضات الزائفة المتوقعة.")

xs = np.arange(0, max(int(lam * 4 + 6), n + 3))
fig = go.Figure()
fig.add_trace(go.Bar(x=xs, y=stats.poisson.pmf(xs, lam), marker_color=["#e8590c" if v == n else "#a5d8ff" for v in xs],
                     name="Poisson(αT)"))
fig.update_xaxes(title="عدد النبضات الزائفة")
st.plotly_chart(figs._base_layout(fig, "توزيع العدد تحت الفرضية العدمية؛ العمود البرتقالي هو ما وجدته", 360))

st.markdown("## :material/play_circle: التلوث يرفع العدد المكتشف")


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

st.markdown("## :material/stacked_line_chart: اختبارات القياس عبر مستويات α")
st.markdown("يمكن تكرار IIS على عدة قيم لـ α ثم اختبار المسار كله معًا: "
            "اختبار **المجموع** (sum) واختبار **الأعلى** (sup) — في Stata: `indsat loop`، وفي R: `isatloop` + `outlierscaletest`.")
st.code("indsat y x, iis tpval(0.01)\nindsat outlier\nindsat distort, boot(199) seed(1)\nindsat loop y x, nums(20(-1)1) graph",
        language="stata")
ui.nav_hint("تصحيح التحيز ومسار المعامل")
