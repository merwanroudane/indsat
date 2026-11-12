from lib import typepage as tp
from lib import ui

tp.render(
    "MIS", "التشبع المضاعِف", "Multiplicative Indicator Saturation", "violet",
    r"M_j^{(k)}(t)=x_{k,t}\,S_j(t)\quad\Rightarrow\quad \beta_k(t)=\beta_k+\sum_j\gamma_j^{(k)}\,\mathbf 1(t\ge j)",
    "حين يتغير أثر متغير على آخر: كسور في المعاملات (الميول) وليس في القاطع",
    detects=["تغيّر المرونة أو الاستجابة: كسر في معامل x",
             "تغيّر درجة الاستمرارية (MIS على y متأخرًا)",
             "تغيّر قاعدة السياسة: استجابة الفائدة للتضخم في قاعدة تايلور"],
    use_when=["تشك في عدم ثبات معامل اقتصادي محدد",
              "بديل لـ Bai-Perron للتغير الهيكلي الجزئي دون تحديد عدد الكسور أو التشذيب",
              "مع الخيار common: كسر واحد في كل المعاملات في نفس التاريخ (تفسير الأنظمة)"],
    cautions=["المتغير الذي نشبّعه يجب أن يكون ضمن متغيرات النموذج",
              "التواريخ المتقاربة جدًا لا تُعرّف المعاملات: تُدمج تلقائيًا في common",
              "اقرأ النتيجة كمسار للمعامل β(t) عبر الزمن (الرسم يعرضه)"],
    examples=["Kitov & Tabor (2015): MIS في Autometrics",
              "Stillwagon (2025): تحولات السياسة النقدية الأمريكية 1972–2025 (حقبة Volcker)",
              "OxRegimes: MIS على متأخرات المتغير التابع مع تواريخ مشتركة"],
    demo=tp.demo_mis, demo_label="انحدار y على x يتغير فيه معامل x.", sizes=(0.0, 3.0, 1.5),
    stata="indsat y x z, mis(x) tpval(0.01)\nindsat y x z, sis mis(x z) common tpval(0.01)   // تواريخ مشتركة\n"
          "indsat path        // مسار المعامل β(t)\nindsat plot",
    r_code="# في gets: ابنِ المصفوفة يدويًا ومرّرها في uis\nS <- sim(y); M <- S * x\nm <- isat(y, mxreg = x, uis = M)",
    next_page="DIS و PIS",
)
ui.key_idea("القراءة الصحيحة: معامل كل مؤشر MIS هو **مقدار تغيّر الميل** ابتداءً من تاريخه. "
            "مسار المعامل الكامل = المعامل الأساسي + مجموع التغيرات النشطة حتى تلك الفترة.")
