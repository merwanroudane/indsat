from lib import typepage as tp
from lib import ui

ui.key_idea("التسمية: super saturation = IIS + SIS؛ ultra saturation (وتسمى أحيانًا «super duper») = IIS + SIS + TIS. "
            "المصطلحان لـ Ericsson (2011).")
tp.render(
    "Super", "التشبع الفائق (IIS + SIS)", "Super saturation", "violet",
    r"D=\big[\,I_1,\dots,I_T\ \big|\ S_2,\dots,S_T\,\big]\qquad\text{(ultra: }+\ T_2,\dots,T_T\text{)}",
    "حين تجتمع القيم الشاذة وتحولات المستوى في نفس السلسلة — وهي الحالة الغالبة",
    detects=["القيم الشاذة وتحولات المستوى معًا دون خلط أحدهما بالآخر",
             "Ultra: يضيف انكسارات الاتجاه إلى ذلك",
             "مزيج الأحداث في السلاسل الاقتصادية الكلية والطاقة والمناخ"],
    use_when=["لا تعرف هل المشكلة شذوذ أم تحول مستوى (الحالة الافتراضية الآمنة)",
              "Ultra للسلاسل ذات الاتجاه (لوغاريتم المستويات، درجات الحرارة، CO2)",
              "تحليل أخطاء التنبؤ (Ericsson & Reisman 2012)"],
    cautions=["عدد المرشحين يتضاعف (2T أو 3T) فيتضاعف العدد الزائف المتوقع: شدّد α",
              "كل مجموعة تُبحث بكتل منفصلة ثم تُجمع الناجيات في بحث نهائي واحد"],
    examples=["Kurle (2025): دراسة مونت كارلو شاملة لـ super saturation",
              "Ericsson, Dore & Butt (2022): ultra saturation لبيانات المناخ",
              "Castle, Doornik & Hendry (2026): التضخم البريطاني 2021–2024"],
    demo=tp.demo_super, demo_label="بيانات فيها قيمة شاذة وتحول مستوى معًا.", sizes=(0.0, 5.0, 3.0),
    stata="indsat y x, super tpval(0.005)       // = iis sis\nindsat y x, ultra tpval(0.005)       // = iis sis tis\n"
          "indsat sim, saturation(iis sis) sizes(0 1 2 3 4)",
    r_code="m <- isat(y, mxreg = X, iis = TRUE, sis = TRUE, tis = FALSE, t.pval = 0.005)",
    next_page="TIS: الاتجاهات المنكسرة",
)
