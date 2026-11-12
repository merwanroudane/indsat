import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy import stats

from lib import figs, sim, ui

ui.header("تصحيح التحيز ومسار المعامل", "Post-selection bias correction and the coefficient path",
          "ما نحتفظ به لأنه «معنوي» يكون عادة مضخّمًا قليلًا — وهذا قابل للتصحيح", "violet")

st.markdown(
    f"""
### :material/content_cut: لماذا يوجد تحيز بعد الاختيار؟
نحتفظ بالمؤشر فقط إذا كان $|t|>c_\\alpha$. فالمؤشرات القريبة من الحد التي احتُفظ بها هي غالبًا التي «حالفها الحظ»
فكانت أكبر من حقيقتها. هذا {ui.t('تحيز الاختيار', 'selection bias')}، ويمكن تصحيحه بتوقع التوزيع الطبيعي المقطوع
(Hendry & Krolzig 2005؛ Pretis 2018):
"""
)
st.latex(r"r(t)=\frac{\varphi(c-t)-\varphi(-c-t)}{1-\Phi(c-t)+\Phi(-c-t)},\qquad "
         r"\tilde\gamma^{(1)}=\hat\gamma\Big(1-\frac{r(t)}{t}\Big),\qquad \tilde\gamma^{(2)}=\hat\gamma\Big(1-\frac{r(t-r(t))}{t}\Big)")

st.markdown("## :material/tune: جرّب التصحيح")
a, b, c = st.columns(3)
alpha = a.select_slider("α", [0.001, 0.005, 0.01, 0.025, 0.05], 0.01, key="bc_a")
se = b.number_input("الخطأ المعياري", 0.1, 10.0, 1.0, key="bc_se")
T = c.number_input("T", 20, 1000, 100, key="bc_T")
ts = np.linspace(2.0, 8.0, 61)
b1, b2 = sim.biascorr(ts * se, np.full_like(ts, se), alpha, int(T))
fig = go.Figure()
fig.add_trace(go.Scatter(x=ts, y=ts * se, name="المقدَّر γ̂", line=dict(color="#868e96", dash="dot")))
fig.add_trace(go.Scatter(x=ts, y=b1, name="مصحح بخطوة واحدة", line=dict(color="#1c7ed6", width=3)))
fig.add_trace(go.Scatter(x=ts, y=b2, name="مصحح بخطوتين", line=dict(color="#e8590c", width=3)))
fig.add_vline(x=stats.t.ppf(1 - alpha / 2, int(T)), line_dash="dash", line_color="#e03131",
              annotation_text="c_α")
fig.update_xaxes(title="إحصاءة t للمؤشر")
fig.update_yaxes(title="قيمة المعامل")
st.plotly_chart(figs._base_layout(fig, "التصحيح كبير قرب القيمة الحرجة ويتلاشى للمؤشرات القوية", 400))
ui.key_idea("مثال حقيقي (نهر النيل، SIS بـ α = 1%): درجة 1908 قُدّرت بـ 205.9، وبعد التصحيح بخطوتين تصبح 122.6؛ "
            "أما درجة 1899 القوية جدًا (t = −6.6) فلا تكاد تتغير (−280.6).")

st.markdown("## :material/auto_graph: مسار المعامل واختبار المسار")
st.markdown(
    """
مجموع الثابت والمؤشرات المحتفظ بها يعطي **مسار القاطع** عبر الزمن. تبايته الدقيق $a_t'Va_t$ حيث $a_t$ قيم
المؤشرات عند $t$. اختبار المسار (Pretis 2016: isattest) يحدد الفترات التي يختلف فيها المسار معنويًا عن قيمة
مرجعية $h_0$ — مثل تحيز نموذج مناخي، أو انحراف التضخم عن الهدف.
"""
)
s1, s2, s3 = st.columns(3)
h0 = s1.number_input("القيمة المرجعية h0", -5.0, 5.0, 1.0, 0.5, key="pt_h0")
shift = s2.slider("حجم التحول", 0.0, 4.0, 1.5, 0.25, key="pt_s")
seed = s3.number_input("البذرة", 1, 99, 5, key="pt_seed")
t, y, x, mu = sim.dgp(100, seed=int(seed), mu=1.0, shifts=[(55, shift)])
res = figs.run_search(y, np.ones((100, 1)), [("SIS", *sim.steps(100))], 0.01)
Z = np.column_stack([np.ones(100)] + ([res.D[:, j] for j in res.selected]))
f = res.fit
XtXi = np.linalg.pinv(Z.T @ Z)
V = XtXi * f.sigma ** 2
path = Z @ f.b
sep = np.sqrt(np.einsum("ij,jk,ik->i", Z, V, Z))
crit = stats.t.ppf(0.995, 100 - Z.shape[1])
lo, hi = path - crit * sep, path + crit * sep
bias = np.where(lo > h0, path - h0, np.where(hi < h0, path - h0, 0))
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=np.r_[t, t[::-1]], y=np.r_[hi, lo[::-1]], fill="toself", fillcolor="rgba(214,51,108,0.15)",
                          line=dict(width=0), name="مجال 99%"))
fig2.add_trace(go.Scatter(x=t, y=y, mode="lines", line=dict(color="#ced4da"), name="البيانات"))
fig2.add_trace(go.Scatter(x=t, y=path, line=dict(color="#d6336c", width=3), name="مسار القاطع"))
fig2.add_hline(y=h0, line_dash="dash", line_color="#212529", annotation_text="h0")
fig2.add_trace(go.Bar(x=t, y=bias, marker_color="rgba(28,126,214,0.55)", name="انحراف معنوي عن h0"))
st.plotly_chart(figs._base_layout(fig2, "المسار ومجال ثقته؛ الأعمدة الزرقاء = فترات الانحراف المعنوي", 420))
st.code("indsat y, sis tpval(0.01)\nindsat biascorr\nindsat path, generate(mu)\nindsat test, hnull(1) biascorr graph",
        language="stata")
ui.nav_hint("التنبؤ بعد الكسور")
