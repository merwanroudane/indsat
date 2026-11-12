import streamlit as st

from lib import figs, ui

ui.header("المؤشرات الوهمية: حجر البناء", "Indicator (dummy) variables",
          "قبل التشبع يجب أن نفهم المؤشر الواحد: متغير يساوي صفرًا إلا في فترة محددة", "green")

st.markdown(
    f"""
{ui.t('المؤشر', 'indicator / dummy variable')} متغير مصطنع نضيفه إلى الانحدار ليلتقط حدثًا في تاريخ معين.
إذا أضفنا المؤشر $d_j(t)$ إلى النموذج

$$y_t = \\beta' x_t + \\gamma_j\\, d_j(t) + \\varepsilon_t$$

فإن معامله $\\gamma_j$ يقيس **حجم الحدث**، واختبار $t$ عليه يقول هل الحدث **معنوي** إحصائيًا.
الأشكال الثلاثة الأساسية:
"""
)
c1, c2, c3 = st.columns(3)
with c1:
    ui.card(":orange[النبضة] :gray[(impulse)]", "تساوي 1 في الفترة j فقط. تلتقط قيمة شاذة.",
            r"I_j(t)=\mathbf 1(t=j)")
with c2:
    ui.card(":blue[الدرجة] :gray[(step)]", "تساوي 1 من الفترة j فصاعدًا. تلتقط تحوّل المستوى.",
            r"S_j(t)=\mathbf 1(t\ge j)")
with c3:
    ui.card(":green[الاتجاه المنكسر] :gray[(broken trend)]", "تبدأ بالارتفاع خطيًا من j. تلتقط تغيّر الميل.",
            r"T_j(t)=(t-j+1)\,\mathbf 1(t\ge j)")

ui.key_idea("العلاقة الذهبية: الدرجة = مجموع نبضات متتالية، والاتجاه المنكسر = مجموع درجات متتالية. "
            "لذلك يمكن للنبضات تقريب أي كسر، لكن الشكل المطابق يحتاج مؤشرًا واحدًا فقط فيكون أقوى بكثير.")

st.markdown("## :material/play_circle: شاهد المؤشر يتحرك عبر الزمن")
st.markdown("اختر النوع ثم اضغط ▶. كل إطار يعرض مؤشرًا يبدأ في تاريخ مختلف؛ "
            "**التشبع** يعني أن نضع كل هذه الأعمدة في النموذج دفعة واحدة.")
kind = st.segmented_control("نوع المؤشر", ["IIS", "SIS", "TIS", "QIS", "DIS", "PIS", "BIS", "MIS"],
                            default="IIS", key="ind_kind")
names = {"IIS": "نبضة", "SIS": "درجة", "TIS": "اتجاه منكسر", "QIS": "اتجاه تربيعي منكسر", "DIS": "نبضة مفرَّقة",
         "PIS": "نبضة زوجية", "BIS": "دالة مصمَّمة (بركانية)", "MIS": "درجة مضروبة في متغير x"}
st.caption(f"النوع المعروض: **{names[kind or 'IIS']}**")
st.plotly_chart(figs.indicator_sweep(kind or "IIS"), key=f"sweep_{kind}")

st.markdown("## :material/grid_on: مصفوفة التشبع")
st.markdown(
    r"""
عندما نجمع كل المؤشرات من نوع واحد نحصل على مصفوفة مربعة تقريبًا $D=(d_1,\dots,d_T)$:

$$D_{IIS}=I_T=\begin{pmatrix}1&0&\cdots&0\\0&1&\cdots&0\\\vdots&&\ddots&\vdots\\0&0&\cdots&1\end{pmatrix},\qquad
D_{SIS}=\begin{pmatrix}0&0&\cdots&0\\1&0&\cdots&0\\1&1&\cdots&0\\\vdots&&\ddots&\vdots\\1&1&\cdots&1\end{pmatrix}$$

النموذج المشبَّع $y = X\beta + D\gamma + \varepsilon$ فيه $k + T$ معلمة مقابل $T$ مشاهدة فقط:
**لا يمكن تقديره بالمربعات الصغرى مباشرة**. الحل في الدرس التالي.
"""
)
ui.warn("ملاحظة عملية: صيغة الدرجة تختلف بين البرمجيات. حزمة gets في R وindsat يستخدمان 1(t ≥ j)، "
        "وAutometrics وCastle et al. (2015) يستخدمان 1(t ≤ j). المعنى واحد لكن إشارة المعامل تنقلب.")
ui.nav_hint("فكرة التشبع والانقسام")
