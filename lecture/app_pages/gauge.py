import numpy as np
import streamlit as st
from scipy import stats

from lib import figs, sim, ui

ui.header("المقياس والقوة", "Gauge and potency",
          "بديلا الحجم والقوة في عالم يُختبر فيه مئات المؤشرات معًا", "violet")

st.markdown(
    f"""
في الاختبار الواحد نتحدث عن {ui.t('الحجم', 'size')} و{ui.t('القوة', 'power')}. في التشبع نختبر مئات المؤشرات،
فنستخدم مفهومين مقابلين (Castle, Doornik & Hendry 2011):

- {ui.t('المقياس', 'gauge')}: **نسبة المؤشرات غير الضرورية التي احتُفظ بها خطأً** — يجب أن تكون قريبة من α.
- {ui.t('القوة الفعلية', 'potency')}: **نسبة المؤشرات الضرورية التي احتُفظ بها فعلًا** — نريدها كبيرة.
"""
)
st.latex(r"\text{gauge}=\frac{1}{T-n_1}\sum_{j\notin \text{truth}}\mathbf 1(\text{retained}_j)\qquad"
         r"\text{potency}=\frac{1}{n_1}\sum_{j\in \text{truth}}\mathbf 1(\text{retained}_j)")

st.markdown("## :material/calculate: الحاسبة النظرية")
c1, c2 = st.columns(2)
T = c1.slider("حجم العينة T", 20, 500, 100, 10, key="g_T")
alpha = c2.select_slider("α", [0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1], 0.01, key="g_a")
lam = alpha * T
m1, m2, m3, m4 = st.columns(4)
m1.metric("القيمة الحرجة c", f"{stats.norm.ppf(1 - alpha / 2):.2f}")
m2.metric("العدد المتوقع للزائفة αT", f"{lam:.2f}")
m3.metric("P(لا زائف)", f"{stats.poisson.pmf(0, lam):.3f}")
m4.metric("P(3 زائفة أو أكثر)", f"{1 - stats.poisson.cdf(2, lam):.3f}")


@st.cache_data(max_entries=20, show_spinner=False)
def mc_gauge(T: int, alpha: float, reps: int) -> np.ndarray:
    return sim.iis_gauge_mc(T, alpha, reps, seed=11)


@st.cache_data(max_entries=10, show_spinner=False)
def mc_potency(T: int, alpha: float, reps: int):
    sizes = [0.5, 1, 1.5, 2, 3, 4]
    pots, gaus = [], []
    for s in sizes:
        p, g = sim.sis_potency_mc(T, alpha, s, reps, seed=5)
        pots.append(p)
        gaus.append(g)
    return sizes, pots, gaus


st.markdown("## :material/play_circle: محاكاة مونت كارلو حية")
st.markdown("نولّد بيانات **بلا أي قيم شاذة** مرات عديدة ونطبق IIS بالنصفين، ثم نعدّ المؤشرات الزائفة. "
            "النظرية تقول إن العدد يتبع تقريبًا توزيع Poisson بمتوسط αT (Johansen & Nielsen 2016).")
reps = st.select_slider("عدد التكرارات", [50, 100, 200, 400], 100, key="g_reps")
if st.button("شغّل المحاكاة", icon=":material/play_arrow:", type="primary", key="g_run"):
    with st.spinner("جارٍ المحاكاة..."):
        counts = mc_gauge(min(T, 200), alpha, reps)
    st.plotly_chart(figs.gauge_hist(counts, alpha, min(T, 200)))
    if T > 200:
        st.caption("لأجل السرعة استُخدم T = 200 في المحاكاة.")

st.markdown("## :material/trending_up: القوة تزداد مع حجم الكسر")
st.markdown("محاكاة SIS: كسر واحد في منتصف العينة بأحجام مختلفة (بوحدات الانحراف المعياري σ).")
if st.button("احسب منحنى القوة", icon=":material/insights:", key="g_pot"):
    with st.spinner("جارٍ الحساب..."):
        sizes, pots, gaus = mc_potency(100, alpha, 40)
    st.plotly_chart(figs.potency_curve(sizes, pots, gaus))

st.markdown("## :material/balance: المفاضلة")
st.markdown(
    """
| إذا... | النتيجة |
|---|---|
| خفّضت α | مؤشرات زائفة أقل (gauge أصغر) لكن كسور صغيرة قد تفوتك (potency أقل) |
| رفعت α | تلتقط كسورًا أصغر لكن تزداد المؤشرات الزائفة |
| زاد حجم العينة T مع ثبات α | يزداد العدد المتوقع للزائفة αT — لذلك نخفض α مع T |
"""
)
ui.key_idea("قاعدة Nielsen & Qian (2025) لـ SIS: استخدم gauge صغيرًا (مثل 1% أو أقل)؛ فالـ gauge الصغير يقلل أيضًا "
            "تحيز التقديرات بعد الاختيار.")
ui.nav_hint("النظرية الإحصائية")
