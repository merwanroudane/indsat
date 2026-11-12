"""Indicator saturation: an interactive lecture from zero (Arabic, with English terms)."""
import streamlit as st

from lib import ui

st.set_page_config(page_title="محاضرة: تشبع المؤشرات | Indicator saturation", page_icon=":material/school:",
                   layout="wide", initial_sidebar_state="expanded")
ui.setup()

P = "app_pages/"
pages = {
    "البداية": [
        st.Page(P + "home.py", title="مرحبًا: خريطة المحاضرة", icon=":material/home:", default=True),
        st.Page(P + "history.py", title="تاريخ المنهجية", icon=":material/history:"),
        st.Page(P + "why.py", title="لماذا نحتاجها؟", icon=":material/help:"),
    ],
    "المفاهيم الأساسية": [
        st.Page(P + "indicators.py", title="المؤشرات الوهمية", icon=":material/category:"),
        st.Page(P + "saturation.py", title="فكرة التشبع والانقسام", icon=":material/call_split:"),
        st.Page(P + "gets.py", title="البحث من العام إلى الخاص", icon=":material/account_tree:"),
        st.Page(P + "gauge.py", title="المقياس والقوة", icon=":material/tune:"),
        st.Page(P + "theory.py", title="النظرية الإحصائية", icon=":material/functions:"),
    ],
    "أنواع التشبع": [
        st.Page(P + "iis.py", title="IIS: النبضات والقيم الشاذة", icon=":material/bolt:"),
        st.Page(P + "sis.py", title="SIS: تحولات المستوى", icon=":material/stairs:"),
        st.Page(P + "super_ultra.py", title="Super و Ultra", icon=":material/layers:"),
        st.Page(P + "trends.py", title="TIS: الاتجاهات المنكسرة", icon=":material/trending_up:"),
        st.Page(P + "mis.py", title="MIS: كسور المعاملات", icon=":material/scatter_plot:"),
        st.Page(P + "dis_pis.py", title="DIS و PIS", icon=":material/compare_arrows:"),
        st.Page(P + "bis.py", title="BIS: الكسور المصمَّمة", icon=":material/volcano:"),
        st.Page(P + "uis.py", title="UIS: مؤشرات المستخدم", icon=":material/build:"),
    ],
    "ما بعد التقدير": [
        st.Page(P + "tests.py", title="اختبارات القيم الشاذة", icon=":material/fact_check:"),
        st.Page(P + "bias_path.py", title="تصحيح التحيز ومسار المعامل", icon=":material/auto_graph:"),
        st.Page(P + "forecast.py", title="التنبؤ بعد الكسور", icon=":material/insights:"),
        st.Page(P + "regression.py", title="التشبع في الانحدار وARDL", icon=":material/multiline_chart:"),
    ],
    "التطبيق والمراجعة": [
        st.Page(P + "lab.py", title="المختبر: جرّب بنفسك", icon=":material/science:"),
        st.Page(P + "compare.py", title="مقارنة مع الطرق الأخرى", icon=":material/difference:"),
        st.Page(P + "guide.py", title="دليل اختيار النوع", icon=":material/route:"),
        st.Page(P + "software.py", title="البرمجيات والأوامر", icon=":material/code:"),
        st.Page(P + "glossary.py", title="قاموس المصطلحات", icon=":material/translate:"),
        st.Page(P + "quiz.py", title="اختبر نفسك", icon=":material/quiz:"),
        st.Page(P + "references.py", title="المراجع", icon=":material/library_books:"),
    ],
}

with st.sidebar:
    st.markdown("### :material/school: تشبع المؤشرات")
    st.caption("Indicator Saturation — محاضرة تفاعلية من الصفر")
    st.link_button("مكتبة indsat على GitHub", "https://github.com/merwanroudane/indsat",
                   icon=":material/code:", width="stretch")

page = st.navigation(pages, position="sidebar", expanded=True)
page.run()
