import streamlit as st

from lib import figs, sim
from lib import typepage as tp

tp.render(
    "BIS", "الكسور المصمَّمة", "Designed break-function saturation", "orange",
    r"d_j(t)=d(t-j+1)\ \ (1\le t-j+1\le L),\qquad d(t)=\frac{e^{-t}\big(e^{t(1-1/\gamma)}-1\big)}{1-1/\gamma}\ \ (\text{volcanic})",
    "حين نعرف مسبقًا «شكل» الصدمة ولا نعرف تاريخها",
    detects=["صدمات ذات شكل معروف: هبوط مفاجئ ثم تعافٍ تدريجي (ثورات البراكين)",
             "التغير المؤقت TC: صدمة تتلاشى هندسيًا δ^k (TRAMO، X-13)",
             "الانحدار الخطي المؤقت (ramp)، ومسار جائحة سابقة (path indicator saturation)"],
    use_when=["نظرية فيزيائية أو اقتصادية تحدد شكل الاستجابة",
              "الصدمات المتكررة بنفس النمط (أوبئة، كوارث، إضرابات)",
              "حين يكون الشكل صحيحًا تكون القوة أكبر بكثير من IIS"],
    cautions=["الشكل الخطأ يقلل القوة: جرّب أكثر من شكل", "طول الدالة L يؤثر في التفسير"],
    examples=["Pretis, Schneider, Smerdon & Hendry (2016): الثورات البركانية في درجات الحرارة",
              "Marczak & Proietti (2016): التغيرات المؤقتة في السلاسل الموسمية",
              "Castle, Doornik & Hendry (2020): مسار الجائحة لتوقعات كوفيد-19"],
    demo=tp.demo_bis, demo_label="صدمة بركانية مدفونة في الضجيج.", sizes=(0.0, 8.0, 5.0),
    stata="indsat temp, bis(volcanic) tpval(0.01)\nindsat y, bis(tc, delta(0.7)) tpval(0.01)\n"
          "indsat y, bis(ramp, length(4))\nindsat y, bis(, shape(1 .6 .3 .1))",
    next_page="UIS: مؤشرات المستخدم",
)
st.markdown("### :material/play_circle: قارن الأشكال المصمَّمة")
shape = st.segmented_control("الشكل", ["بركاني γ=0.5", "بركاني γ=3", "TC δ=0.7", "منحدر L=4"],
                             default="بركاني γ=0.5", key="bis_shape")
shapes = {"بركاني γ=0.5": sim.volcanic_shape(0.5, 3), "بركاني γ=3": sim.volcanic_shape(3, 4),
          "TC δ=0.7": sim.tc_shape(0.7, 10), "منحدر L=4": sim.ramp_shape(4)}
st.plotly_chart(figs.indicator_sweep("BIS", T=30, every=2, shape=shapes[shape or "بركاني γ=0.5"]),
                key=f"bis_sw_{shape}")
