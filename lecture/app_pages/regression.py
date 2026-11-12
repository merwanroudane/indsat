import numpy as np
import plotly.graph_objects as go
import streamlit as st

from lib import figs, sim, ui

ui.header("التشبع داخل الانحدار ونماذج ARDL", "Saturating regressions and ARDL models",
          "قدّر نموذجك المعتاد ثم شبّعه: ما الذي يتغير؟", "green")

st.markdown(
    f"""
التشبع لا يستبدل نموذجك الاقتصادي بل **يحميه**. متغيرات النموذج (x، والمتأخرات، والثوابت) تبقى ثابتة أثناء البحث،
والمؤشرات وحدها تُختار. النتيجة: {ui.t('تقديرات قوية', 'robust estimates')} لمعاملاتك مع خريطة للأحداث.

### :material/route: سير العمل الموصى به
1. قدّر نموذجك المعتاد: انحدار عادي، Newey-West، أو ARDL.
2. شبّعه بالنوع المناسب (super عادة، وMIS إن شككت في معامل).
3. قارن: هل تغيرت المعاملات؟ (جدول ورسم المقارنة).
4. في ARDL: أعد اختبار الحدود (PSS) مع المؤشرات كمتغيرات حتمية غير مقيدة.
5. افحص التشخيصات والرسوم، وأبلغ عن النتائج **مع وبدون** التشبع.
"""
)

st.markdown("## :material/compare_arrows: عرض: الانحدار قبل التشبع وبعده")
a, b, c = st.columns(3)
shift = a.slider("تحول المستوى غير المنمذج", 0.0, 5.0, 3.0, 0.25, key="rg_s")
outl = b.slider("قيمة شاذة", 0.0, 10.0, 6.0, 0.5, key="rg_o")
seed = c.number_input("البذرة", 1, 99, 9, key="rg_seed")
T = 100
rng = np.random.default_rng(int(seed))
x = np.cumsum(rng.normal(size=T)) * 0.3 + rng.normal(size=T)
tt = np.arange(T)
y = 2 + 0.8 * x + shift * (tt >= 60) + rng.normal(size=T)
y[25] += outl
X = np.column_stack([np.ones(T), x])
f0 = sim.ols(y, X)
res = figs.run_search(y, X, [("IIS", *sim.impulses(T)), ("SIS", *sim.steps(T))], 0.01)
f1 = res.fit
rows = [("الثابت", 2.0, f0.b[0], f0.se[0], f1.b[0], f1.se[0]), ("معامل x", 0.8, f0.b[1], f0.se[1], f1.b[1], f1.se[1])]
fig = go.Figure()
for i, (nm, tru, b0, s0, b1, s1) in enumerate(rows[1:]):
    fig.add_trace(go.Scatter(x=[b0], y=["OLS"], error_x=dict(array=[1.96 * s0]), mode="markers",
                             marker=dict(size=14, color="#868e96"), name="OLS العادي"))
    fig.add_trace(go.Scatter(x=[b1], y=["المشبَّع"], error_x=dict(array=[1.96 * s1]), mode="markers",
                             marker=dict(size=14, color="#d6336c", symbol="diamond"), name="بعد التشبع"))
    fig.add_vline(x=tru, line_dash="dash", line_color="#2f9e44", annotation_text="الحقيقة 0.8")
st.plotly_chart(figs._base_layout(fig, "معامل x مع مجال ثقة 95%: قبل التشبع وبعده", 300))
k1, k2, k3 = st.columns(3)
k1.metric("معامل x (OLS)", f"{f0.b[1]:.3f}", delta=f"{f0.b[1] - 0.8:+.3f} عن الحقيقة", delta_color="inverse")
k2.metric("معامل x (مشبَّع)", f"{f1.b[1]:.3f}", delta=f"{f1.b[1] - 0.8:+.3f} عن الحقيقة", delta_color="inverse")
kinds = res.__dict__["_all_kinds"]
k3.metric("المؤشرات المكتشفة", ", ".join(f"{kinds[j]}{tau}" for j, tau in zip(res.selected, res.taus)) or "—")
st.plotly_chart(figs.result_figure(tt, y, res, None, "البيانات والتوفيق المشبَّع مع تواريخ الأحداث"))

st.markdown("## :material/multiline_chart: التشبع في ARDL")
st.latex(r"\Delta y_t=c+\alpha\,(y_{t-1}-\theta' x_{t-1})+\sum_i \phi_i\Delta y_{t-i}+\sum_j \omega_j'\Delta x_{t-j}"
         r"+\underbrace{\sum_s \gamma_s d_s(t)}_{\text{مؤشرات غير مقيدة}}+\varepsilon_t")
st.markdown(
    """
- المؤشرات تدخل **غير مقيدة** (الحالة الثالثة في PSS): درجة بحجم γ تزيح التوازن طويل الأجل بمقدار γ/(−α).
- القيم الشاذة وتحولات المستوى غير المنمذجة **تحرف** سرعة التعديل α والمعاملات طويلة الأجل θ واختبار الحدود.
- قيم الحدود الحرجة لا تأخذ الاختيار في الحسبان: استخدم α صغيرًا وقدّم النتائج بالطريقتين.
"""
)
st.code("regress y x1 x2\nindsat, super tpval(0.01)        // يقرأ النموذج من الذاكرة + رسوم + مقارنة\n\n"
        "ardl c y D4p, lags(2 2 1)\nindsat, sis tpval(0.01)          // ARDL مشبّع + مقارنة طويلة الأجل + اختبار الحدود",
        language="stata")
ui.nav_hint("المختبر: جرّب بنفسك")
