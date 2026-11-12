from lib import typepage as tp

tp.render(
    "IIS", "تشبع مؤشرات النبضة", "Impulse Indicator Saturation", "orange",
    r"I_j(t)=\mathbf 1(t=j),\quad j=1,\dots,T \quad\Rightarrow\quad y_t=\beta'x_t+\sum_{j}\gamma_j I_j(t)+\varepsilon_t",
    "الأب المؤسس لعائلة التشبع: مؤشر لكل مشاهدة لاكتشاف القيم الشاذة",
    detects=["القيم الشاذة الإضافية (additive outliers) في مشاهدة واحدة",
             "الصدمات العابرة: إضراب، عطلة، كارثة، إعلان سياسة لمرة واحدة",
             "أخطاء القياس والإدخال",
             "يقرّب أي كسر آخر بسلسلة نبضات (لكن بقوة أقل من الشكل المطابق)"],
    use_when=["تريد تقديرات قوية (robust) لمعاملات النموذج ضد التلوث",
              "تريد قائمة موثقة بتواريخ القيم الشاذة وأحجامها",
              "قبل أي نموذج تطبيقي كتأمين رخيص: فقدان الكفاءة نحو 7% فقط عند α = 1%",
              "لاختبار وجود قيم شاذة أصلًا (اختبارات Jiao-Pretis)"],
    cautions=["سلسلة نبضات متتالية بإشارات متشابهة تعني غالبًا تحول مستوى: استخدم SIS أو super",
              "في النماذج الديناميكية، القيمة الشاذة في y تظهر في بواقي فترتين (انظر PIS)",
              "اختر α ≈ 1/T حتى لا يتراكم العدد الزائف"],
    examples=["Hendry (1999): الإنفاق على الغذاء في أمريكا، قيمتان شاذتان في الكساد والحرب",
              "سوق السمك في نيويورك (Johansen & Nielsen 2016): عطلات Boxing Day ويوم مارتن لوثر كينغ",
              "Marczak & Proietti (2016): القيم الشاذة في السلاسل الموسمية الأوروبية",
              "Che Rose et al. (2019): IIS في نموذج المستوى المحلي"],
    demo=tp.demo_outliers, demo_label="بيانات فيها ثلاث قيم شاذة.", sizes=(0.0, 8.0, 5.0),
    stata="indsat y x1 x2, iis tpval(0.01)\nindsat dates          // جدول القيم الشاذة\n"
          "indsat outlier        // اختبار Jiao-Pretis\nindsat distort        // هل غيّرت القيم الشاذة المعاملات؟",
    r_code="library(gets)\nm <- isat(y, mxreg = X, iis = TRUE, sis = FALSE, t.pval = 0.01)\noutliertest(m); distorttest(m)",
    next_page="SIS: تحولات المستوى",
)
