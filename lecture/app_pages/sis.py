from lib import typepage as tp

tp.render(
    "SIS", "تشبع مؤشرات الدرجة", "Step Indicator Saturation", "blue",
    r"S_j(t)=\mathbf 1(t\ge j)\ \ (\text{gets, indsat})\qquad\text{or}\qquad S_j(t)=\mathbf 1(t\le j)\ \ (\text{Autometrics})",
    "اكتشاف تحولات المستوى: متى تغيّر المتوسط، وبكم؟",
    detects=["تحولات المستوى (location shifts) بعدد وتواريخ وأحجام غير معروفة",
             "الأنظمة (regimes) المتتالية: كل نظام له متوسطه",
             "الكسور القريبة من طرفي العينة (حيث تضعف الطرق الأخرى)",
             "قيمة شاذة تُلتقط بدرجتين متتاليتين متعاكستين"],
    use_when=["تغيّر سياسة أو مؤسسة: تثبيت سعر صرف، إصلاح ضريبي، قانون جديد",
              "تغيّر طريقة القياس أو الإحصاء الرسمي",
              "بديل لـ Bai-Perron حين يكون عدد الكسور كبيرًا أو غير معروف",
              "تحليل أخطاء التنبؤ لمعرفة متى أصبح التنبؤ منحازًا"],
    cautions=["تباين الـ gauge أكبر من IIS (Nielsen & Qian 2025): استخدم α صغيرًا",
              "المعاملات المحتفظ بها متحيزة قليلًا بعد الاختيار: استخدم تصحيح التحيز",
              "انتبه لصيغة الدرجة (أعلى/أسفل) عند مقارنة البرمجيات"],
    examples=["نهر النيل 1871–1970: انخفاض التدفق بعد 1898 (سد أسوان)",
              "قانون حزام الأمان البريطاني 1983 وأعداد الضحايا",
              "Castle et al. (2015): كسور في الطلب على النقود",
              "Ericsson et al. (2022): تحولات في بيانات المناخ"],
    demo=tp.demo_shifts, demo_label="بيانات فيها تحولان في المستوى.", sizes=(0.0, 5.0, 2.5),
    stata="indsat y, sis tpval(0.01)\nindsat dates          // جدول الأنظمة (regimes)\n"
          "indsat test, hnull(0) biascorr graph\nindsat plot",
    r_code="m <- isat(y, sis = TRUE, t.pval = 0.01)\nisatdates(m); isattest(m, hnull = 0, biascorr = TRUE)",
    next_page="Super و Ultra",
)
