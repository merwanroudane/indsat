"""Template used by every 'type of saturation' lesson."""
from __future__ import annotations

from typing import Callable

import numpy as np
import streamlit as st

from . import figs, sim, ui


def render(code: str, ar: str, en: str, color: str, formula: str, intro: str,
           detects: list[str], use_when: list[str], cautions: list[str], examples: list[str],
           demo: Callable[[float, int, int], tuple] | None, demo_label: str, sizes: tuple[float, float, float],
           stata: str, r_code: str | None = None, next_page: str = "") -> None:
    ui.header(f"{code}: {ar}", en, intro, color)
    st.markdown("### :material/functions: التعريف")
    st.latex(formula)

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown(f"#### :{color}[ماذا يكشف؟]")
            st.markdown("\n".join(f"- {d}" for d in detects))
        with st.container(border=True):
            st.markdown("#### :orange[تنبيهات]")
            st.markdown("\n".join(f"- {d}" for d in cautions))
    with c2:
        with st.container(border=True):
            st.markdown("#### :green[متى نستخدمه؟]")
            st.markdown("\n".join(f"- {d}" for d in use_when))
        with st.container(border=True):
            st.markdown("#### :blue[أمثلة من الواقع والأبحاث]")
            st.markdown("\n".join(f"- {d}" for d in examples))

    if demo is not None:
        st.markdown("### :material/play_circle: العرض التفاعلي")
        st.markdown(demo_label + " اضغط ▶ لمشاهدة البحث كتلةً كتلة، ثم اقرأ النتيجة النهائية أسفله.")
        with st.container(border=True):
            a, b, c = st.columns(3)
            size = a.slider("حجم الحدث", sizes[0], sizes[1], sizes[2], 0.25, key=f"{code}_size")
            alpha = b.select_slider("α", [0.001, 0.005, 0.01, 0.025, 0.05], 0.01, key=f"{code}_a")
            seed = c.number_input("البذرة", 1, 999, 7, key=f"{code}_seed")
        t, y, X, sets, truth, note = demo(size, int(seed), 0)
        res = figs.run_search(y, X, sets, alpha)
        tab1, tab2 = st.tabs(["▶ البحث خطوة بخطوة", "النتيجة النهائية"])
        with tab1:
            st.plotly_chart(figs.search_animation(t, y, res, truth), key=f"{code}_anim_{size}_{alpha}_{seed}")
        with tab2:
            st.plotly_chart(figs.result_figure(t, y, res, truth, "البيانات، الحقيقة، والنموذج المشبَّع"),
                            key=f"{code}_res_{size}_{alpha}_{seed}")
        kinds = res.__dict__["_all_kinds"]
        found = ", ".join(f"{kinds[j]} عند t={tau}" for j, tau in zip(res.selected, res.taus)) or "لا شيء"
        st.markdown(f"**المؤشرات المحتفظ بها:** {found}  \n**الحقيقة:** {note}")

    st.markdown("### :material/code: كيف أطبّقه؟")
    t1, t2 = st.tabs(["Stata (indsat)", "R (gets)"])
    with t1:
        st.code(stata, language="stata")
    with t2:
        st.code(r_code or "# غير متاح مباشرة في gets؛ استخدم uis = مصفوفة المؤشرات", language="r")
    if next_page:
        ui.nav_hint(next_page)


# ------------------------------------------------------------------ demo DGPs


def const_X(T: int) -> np.ndarray:
    return np.ones((T, 1))


def demo_outliers(size, seed, _):
    T = 90
    taus = [20, 55, 72]
    t, y, x, mu = sim.dgp(T, seed=seed, outliers=[(taus[0], size), (taus[1], -size), (taus[2], 0.8 * size)])
    truth = mu.copy()
    return t, y, const_X(T), [("IIS", *sim.impulses(T))], truth, \
        f"قيم شاذة عند t = {taus} بحجم ±{size:.1f}"


def demo_shifts(size, seed, _):
    T = 100
    t, y, x, mu = sim.dgp(T, seed=seed, shifts=[(35, size), (70, -1.2 * size)])
    return t, y, const_X(T), [("SIS", *sim.steps(T))], mu, f"تحول مستوى عند t = 35 (+{size:.1f}) وt = 70 (−{1.2 * size:.1f})"


def demo_super(size, seed, _):
    T = 100
    t, y, x, mu = sim.dgp(T, seed=seed, outliers=[(25, 1.8 * size)], shifts=[(60, size)])
    return t, y, const_X(T), [("IIS", *sim.impulses(T)), ("SIS", *sim.steps(T))], mu, \
        f"قيمة شاذة عند t = 25 وتحول مستوى عند t = 60"


def demo_trend(size, seed, _):
    T = 120
    t, y, x, mu = sim.dgp(T, seed=seed, trend_breaks=[(70, size / 10)])
    return t, y, const_X(T), [("TIS", *sim.trends(T))], mu, f"انكسار اتجاه عند t = 70 بميل إضافي {size / 10:.2f}"


def demo_mis(size, seed, _):
    T = 120
    t, y, x, mu = sim.dgp(T, seed=seed, beta=1.0, beta_shift=(65, size))
    X = np.column_stack([np.ones(T), x])
    return t, y, X, [("MIS", *sim.multiplicative(x))], None, f"معامل x يتغير من 1 إلى {1 + size:.1f} عند t = 65"


def demo_dis(size, seed, _):
    T = 90
    t, y, x, mu = sim.dgp(T, seed=seed, outliers=[(40, size), (41, -size)])
    return t, y, const_X(T), [("DIS", *sim.diff_impulses(T))], mu, f"قفزة +{size:.1f} عند t = 40 تنعكس عند t = 41"


def demo_pis(size, seed, _):
    T = 90
    t, y, x, mu = sim.dgp(T, seed=seed, outliers=[(30, size), (31, size)])
    return t, y, const_X(T), [("PIS", *sim.pair_impulses(T, 1))], mu, f"شذوذ مزدوج عند t = 30 و31"


def demo_bis(size, seed, _):
    T = 100
    shape = sim.volcanic_shape(0.5, 3)
    t, y, x, mu = sim.dgp(T, seed=seed, shape_shock=(45, -size, shape))
    return t, y, const_X(T), [("BIS", *sim.designed(T, shape))], mu, f"صدمة بركانية بحجم −{size:.1f} تبدأ عند t = 45"
