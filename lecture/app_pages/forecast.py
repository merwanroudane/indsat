import numpy as np
import plotly.graph_objects as go
import streamlit as st

from lib import figs, ui

ui.hero("ما بعد التقدير 3", "التنبؤ بعد الكسور", "Forecasting after breaks and large forecast errors",
        "المؤشرات ليست أداة لفهم الماضي فقط. حين يقع كسر قرب نهاية العينة، تصبح هي الطريقة الوحيدة لإعادة التنبؤ إلى "
        "المسار الصحيح بسرعة. هذا الدرس يشرح كيف يتصرف كل نوع عند التنبؤ، وأحدث فكرة في هذا المجال (2026).", "blue")
ui.objectives([
    "لماذا تفشل النماذج في التنبؤ بعد تحولات المستوى",
    "ماذا يحدث لكل نوع من المؤشرات عند التنبؤ",
    "تصحيح القاطع: أبسط أداة لإنقاذ التنبؤ",
    "طريقة Castle وDoornik وHendry (2026): التعلم من الأخطاء الكبيرة",
], minutes=15)

st.markdown("## 🔮 لماذا تفشل التنبؤات؟")
st.markdown(
    """
وجد Clements وHendry في سلسلة أبحاث شهيرة (التسعينيات) أن **السبب الأول** لفشل التنبؤات الاقتصادية ليس المتغيرات المنسية
ولا الأخطاء في المعاملات، بل **تحولات المستوى** التي لم يعرف بها النموذج. النموذج الذي قُدّر قبل الكسر «يعيش في الماضي»:
يتنبأ بالمتوسط القديم بينما الواقع انتقل إلى مستوى جديد، فتتراكم الأخطاء في اتجاه واحد فترة بعد فترة.
"""
)
with ui.box("analogy", "تطبيق الخرائط بعد إغلاق طريق"):
    st.markdown("تطبيق الخرائط الذي لم يعلم بإغلاق جسر سيستمر في توجيهك إليه كل مرة. التطبيق الذكي يلاحظ أن السيارات توقفت عنده "
                "فيعيد حساب المسار فورًا. المؤشرات في نهاية العينة هي «إشعار الإغلاق» الذي يجعل النموذج يعيد حساب تنبؤه.")

st.markdown("## 🧭 ماذا يحدث لكل نوع عند التنبؤ؟")
ui.steps([
    ("النبضة", "تنتهي داخل العينة، فلا تؤثر في التنبؤ. القيمة الشاذة لا تُنقل إلى المستقبل، وهذا صحيح."),
    ("الدرجة", "تستمر: المستوى الجديد يُنقل إلى المستقبل. ولهذا يفضّل بعض الباحثين صيغة 1(t ≤ j) حتى لا تمتد للتنبؤ."),
    ("الاتجاه المنكسر", "يستمر بميله الجديد، فيتنبأ النموذج بالنمو الجديد لا القديم."),
    ("تصحيح القاطع", "إضافة آخر خطأ تنبؤ إلى التنبؤات اللاحقة (Hendry & Clements 1994): بسيط وقوي جدًا بعد تحول مستوى."),
], "blue")
with ui.box("why", "الفكرة الجديدة: Castle وDoornik وHendry (2026)"):
    st.markdown(
        """
**خطأ تنبؤ كبير واحد يحمل معلومة ثمينة.** نضيف **نبضة** عند أصل التنبؤ، وهذا يعادل تصحيح القاطع. فإذا تبعه خطأ كبير آخر
**بالإشارة نفسها**، فالأرجح أن ما يحدث ليس صدمة عابرة بل **انكسار اتجاه**. عندئذ نختبر هل تحل الدرجة أو الاتجاه المنكسر
(الخطي أو اللوغاريتمي) محل النبضتين، ثم نتنبأ بالنموذج الجديد. طُبّقت الطريقة على التضخم البريطاني 2021–2024،
فبقيت التنبؤات جيدة حتى أفق 16 شهرًا رغم صدمات الطاقة.
"""
    )

st.markdown("## ▶️ محاكاة: تنبؤ يتعلم من أخطائه")
st.markdown("في المحاكاة ينكسر الاتجاه عند الخط الأحمر. اضغط ▶: في كل إطار يتقدم أصل التنبؤ فترة واحدة، ويختار النموذج "
            "أداته: أولًا النموذج القديم، ثم تصحيح القاطع بعد أول خطأ كبير، ثم الاتجاه المنكسر بعد خطأين.")
a, b = st.columns(2)
slope = a.slider("ميل الاتجاه الجديد بعد الكسر", 0.0, 1.0, 0.5, 0.05, key="fc_s")
seed = b.number_input("البذرة", 1, 99, 2, key="fc_seed")
rng = np.random.default_rng(int(seed))
T0, H = 60, 16
t = np.arange(T0 + H)
y = 10 + 0.1 * t + rng.normal(scale=0.4, size=len(t)) + slope * np.clip(t - T0 + 1, 0, None)
X = np.column_stack([np.ones(T0), np.arange(T0)])
b0 = np.linalg.lstsq(X, y[:T0], rcond=None)[0]
naive = b0[0] + b0[1] * t
frames = []
devices = []
for origin in range(T0, T0 + H):
    # broken-trend device: re-estimate with a broken trend starting at T0 once 2 post-break points exist
    if origin >= T0 + 2:
        Xb = np.column_stack([np.ones(origin), np.arange(origin), np.clip(np.arange(origin) - T0 + 1, 0, None)])
        bb = np.linalg.lstsq(Xb, y[:origin], rcond=None)[0]
        fc = bb[0] + bb[1] * t + bb[2] * np.clip(t - T0 + 1, 0, None)
        lab = "اتجاه منكسر"
    elif origin == T0 + 1:
        ic = y[T0] - naive[T0]
        fc = naive + ic
        lab = "تصحيح القاطع (نبضة)"
    else:
        fc = naive.copy()
        lab = "النموذج القديم"
    fc = np.where(t >= origin, fc, np.nan)
    devices.append(lab)
    frames.append(go.Frame(data=[go.Scatter(x=t[:origin], y=y[:origin]), go.Scatter(x=t, y=fc)], traces=[0, 2],
                           name=str(origin), layout=go.Layout(title=dict(text=f"أصل التنبؤ t = {origin}: {lab}"))))
fig = go.Figure()
fig.add_trace(go.Scatter(x=t[:T0], y=y[:T0], mode="lines+markers", marker=dict(size=4, color="#495057"),
                         line=dict(color="#495057"), name="المشاهدات المتاحة"))
fig.add_trace(go.Scatter(x=t, y=naive, mode="lines", line=dict(color="#adb5bd", dash="dot"), name="تنبؤ يتجاهل الكسر"))
fig.add_trace(go.Scatter(x=t, y=np.where(t >= T0, naive, np.nan), mode="lines", line=dict(color="#1c7ed6", width=3),
                         name="التنبؤ الحالي"))
fig.add_trace(go.Scatter(x=t, y=y, mode="markers", marker=dict(size=5, color="#fab005", symbol="x"), name="الواقع اللاحق"))
fig.add_vline(x=T0 - 0.5, line_dash="dash", line_color="#e03131", annotation_text="الكسر")
fig.frames = frames
fig.update_yaxes(range=[float(y.min()) - 1, float(y.max()) + 2])
figs._base_layout(fig, f"أصل التنبؤ t = {T0}: النموذج القديم", 460)
st.plotly_chart(figs._play_controls(fig, [f.name for f in frames], [f.name for f in frames], duration=900))
st.code("indsat y, ultra tpval(0.005)\nindsat forecast, h(12) graph\nindsat forecast, h(12) intercept   // مع تصحيح القاطع",
        language="stata")
with ui.box("warn", "أخطاء شائعة"):
    st.markdown("- الاعتماد على نموذج قُدّر قبل الأزمة دون تحديث: أخطر خطأ في التنبؤ.\n"
                "- تفسير خطأ كبير واحد على أنه كسر دائم: انتظر إشارة ثانية أو استخدم تصحيح القاطع أولًا.\n"
                "- نسيان أن الدرجة المحتفظ بها في نهاية العينة مقدّرة من مشاهدات قليلة، فخطؤها المعياري كبير.")
ui.check("لماذا لا تؤثر النبضة في التنبؤ؟", ["لأنها صغيرة", "لأنها تساوي صفرًا في كل الفترات بعد تاريخها",
                                            "لأنها تُحذف دائمًا", "تؤثر دائمًا"], 1,
         "النبضة تنتهي داخل العينة؛ أما الدرجة والاتجاه فيستمران إلى المستقبل.", "fc_q1")
ui.summary([
    "تحولات المستوى غير المنمذجة هي السبب الأول لفشل التنبؤات.",
    "النبضة لا تمتد إلى المستقبل؛ الدرجة والاتجاه المنكسر يمتدان.",
    "تصحيح القاطع أداة بسيطة وقوية بعد تحول مستوى.",
    "خطآن كبيران بالإشارة نفسها يشيران إلى انكسار اتجاه (Castle, Doornik & Hendry 2026).",
])
ui.nav_hint("التشبع في الانحدار وARDL")
