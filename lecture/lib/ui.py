"""Design system of the lecture: right-to-left Arabic layout, right-hand sidebar, coloured
lesson banners and boxes (definition, analogy, example, warning, tip, summary, think),
numbered steps, term chips and small self-check questions.

The user explicitly asked for a custom, colourful design, so CSS is used here. Boxes are
native Streamlit containers whose `key` gives a CSS class (st-key-...), so Markdown and
LaTeX keep working inside them.
"""
from __future__ import annotations

import html
import re

import streamlit as st

# --------------------------------------------------------------------------- palette
THEMES = {
    "blue":   ("#e7f5ff", "#1c7ed6", "#d0ebff"),
    "teal":   ("#e6fcf5", "#0ca678", "#c3fae8"),
    "green":  ("#ebfbee", "#2f9e44", "#d3f9d8"),
    "orange": ("#fff4e6", "#e8590c", "#ffe8cc"),
    "violet": ("#f8f0fc", "#ae3ec9", "#f3d9fa"),
    "pink":   ("#fff0f6", "#d6336c", "#ffdeeb"),
    "yellow": ("#fff9db", "#f08c00", "#fff3bf"),
    "indigo": ("#edf2ff", "#4263eb", "#dbe4ff"),
    "red":    ("#fff5f5", "#e03131", "#ffe3e3"),
    "gray":   ("#f8f9fa", "#495057", "#e9ecef"),
}

BOX = {  # kind: (label, icon, theme)
    "def":     ("تعريف", "📘", "blue"),
    "analogy": ("تشبيه من الحياة", "💡", "yellow"),
    "example": ("مثال محلول", "🧮", "green"),
    "warn":    ("انتبه", "⚠️", "orange"),
    "tip":     ("نصيحة عملية", "🛠️", "teal"),
    "summary": ("خلاصة", "📌", "violet"),
    "think":   ("توقف وفكّر", "🤔", "pink"),
    "formula": ("الصيغة", "∑", "indigo"),
    "story":   ("قصة من التاريخ", "📜", "gray"),
    "why":     ("لماذا يهم هذا؟", "🎯", "red"),
}


def _box_css() -> str:
    rules = []
    for kind, (_, _, theme) in BOX.items():
        bg, accent, _ = THEMES[theme]
        rules.append(
            f'div[class*="st-key-box-{kind}-"] {{ background:{bg}; border-right:6px solid {accent};'
            f' border-radius:16px; padding:1.1rem 1.4rem 0.6rem 1.4rem; margin:0.4rem 0 0.9rem 0;'
            f' box-shadow:0 1px 3px rgba(0,0,0,0.05); }}\n'
            f'div[class*="st-key-box-{kind}-"] .box-title {{ color:{accent}; font-weight:700; font-size:1.05rem;'
            f' margin-bottom:0.3rem; }}'
        )
    return "\n".join(rules)


CSS = f"""
<style>
/* --- right-hand sidebar and Arabic right-to-left reading (requested by the user) --- */
[data-testid="stAppViewContainer"] {{ flex-direction: row-reverse; }}
[data-testid="stSidebar"] {{ border-left: 1px solid #dbe4ff; border-right: none; }}
[data-testid="stMain"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebarNav"], [data-testid="stWidgetLabel"],
[data-testid="stExpander"] summary, [data-testid="stAlert"],
[data-testid="stTabs"] [role="tablist"], [data-testid="stCaptionContainer"],
[data-testid="stMetric"], h1, h2, h3, h4, h5 {{ direction: rtl; text-align: right; }}
[data-testid="stSidebarNav"] a {{ flex-direction: row-reverse; }}
/* formulas, code and charts stay left-to-right: isolate them inside the Arabic paragraph */
.katex-display, .katex, code, pre, [data-testid="stCode"], .js-plotly-plot, .ltr {{
    direction: ltr !important; unicode-bidi: isolate !important; text-align: left;
}}
.katex .katex-html, .katex .base {{ direction: ltr !important; unicode-bidi: isolate; }}
.katex-display {{ text-align: center !important; }}
[data-testid="stMarkdownContainer"] ul, [data-testid="stMarkdownContainer"] ol {{
    padding-right: 1.4rem; padding-left: 0;
}}
/* --- comfortable reading --- */
[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
[data-testid="stMain"] [data-testid="stMarkdownContainer"] li {{ line-height: 2.0; font-size: 1.04rem; }}
[data-testid="stMain"] .block-container {{ max-width: 1180px; padding-top: 1.5rem; }}
h2 {{ margin-top: 1.6rem !important; }}
/* --- coloured boxes --- */
{_box_css()}
/* --- lesson banner --- */
.hero {{ border-radius: 22px; padding: 1.6rem 2rem; margin-bottom: 1.2rem; direction: rtl; text-align: right;
         box-shadow: 0 4px 14px rgba(28,126,214,0.10); }}
.hero .num {{ display:inline-block; font-size:0.85rem; font-weight:700; padding:0.2rem 0.8rem; border-radius:999px;
              background:rgba(255,255,255,0.75); margin-bottom:0.6rem; }}
.hero h1 {{ font-size: 2.1rem; margin: 0.2rem 0 0.3rem 0; line-height: 1.5; }}
.hero .en {{ font-size: 1.0rem; opacity: 0.8; direction: ltr; unicode-bidi: isolate; font-weight:600; }}
.hero p {{ font-size: 1.12rem; margin: 0.6rem 0 0 0; line-height: 1.9; }}
/* --- objectives, steps, chips --- */
.obj {{ background:#ffffff; border:1px dashed #91a7ff; border-radius:16px; padding:1rem 1.4rem; margin-bottom:1rem;
        direction: rtl; text-align: right; }}
.obj b {{ color:#4263eb; }}
.obj ul {{ margin: 0.4rem 0 0 0; padding-right: 1.3rem; line-height: 2; }}
.steps {{ direction: rtl; text-align: right; margin: 0.4rem 0 1rem 0; }}
.step {{ display:flex; gap:0.9rem; align-items:flex-start; background:#ffffff; border:1px solid #e9ecef;
         border-radius:14px; padding:0.8rem 1rem; margin-bottom:0.55rem; }}
.step .n {{ min-width:2.1rem; height:2.1rem; border-radius:50%; color:#fff; font-weight:700; display:flex;
            align-items:center; justify-content:center; font-size:1rem; }}
.step .t b {{ font-size:1.04rem; }}
.step .t {{ line-height:1.9; }}
.chips {{ direction: rtl; text-align: right; margin: 0.3rem 0 0.8rem 0; }}
.chip {{ display:inline-block; padding:0.25rem 0.75rem; margin:0.2rem; border-radius:999px; font-size:0.92rem;
         border:1px solid; }}
.chip .en {{ direction: ltr; unicode-bidi: isolate; opacity:0.75; font-size:0.85rem; }}
.path {{ display:flex; flex-wrap:wrap; gap:0.6rem; direction: rtl; margin: 0.6rem 0 1rem 0; }}
.path .stage {{ flex:1 1 180px; border-radius:16px; padding:0.9rem 1rem; text-align:right; }}
.path .stage .h {{ font-weight:700; font-size:1.02rem; margin-bottom:0.3rem; }}
.path .stage .b {{ font-size:0.95rem; line-height:1.8; }}
</style>
"""

_PALETTE_CYCLE = ["blue", "green", "orange", "violet", "teal", "pink", "indigo", "yellow"]


def _md(s: str) -> str:
    """Escape text for HTML cards but keep **bold** from the lesson prose."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(s))


def setup() -> None:
    st.html(CSS)


def _next_id() -> int:
    st.session_state["_ui_box_counter"] = st.session_state.get("_ui_box_counter", 0) + 1
    return st.session_state["_ui_box_counter"]


# --------------------------------------------------------------------------- page parts


def hero(num: str, title: str, en: str, lead: str, theme: str = "blue") -> None:
    """Coloured lesson banner."""
    bg, accent, mid = THEMES[theme]
    st.session_state["_ui_box_counter"] = 0
    st.html(
        f'<div class="hero" style="background:linear-gradient(120deg,{bg} 0%,{mid} 100%);'
        f'border-right:8px solid {accent};">'
        f'<span class="num" style="color:{accent};">{html.escape(num)}</span>'
        f'<h1 style="color:#1f2a44;">{html.escape(title)}</h1>'
        f'<div class="en" style="color:{accent};">{html.escape(en)}</div>'
        f'<p style="color:#343a40;">{_md(lead)}</p></div>'
    )


def objectives(items: list[str], minutes: int | None = None) -> None:
    lis = "".join(f"<li>{_md(i)}</li>" for i in items)
    tm = f" · مدة الدرس نحو {minutes} دقيقة" if minutes else ""
    st.html(f'<div class="obj"><b>🎯 في هذا الدرس ستتعلم{tm}</b><ul>{lis}</ul></div>')


def box(kind: str, title: str = ""):
    """Coloured container; use as `with ui.box("def", "..."):` and write Markdown/LaTeX inside."""
    label, icon, _ = BOX[kind]
    c = st.container(key=f"box-{kind}-{_next_id()}")
    head = f"{icon} {label}" + (f": {title}" if title else "")
    c.html(f'<div class="box-title" style="direction:rtl;text-align:right;">{html.escape(head)}</div>')
    return c


def steps(items: list[tuple[str, str]], theme: str = "blue") -> None:
    """Numbered steps. items: (bold title, plain explanation)."""
    _, accent, _ = THEMES[theme]
    out = []
    for i, (h, b) in enumerate(items, 1):
        out.append(f'<div class="step"><div class="n" style="background:{accent};">{i}</div>'
                   f'<div class="t"><b>{html.escape(h)}</b><br>{_md(b)}</div></div>')
    st.html('<div class="steps">' + "".join(out) + "</div>")


def chips(terms: list[tuple[str, str]]) -> None:
    """Term chips: (Arabic, English)."""
    out = []
    for i, (ar, en) in enumerate(terms):
        bg, accent, _ = THEMES[_PALETTE_CYCLE[i % len(_PALETTE_CYCLE)]]
        out.append(f'<span class="chip" style="background:{bg};border-color:{accent};color:{accent};">'
                   f'{html.escape(ar)} <span class="en">({html.escape(en)})</span></span>')
    st.html('<div class="chips">' + "".join(out) + "</div>")


def path(stages: list[tuple[str, str]], themes: list[str] | None = None) -> None:
    """A row of coloured stage cards (learning path)."""
    themes = themes or _PALETTE_CYCLE
    out = []
    for i, (h, b) in enumerate(stages):
        bg, accent, _ = THEMES[themes[i % len(themes)]]
        out.append(f'<div class="stage" style="background:{bg};border-top:5px solid {accent};">'
                   f'<div class="h" style="color:{accent};">{html.escape(h)}</div>'
                   f'<div class="b">{_md(b)}</div></div>')
    st.html('<div class="path">' + "".join(out) + "</div>")


def check(question: str, options: list[str], answer: int, explanation: str, key: str) -> None:
    """A self-check question with immediate feedback."""
    with box("think", question):
        choice = st.radio("اختر الإجابة", options, index=None, key=key, label_visibility="collapsed")
        if choice is not None:
            if options.index(choice) == answer:
                st.success(f"إجابة صحيحة. {explanation}", icon=":material/check_circle:")
            else:
                st.error(f"ليست هذه. الصحيح: {options[answer]}. {explanation}", icon=":material/cancel:")


def summary(points: list[str]) -> None:
    with box("summary", "خلاصة الدرس"):
        st.markdown("\n".join(f"- {p}" for p in points))


def t(ar: str, en: str) -> str:
    """Arabic term with its English equivalent, for Markdown."""
    return f"**{ar}** :gray[({en})]"


def nav_hint(next_page: str) -> None:
    st.divider()
    st.caption(f"الدرس التالي ←  {next_page}  (من القائمة الجانبية على اليمين)")


# ---- backward-compatible helpers used by some pages ---------------------------------


def header(ar: str, en: str, lead: str, color: str = "blue") -> None:
    hero("", ar, en, lead, {"gray": "gray"}.get(color, color if color in THEMES else "blue"))


def key_idea(text: str) -> None:
    with box("tip"):
        st.markdown(text)


def warn(text: str) -> None:
    with box("warn"):
        st.markdown(text)


def good(text: str) -> None:
    st.success(text, icon=":material/verified:")


def card(title: str, body: str, formula: str | None = None, icon: str = "") -> None:
    with st.container(border=True):
        st.markdown(f"##### {title}")
        st.markdown(body)
        if formula:
            st.latex(formula)
