import numpy as np
import streamlit as st

from lib import figs, sim, ui

ui.header("فكرة التشبع: متغيرات أكثر من المشاهدات", "Saturation and the split-half algorithm",
          "كيف نقدّر نموذجًا فيه T مؤشرًا وT مشاهدة فقط؟ نقسّم المؤشرات إلى كتل", "green")

st.markdown(
    f"""
### الحيلة الذكية: {ui.t('خوارزمية النصفين', 'split-half algorithm')}
اقترحها Hendry وحلّلها Hendry وJohansen وSantos (2008). خطواتها لـ IIS:

1. **الكتلة الأولى:** أضف مؤشرات النصف الأول من العينة ($T/2$ نبضة) وقدّر النموذج — هذا ممكن لأن المعالم أقل من المشاهدات.
   احتفظ بالمؤشرات ذات $|t| > c_\\alpha$.
2. **الكتلة الثانية:** احذف تلك المؤشرات، وأضف مؤشرات النصف الثاني، وكرّر.
3. **الاتحاد:** اجمع المؤشرات المحتفظ بها من الكتلتين في نموذج واحد، واحذف ما لم يعد معنويًا.
"""
)
ui.key_idea("لماذا تعمل؟ إضافة نبضة لمشاهدة يعادل **حذف** تلك المشاهدة من التقدير. فالكتلة الأولى تقدّر النموذج "
            "من النصف الثاني فقط، ثم تختبر هل كل مشاهدة من النصف الأول «تتوافق» مع ذلك النموذج. "
            "هذا يشبه التحقق المتقاطع (cross-validation) الذي يكشف الشذوذ دون أن يتلوث به.")

st.markdown("## :material/play_circle: شاهد الخوارزمية خطوة بخطوة")
st.markdown("صمّم البيانات ثم اضغط ▶. **الأعلى:** البيانات والتوفيق في كل مرحلة، والكتلة الحالية مظللة. "
            "**الأسفل:** قيمة |t| لكل مؤشر مرشح؛ الملوَّن محتفظ به، والرمادي مستبعد، والخط الأحمر القيمة الحرجة.")
with st.container(border=True):
    a, b, c, d = st.columns(4)
    T = a.slider("عدد المشاهدات T", 40, 150, 80, 10, key="sat_T")
    o_size = b.slider("حجم القيمة الشاذة", 0.0, 10.0, 6.0, 0.5, key="sat_o")
    s_size = c.slider("حجم تحول المستوى", 0.0, 6.0, 3.0, 0.5, key="sat_s")
    alpha = d.select_slider("مستوى الدلالة المستهدف α", [0.001, 0.005, 0.01, 0.025, 0.05], 0.01, key="sat_a")
    kinds = st.pills("أنواع المؤشرات", ["IIS", "SIS"], selection_mode="multi", default=["IIS"], key="sat_k")
    seed = st.number_input("البذرة العشوائية", 1, 999, 3, key="sat_seed")

kinds = kinds or ["IIS"]
t, y, x, mu = sim.dgp(T, seed=int(seed), outliers=[(int(T * 0.3), o_size)] if o_size else None,
                      shifts=[(int(T * 0.65), s_size)] if s_size else None)
sets = [(k, *sim.build_set(k, T)) for k in kinds]
res = figs.run_search(y, np.ones((T, 1)), sets, alpha)
st.plotly_chart(figs.search_animation(t, y, res, mu), key=f"satanim_{T}_{o_size}_{s_size}_{alpha}_{kinds}_{seed}")

kinds_found = res.__dict__["_all_kinds"]
found = ", ".join(f"{kinds_found[j]} عند t={tau}" for j, tau in zip(res.selected, res.taus)) or "لا شيء"
st.markdown(f"**النتيجة:** المؤشرات المحتفظ بها: {found}. "
            f"الحقيقة: شذوذ عند t={int(T * 0.3)} وتحول عند t={int(T * 0.65)}.")
if kinds == ["IIS"] and s_size >= 2:
    ui.warn("لاحظ: مع IIS وحده يُلتقط تحول المستوى بسلسلة من النبضات (إن التُقط أصلًا). جرّب إضافة SIS.")

st.markdown("## :material/functions: النتيجة النظرية الأساسية")
st.markdown(
    r"""
تحت الفرضية العدمية (لا قيم شاذة)، كل نبضة تُختبر بمستوى $\alpha$، فعدد المؤشرات الزائفة المحتفظ بها

$$E[\text{عدد الزائفة}] = \alpha T .$$

مثلًا: $T=100$ و$\alpha=0.01$ يعني **مؤشرًا زائفًا واحدًا في المتوسط** — وهو ثمن زهيد مقابل الحماية من كل القيم الشاذة الممكنة.
هذه هي نتيجة Hendry وJohansen وSantos (2008)، وهي أساس مفهوم الـ **gauge** في الدرس بعد التالي.
"""
)
with st.expander("من النصفين إلى J كتلة (كيف تعمل البرمجيات الحديثة؟)"):
    st.markdown(
        """
- **gets/isat وindsat:** عدد الكتل يُحدَّد من نسبة (ratio threshold) وحد أقصى لحجم الكتلة (عادة 30)،
  وداخل كل كتلة يُجرى بحث متعدد المسارات (GETS)، ثم بحث على الاتحاد.
- **Autometrics:** بحث شجري يضيف ويحذف كتلًا مع اختبارات تشخيصية (backtesting).
- **الخلاصة:** الكتل الأكثر والبحث متعدد المسارات يزيدان القوة، لكن المبدأ هو نفسه مبدأ النصفين.
"""
    )
ui.nav_hint("البحث من العام إلى الخاص")
