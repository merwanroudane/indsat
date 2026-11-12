import numpy as np
import plotly.graph_objects as go
import streamlit as st

from lib import figs, ui

ui.header("التنبؤ بعد الكسور", "Forecasting after breaks and large forecast errors",
          "المؤشرات ليست للماضي فقط: هي أدوات لإعادة التنبؤ إلى المسار الصحيح", "blue")

st.markdown(
    f"""
### :material/insights: ماذا يحدث للتنبؤ بعد كسر؟
- **النبضة** تنتهي داخل العينة، فلا تؤثر في التنبؤ.
- **الدرجة** تستمر: المستوى الجديد يُنقل إلى المستقبل (لذلك يفضّل البعض صيغة 1(t ≤ j) حتى لا تمتد للتنبؤ).
- **الاتجاه المنكسر** يستمر بميله الجديد.
- {ui.t('تصحيح القاطع', 'intercept correction')}: إضافة آخر خطأ تنبؤ إلى التنبؤات اللاحقة (Hendry & Clements 1994).

### الفكرة الجديدة (Castle, Doornik & Hendry 2026)
خطأ تنبؤ كبير واحد يحمل معلومة ثمينة. نضيف **نبضة** عند أصل التنبؤ (تصحيح للقاطع). إذا تبعه خطأ كبير آخر
بنفس الإشارة، فالأرجح أنه **انكسار اتجاه**؛ نختبر هل تحل الدرجة أو الاتجاه المنكسر الخطي/اللوغاريتمي محل
النبضتين، ثم نتنبأ بالنموذج الجديد. طُبّق ذلك على التضخم البريطاني 2021–2024 فتنبأ جيدًا حتى 16 شهرًا.
"""
)
st.markdown("## :material/play_circle: محاكاة: تنبؤ يتعلم من أخطائه")
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
ui.nav_hint("التشبع في الانحدار وARDL")
