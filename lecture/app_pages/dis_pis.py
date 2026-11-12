import streamlit as st

from lib import typepage as tp

choice = st.segmented_control("اختر النوع", ["DIS: النبضة المفرَّقة", "PIS: النبضة الزوجية"],
                              default="DIS: النبضة المفرَّقة", key="dp_choice")
if (choice or "").startswith("PIS"):
    tp.render(
        "PIS", "النبضات الزوجية", "Pairwise impulse indicator saturation", "red",
        r"P_i(t)=I_i(t)+I_{i+h}(t),\qquad i=1,\dots,T-h",
        "قيمتان شاذتان مرتبطتان بمسافة ثابتة h",
        detects=["قيمة شاذة في y داخل نموذج AR(1): تظهر في بواقي فترتين متتاليتين (h = 1)",
                 "نفس الفصل أو الشهر في سنتين متتاليتين (h = 4 أو 12)",
                 "حدث يتكرر بفاصل معروف"],
        use_when=["خطأ قياس في مستوى متغير يظهر في معادلة ديناميكية",
                  "حين تعطي IIS نبضتين متتاليتين بنفس الإشارة تقريبًا"],
        cautions=["اختر h من فهمك للبيانات", "مؤشر واحد بدل نبضتين يوفّر درجة حرية ويرفع القوة"],
        examples=["Ericsson (2011): النبضات الزوجية المتتالية وغير المتتالية",
                  "Johansen & Nielsen (2016): القيم الشاذة الإضافية مقابل الابتكارية"],
        demo=tp.demo_pis, demo_label="شذوذ مزدوج في فترتين متتاليتين.", sizes=(0.0, 6.0, 3.5),
        stata="indsat y, pis(1) tpval(0.01)\nindsat y, pis(12) tpval(0.01)   // بيانات شهرية",
        next_page="BIS: الكسور المصمَّمة",
    )
else:
    tp.render(
        "DIS", "النبضات المفرَّقة (صفرية المجموع)", "Differenced impulse indicator saturation", "green",
        r"Z_j(t)=I_j(t)-I_{j-1}(t)=\Delta I_j(t),\qquad \sum_t Z_j(t)=0",
        "قفزة تُعكس في الفترة التالية: ما يُضاف اليوم يُطرح غدًا",
        detects=["أخطاء التوقيت: نقل قيمة من فترة إلى أخرى",
                 "تقديم المشتريات قبل زيادة ضريبية ثم انخفاضها بعدها",
                 "نقل الإنتاج بين شهرين أو تأريخ مشاهدة خطأ"],
        use_when=["حين تظهر نبضتان متتاليتان بإشارتين متعاكستين وحجمين متقاربين",
                  "بيانات الإنفاق والإنتاج الحساسة للتوقيت"],
        cautions=["مؤشر واحد يلتقط زوجًا من النبضات المتعاكسة", "لا يغيّر المستوى طويل الأجل (مجموعه صفر)"],
        examples=["Ericsson (2011): differenced IIS أو zero-sum pairwise IIS",
                  "شراء السيارات قبل تغيير ضريبة القيمة المضافة"],
        demo=tp.demo_dis, demo_label="قفزة تنعكس في الفترة التالية.", sizes=(0.0, 6.0, 3.5),
        stata="indsat y, dis tpval(0.01)",
        next_page="BIS: الكسور المصمَّمة",
    )
