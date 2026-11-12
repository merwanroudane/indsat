import streamlit as st

from lib import figs, sim, ui

ui.header("النظرية الإحصائية", "Asymptotic theory: IIS as a robust estimator",
          "Johansen & Nielsen: التشبع بالنبضات هو مقدِّر Huber-skip — حماية شبه مجانية", "violet")

st.markdown(
    f"""
### من الخوارزمية إلى المقدِّر
أثبت Johansen وNielsen (2009) أن IIS ذا النصفين يكافئ {ui.t('مقدِّر M ذا الخطوة الواحدة', 'one-step M-estimator')}
من نوع {ui.t('Huber-skip', 'skip function')}: نقدّر مبدئيًا، ثم **نتخطى** المشاهدات التي تتجاوز بواقيها المعيارية حدًّا $c$،
ثم نعيد التقدير بالمربعات الصغرى على الباقي:
"""
)
st.latex(r"\tilde\beta=\Big(\sum_{t} x_t x_t'\,\mathbf 1(|v_t|\le c)\Big)^{-1}\sum_t x_t y_t\,\mathbf 1(|v_t|\le c),"
         r"\qquad v_t=\frac{y_t-\hat\beta' x_t}{\hat\sigma}")
st.markdown("وتكرار هذه الخطوة m مرة يعطي **Huber-skip ذا m خطوة** (Johansen & Nielsen 2013, 2016)، "
            "أما الحد الأقصى للتكرار فيعطي مقدِّر Huber-skip الكامل.")

st.markdown("### :material/functions: الكميات الأساسية (توزيع طبيعي)")
st.latex(r"\psi=\Phi(c)-\Phi(-c)=1-\alpha,\qquad \tau=\psi-2c\,\varphi(c),\qquad "
         r"\xi^2=\frac{\psi}{\tau},\qquad \eta_1^2=\Big(\frac{1}{\psi^2}+\frac{2\rho}{\psi}\Big)\tau+\rho^2,\ \ \rho=\frac{2c\varphi(c)}{\psi}")
st.markdown(
    """
- $\\xi$: **عامل الاتساق** — التباين المقدَّر من المشاهدات «الجيدة» أصغر من الحقيقي لأننا حذفنا الأطراف، فنضربه في $\\xi^2$.
- $\\eta^2$: **تضخم تباين** $\\hat\\beta$ مقارنة بالمربعات الصغرى حين لا توجد قيم شاذة؛ الكفاءة = $1/\\eta^2$.
"""
)
a = st.select_slider("اختر α", [0.001, 0.005, 0.01, 0.025, 0.05, 0.1], 0.01, key="th_a")
f = sim.jn_factors(a)
c1, c2, c3, c4 = st.columns(4)
c1.metric("c", f"{f['c']:.3f}")
c2.metric("ξ (اتساق σ)", f"{f['xi']:.4f}")
c3.metric("η (تضخم s.e.)", f"{f['eta']:.4f}")
c4.metric("الكفاءة 1/η²", f"{100 * f['eff']:.1f}%")
st.plotly_chart(figs.efficiency_curve())
ui.good("مع α = 1% تبلغ كفاءة IIS نحو 93% من كفاءة OLS حين لا توجد قيم شاذة أصلًا — "
        "وحين توجد، يتفوق IIS على OLS بفارق كبير. إنه تأمين رخيص.")

st.markdown("### :material/science: نتائج نظرية أخرى مهمة")
r1, r2 = st.columns(2)
with r1:
    ui.card("Gauge طبيعي وPoisson", "عدد المؤشرات الزائفة ≈ Poisson(αT) حين يكون α صغيرًا، "
            "ونسبته ≈ طبيعي حين α ثابت (Johansen & Nielsen 2016).",
            r"\sqrt{T}(\hat g-\alpha)\ \xrightarrow{d}\ N\big(0,\ \psi(1-\psi)+\eta_\gamma\big)")
    ui.card("اختبار نسبة القيم الشاذة", "يستخدم التوزيع أعلاه لاختبار H0: لا توجد قيم شاذة (Jiao & Pretis 2022).",
            r"z=\frac{\hat g-\alpha}{\widehat{sd}(\hat g)}\sim N(0,1)")
with r2:
    ui.card("SIS: فروق للأمام", "تحليل Nielsen & Qian (2025) يعمل على الفروق Δy؛ تباين الـ gauge أكبر من IIS "
            "ويتأثر بالارتباط الذاتي، لذا يُفضَّل α أصغر.", r"\chi_i=\frac{\varepsilon_i-\varepsilon_{i+1}}{\sqrt2\,\sigma}")
    ui.card("صلاحية واسعة", "النتائج تشمل الانحدارات الثابتة، والانحدار الذاتي، والاتجاهات الحتمية، "
            "وجذر الوحدة (بتوزيعات حدية مختلفة).", r"N^{-1}(\tilde\beta-\beta)\ \text{يتبع نفس توسع}\ \text{Huber}")
ui.nav_hint("IIS: النبضات والقيم الشاذة")
