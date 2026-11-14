import numpy as np
import pandas as pd
import streamlit as st

from lib import figs, sim, ui

ui.hero("المختبر", "صمّم بياناتك وجرّب بنفسك", "Indicator saturation lab",
        "أفضل طريقة لفهم أي طريقة إحصائية أن تجربها على بيانات تعرف حقيقتها. هنا تصنع سلسلة فيها أحداث تختارها أنت، "
        "ثم ترى هل تكتشفها الخوارزمية، ومتى تخطئ، ولماذا.", "orange")
with ui.box("tip", "كيف تستخدم المختبر؟"):
    st.markdown(
        """
1. **الإعدادات العامة** (حجم العينة، الضجيج، الارتباط الذاتي) في القائمة الجانبية على اليمين.
2. **صمّم الأحداث**: اختر تواريخ القيم الشاذة وتحولات المستوى وأحجامها، وإن شئت انكسار اتجاه أو كسر معامل.
3. **اختر الأنواع** وα، ثم شاهد البحث وقارن ما وجدته الخوارزمية بالحقيقة في العدادات أسفل الصفحة.
"""
    )

with st.sidebar:
    st.markdown("#### :material/science: إعدادات المختبر")
    T = st.slider("T", 50, 200, 100, 10, key="lab_T")
    sigma = st.slider("الانحراف المعياري للضجيج σ", 0.3, 3.0, 1.0, 0.1, key="lab_sig")
    rho = st.slider("الارتباط الذاتي للأخطاء ρ", 0.0, 0.8, 0.0, 0.1, key="lab_rho")
    seed = st.number_input("البذرة", 1, 9999, 11, key="lab_seed")

st.markdown("## ✏️ 1. صمّم الأحداث الحقيقية")
c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.markdown(":orange[**قيم شاذة**]")
        o_dates = st.multiselect("التواريخ", list(range(T)), default=[int(0.2 * T), int(0.75 * T)], key="lab_od")
        o_size = st.slider("الحجم", -10.0, 10.0, 5.0, 0.5, key="lab_os")
with c2:
    with st.container(border=True):
        st.markdown(":blue[**تحولات مستوى**]")
        s_dates = st.multiselect("التواريخ ", list(range(1, T)), default=[int(0.5 * T)], key="lab_sd")
        s_size = st.slider("الحجم ", -6.0, 6.0, 2.5, 0.25, key="lab_ss")
with c3:
    with st.container(border=True):
        st.markdown(":green[**انكسار اتجاه / معامل**]")
        tb = st.number_input("تاريخ انكسار الاتجاه (0 = لا يوجد)", 0, T - 1, 0, key="lab_tb")
        tslope = st.slider("الميل الإضافي", -0.3, 0.3, 0.1, 0.02, key="lab_tsl")
        bb = st.number_input("تاريخ كسر معامل x (0 = لا يوجد)", 0, T - 1, 0, key="lab_bb")
        bshift = st.slider("تغيّر معامل x", -3.0, 3.0, 1.5, 0.25, key="lab_bs")

st.markdown("## 🎛️ 2. اختر طريقة التشبع")
d1, d2 = st.columns([3, 1])
kinds = d1.pills("أنواع المؤشرات", ["IIS", "SIS", "TIS", "DIS", "PIS", "BIS", "MIS"], selection_mode="multi",
                 default=["IIS", "SIS"], key="lab_kinds")
alpha = d2.select_slider("α", [0.001, 0.0025, 0.005, 0.01, 0.025, 0.05], 0.01, key="lab_a")
kinds = kinds or ["IIS"]

t, y, x, mu = sim.dgp(T, seed=int(seed), sigma=sigma, rho=rho, beta=1.0,
                      outliers=[(d, o_size) for d in o_dates], shifts=[(d, s_size) for d in s_dates],
                      trend_breaks=[(int(tb), tslope)] if tb else None,
                      beta_shift=(int(bb), bshift) if bb else None)
X = np.column_stack([np.ones(T), x])
sets = []
for k in kinds:
    if k == "MIS":
        sets.append(("MIS", *sim.multiplicative(x)))
    else:
        sets.append((k, *sim.build_set(k, T)))
ncand = sum(s[1].shape[1] for s in sets)
st.caption(f"عدد المرشحين = {ncand}، والعدد المتوقع للمؤشرات الزائفة αN ≈ {alpha * ncand:.2f}")

res = figs.run_search(y, X, sets, alpha)

st.markdown("## ▶️ 3. شاهد البحث")
tab1, tab2, tab3 = st.tabs(["▶ البحث خطوة بخطوة", "النتيجة", "الجدول"])
with tab1:
    st.plotly_chart(figs.search_animation(t, y, res, None),
                    key=f"lab_anim_{seed}_{alpha}_{kinds}_{T}")
with tab2:
    st.plotly_chart(figs.result_figure(t, y, res, None, "البيانات والنموذج المشبَّع"), key=f"lab_res_{seed}_{alpha}_{kinds}")
with tab3:
    kd = res.__dict__["_all_kinds"]
    k = X.shape[1]
    rows = []
    for i, (j, tau) in enumerate(zip(res.selected, res.taus)):
        rows.append({"النوع": kd[j], "التاريخ": tau, "المعامل": round(res.fit.b[k + i], 3),
                     "الخطأ المعياري": round(res.fit.se[k + i], 3), "t": round(res.fit.t[k + i], 2)})
    st.dataframe(pd.DataFrame(rows) if rows else pd.DataFrame({"النتيجة": ["لم يُحتفظ بأي مؤشر"]}), hide_index=True)
    st.markdown(f"**معامل x المقدَّر:** {res.fit.b[1]:.3f} (الحقيقي 1.0{f' ثم {1 + bshift:.2f} بعد t={bb}' if bb else ''})")

truth = sorted(set([("IIS", d) for d in o_dates] + [("SIS", d) for d in s_dates] +
                   ([("TIS", int(tb))] if tb else []) + ([("MIS", int(bb))] if bb else [])), key=lambda z: z[1])
found = list(zip([res.__dict__["_all_kinds"][j] for j in res.selected], res.taus))
hits = sum(any(abs(fd[1] - tr[1]) <= 2 for fd in found) for tr in truth)
false = sum(not any(abs(fd[1] - tr[1]) <= 2 for tr in truth) for fd in found)
m1, m2, m3 = st.columns(3)
m1.metric("الأحداث الحقيقية", len(truth))
m2.metric("اكتُشفت (±2)", f"{hits} / {len(truth)}")
m3.metric("مؤشرات زائفة", false)
st.markdown("## 🧪 تجارب مقترحة")
ui.steps([
    ("IIS وحده مع تحول مستوى كبير", "أزل SIS واترك IIS. كيف يلتقط التحول؟ بسلسلة نبضات أم لا يلتقطه أصلًا؟"),
    ("ارفع α إلى 0.05", "راقب عداد المؤشرات الزائفة. هل يقترب من αN المتوقع المكتوب تحت الأزرار؟"),
    ("أضف ارتباطًا ذاتيًا ρ = 0.6", "دون نمذجته، يزيد الارتباط الذاتي الاكتشافات الزائفة. الدرس: النموذج الجيد أولًا."),
    ("كسر في معامل x", "ضع تاريخًا لكسر المعامل، ثم جرّب SIS وحده ثم MIS. أيهما يلتقطه؟"),
    ("حدث صغير جدًا", "صغّر حجم تحول المستوى إلى 0.5. متى تبدأ الخوارزمية في تفويته؟ هذه هي القوة."),
], "orange")
ui.summary([
    "التجربة على بيانات تعرف حقيقتها هي أسرع طريق لفهم الطريقة.",
    "الشكل المطابق (SIS للتحول، MIS للمعامل) يكتشف الأحداث بقوة أكبر.",
    "α الكبير يرفع المؤشرات الزائفة، والارتباط الذاتي غير المنمذج يرفعها أيضًا.",
])
ui.nav_hint("مقارنة مع الطرق الأخرى")
