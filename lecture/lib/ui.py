"""Shared UI helpers: right-hand sidebar + Arabic right-to-left layout, bilingual terms."""
from __future__ import annotations

import streamlit as st

# Requested by the user: sidebar on the right and Arabic (RTL) reading direction.
# Formulas, code and charts stay left-to-right.
RTL_CSS = """
<style>
[data-testid="stAppViewContainer"] { flex-direction: row-reverse; }
[data-testid="stSidebar"] { border-left: 1px solid #e9ecef; border-right: none; }
[data-testid="stMain"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebarNav"], [data-testid="stWidgetLabel"],
[data-testid="stExpander"] summary, [data-testid="stAlert"],
[data-testid="stTabs"] [role="tablist"], [data-testid="stCaptionContainer"],
[data-testid="stMetric"], h1, h2, h3, h4, h5 {
    direction: rtl; text-align: right;
}
[data-testid="stSidebarNav"] a { flex-direction: row-reverse; }
/* direction alone does not reorder inline content: unicode-bidi isolate makes each formula
   an independent left-to-right run inside the right-to-left Arabic paragraph */
.katex-display, .katex, code, pre, [data-testid="stCode"], .js-plotly-plot, .ltr {
    direction: ltr !important; unicode-bidi: isolate !important; text-align: left;
}
.katex .katex-html, .katex .base { direction: ltr !important; unicode-bidi: isolate; }
.katex-display { text-align: center !important; }
[data-testid="stMarkdownContainer"] ul, [data-testid="stMarkdownContainer"] ol {
    padding-right: 1.3rem; padding-left: 0;
}
</style>
"""


def setup() -> None:
    st.html(RTL_CSS)


def t(ar: str, en: str) -> str:
    """Arabic term with its English equivalent."""
    return f"**{ar}** :gray[({en})]"


def header(ar: str, en: str, lead: str, color: str = "blue") -> None:
    st.markdown(f"# {ar}")
    st.markdown(f":{color}-badge[{en}]")
    st.markdown(f"#### {lead}")


def key_idea(text: str) -> None:
    st.info(text, icon=":material/lightbulb:")


def warn(text: str) -> None:
    st.warning(text, icon=":material/warning:")


def good(text: str) -> None:
    st.success(text, icon=":material/verified:")


def card(title: str, body: str, formula: str | None = None, icon: str = ":material/info:") -> None:
    with st.container(border=True):
        st.markdown(f"##### {title}")
        st.markdown(body)
        if formula:
            st.latex(formula)


def type_card(code: str, ar: str, en: str, color: str, detects: str, formula: str, use_when: str) -> None:
    with st.container(border=True):
        st.markdown(f"### :{color}[{code}] — {ar}")
        st.markdown(f":{color}-badge[{en}]")
        st.latex(formula)
        st.markdown(f"**ماذا يكشف؟** {detects}")
        st.markdown(f"**متى نستخدمه؟** {use_when}")


def nav_hint(next_page: str) -> None:
    st.divider()
    st.caption(f"الدرس التالي: {next_page}  ←  استخدم القائمة الجانبية على اليمين")


def stata(code: str) -> None:
    st.code(code, language="stata")
