from lib import typepage as tp

tp.render(
    "TIS", "تشبع الاتجاهات المنكسرة (و QIS / CIS)", "Trend Indicator Saturation", "green",
    r"T_j(t)=(t-j+1)\,\mathbf 1(t\ge j),\quad Q_j(t)=(t-j+1)^2\,\mathbf 1(t\ge j),\quad C_j(t)=(t-j+1)^3\,\mathbf 1(t\ge j)",
    "حين يتغير معدل النمو — الميل — وليس المستوى فقط",
    detects=["انكسار الاتجاه الخطي: تباطؤ أو تسارع النمو بعد تاريخ معين",
             "QIS/CIS: تسارع أو انحناء الاتجاه (اتجاهات تربيعية وتكعيبية منكسرة)",
             "التحولات البطيئة التي تبدو في IIS/SIS كسلسلة طويلة من المؤشرات"],
    use_when=["السلاسل ذات الاتجاه: الإنتاجية، الناتج، الأسعار باللوغاريتم، درجات الحرارة",
              "التنبؤ بعد أخطاء كبيرة متزايدة في اتجاه واحد (Castle, Doornik & Hendry 2026)",
              "تقييم نماذج المناخ (Pretis, Mann & Kaufmann 2015)"],
    cautions=["الاتجاهات المنكسرة شديدة الترابط؛ البرمجيات تعيد قياسها أثناء البحث",
              "QIS/CIS تحتاج كتلًا صغيرة (indsat يستخدم 15 و8 تلقائيًا)",
              "اجمعه مع SIS حين يتغير المستوى والميل معًا (ultra)"],
    examples=["التضخم البريطاني 2021–2024: اتجاهات لوغاريتمية منكسرة بعد كل صدمة",
              "Ericsson et al. (2022): انكسار اتجاه درجات الحرارة",
              "تباطؤ الإنتاجية البريطانية بعد 2008 (Nielsen & Qian 2025)"],
    demo=tp.demo_trend, demo_label="سلسلة ينكسر اتجاهها.", sizes=(0.0, 4.0, 2.0),
    stata="indsat y, tis tpval(0.01)\nindsat y, qis tpval(0.005)      // تربيعي\n"
          "indsat y, cis tpval(0.005)      // تكعيبي\nindsat forecast, h(12) graph",
    r_code="m <- isat(y, sis = FALSE, tis = TRUE, t.pval = 0.01)",
    next_page="MIS: كسور المعاملات",
)
