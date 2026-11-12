"""Plotly figures for the lecture, most of them animated (Play / Pause + slider)."""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

from . import sim

FONT = "IBM Plex Sans Arabic, Segoe UI, sans-serif"
COL = {
    "IIS": "#e8590c", "SIS": "#1c7ed6", "TIS": "#2f9e44", "QIS": "#5c940d", "MIS": "#ae3ec9",
    "BIS": "#f08c00", "DIS": "#0ca678", "PIS": "#d6336c", "UIS": "#495057",
    "data": "#868e96", "fit": "#d6336c", "true": "#2f9e44", "crit": "#fa5252", "band": "rgba(28,126,214,0.15)",
}
STAGE_AR = {"block": "كتلة", "union": "الاتحاد", "eliminate": "حذف تراجعي", "final": "النموذج النهائي"}


def _base_layout(fig: go.Figure, title: str = "", height: int = 420) -> go.Figure:
    fig.update_layout(
        title=dict(text=title, x=0.5, font=dict(size=16)),
        font=dict(family=FONT, size=13, color="#343a40"),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", height=height,
        margin=dict(l=40, r=30, t=60, b=40),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#f1f3f5", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f1f3f5", zeroline=False)
    return fig


def _play_controls(fig: go.Figure, names: list[str], labels: list[str] | None = None,
                   duration: int = 700) -> go.Figure:
    labels = labels or names
    fig.update_layout(
        updatemenus=[dict(
            type="buttons", direction="left", x=0.0, y=1.18, xanchor="left", yanchor="top",
            pad=dict(r=6, t=4), showactive=False,
            buttons=[
                dict(label="▶  Play / تشغيل", method="animate",
                     args=[None, dict(frame=dict(duration=duration, redraw=True), fromcurrent=True,
                                      transition=dict(duration=250))]),
                dict(label="⏸  Pause / إيقاف", method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate",
                                        transition=dict(duration=0))]),
            ])],
        sliders=[dict(
            active=0, x=0.05, len=0.9, y=-0.02, yanchor="top", pad=dict(t=30),
            currentvalue=dict(prefix="", font=dict(size=12)),
            steps=[dict(method="animate", label=lab,
                        args=[[nm], dict(mode="immediate", frame=dict(duration=duration, redraw=True),
                                         transition=dict(duration=200))])
                   for nm, lab in zip(names, labels)])],
    )
    return fig


# --------------------------------------------------------------------------- indicator sweep


def indicator_sweep(kind: str = "IIS", T: int = 40, every: int = 3, shape=None, h: int = 1) -> go.Figure:
    """Animate one column d_j(t) of a saturating set moving through the sample."""
    if kind == "BIS":
        M, taus = sim.designed(T, shape if shape is not None else sim.volcanic_shape())
    elif kind == "PIS":
        M, taus = sim.pair_impulses(T, h)
    elif kind == "MIS":
        rng = np.random.default_rng(2)
        x = rng.normal(size=T)
        M, taus = sim.multiplicative(x)
    else:
        M, taus = sim.build_set(kind, T)
    if kind in ("TIS", "QIS"):
        t = np.arange(T)[:, None]
        j = np.arange(1, T)[None, :]
        M = np.where(t >= j, (t - j + 1.0) ** (1 if kind == "TIS" else 2), 0.0)
    cols = list(range(0, M.shape[1], every))
    t = np.arange(T)
    color = COL.get(kind, "#1c7ed6")
    fig = go.Figure(data=[go.Bar(x=t, y=M[:, cols[0]], marker_color=color, name=f"d_j(t)")])
    frames = [go.Frame(data=[go.Bar(x=t, y=M[:, c], marker_color=color)], name=str(c),
                       layout=go.Layout(title=dict(text=f"{kind}: indicator starting at j = {taus[c]}")))
              for c in cols]
    fig.frames = frames
    ymax = float(np.nanmax(np.abs(M[:, cols]))) * 1.15
    ymin = float(np.nanmin(M[:, cols]))
    fig.update_yaxes(range=[min(0, ymin * 1.15), ymax])
    fig.update_xaxes(title="t (time)")
    _base_layout(fig, f"{kind}: indicator starting at j = {taus[cols[0]]}", 380)
    return _play_controls(fig, [str(c) for c in cols], [str(taus[c]) for c in cols], duration=350)


# --------------------------------------------------------------------------- search animation


def search_animation(t: np.ndarray, y: np.ndarray, res: sim.Result, mu_true: np.ndarray | None = None,
                     title: str = "") -> go.Figure:
    """Top: data and the fit of each stage; bottom: |t| of the candidates examined at that stage."""
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.62, 0.38], vertical_spacing=0.08)
    T = len(y)
    all_taus = np.array(_taus_of(res))
    kinds = _kinds_of(res)
    c = res.crit
    ymax_t = max([max(st.tvals) if st.tvals else 0 for st in res.steps] + [c]) * 1.15

    def stage_traces(st: sim.Step):
        xs = [all_taus[j] for j in st.cols]
        ts = list(st.tvals) if st.tvals else [0.0] * len(st.cols)
        colors = [COL.get(kinds[j], "#1c7ed6") if j in st.kept else "#ced4da" for j in st.cols]
        if st.cols:
            x0, x1 = min(xs), max(xs)
        else:
            x0 = x1 = 0
        band = go.Scatter(x=[x0, x1, x1, x0, x0], y=[ymin, ymin, ymax, ymax, ymin], fill="toself",
                          fillcolor="rgba(250,176,5,0.13)", line=dict(width=0), hoverinfo="skip",
                          name="الكتلة الحالية / current block", showlegend=True)
        fit = go.Scatter(x=t, y=st.fitted, mode="lines", line=dict(color=COL["fit"], width=2.5),
                         name="التوفيق / fit")
        bars = go.Bar(x=xs, y=ts, marker_color=colors, name="|t| للمؤشرات", showlegend=False)
        return band, fit, bars

    ymin, ymax = float(np.min(y)) - 0.5, float(np.max(y)) + 0.5
    st0 = res.steps[0]
    band, fit, bars = stage_traces(st0)
    fig.add_trace(band, 1, 1)
    fig.add_trace(go.Scatter(x=t, y=y, mode="lines+markers", marker=dict(size=4, color=COL["data"]),
                             line=dict(color=COL["data"], width=1), name="البيانات / data"), 1, 1)
    if mu_true is not None:
        fig.add_trace(go.Scatter(x=t, y=mu_true, mode="lines", line=dict(color=COL["true"], dash="dot", width=2),
                                 name="المسار الحقيقي / true path"), 1, 1)
    fig.add_trace(fit, 1, 1)
    fig.add_trace(bars, 2, 1)
    fig.add_trace(go.Scatter(x=[0, T - 1], y=[c, c], mode="lines", line=dict(color=COL["crit"], dash="dash"),
                             name=f"القيمة الحرجة c = {c:.2f}"), 2, 1)
    i_band, i_fit, i_bar = 0, (3 if mu_true is not None else 2), (4 if mu_true is not None else 3)
    frames, names, labels = [], [], []
    for i, st in enumerate(res.steps):
        b_, f_, br_ = stage_traces(st)
        lab = STAGE_AR.get(st.stage, st.stage)
        if st.stage == "block":
            nb = sum(1 for s in res.steps[: i + 1] if s.stage == "block")
            lab = f"{lab} {nb}"
        txt = f"{lab}: {len(st.cols)} مرشح ← {len(st.kept)} محتفظ به"
        frames.append(go.Frame(data=[b_, f_, br_], traces=[i_band, i_fit, i_bar], name=str(i),
                               layout=go.Layout(title=dict(text=txt))))
        names.append(str(i))
        labels.append(lab)
    fig.frames = frames
    fig.update_yaxes(range=[ymin, ymax], row=1, col=1)
    fig.update_yaxes(range=[0, ymax_t], title="|t|", row=2, col=1)
    fig.update_xaxes(range=[-1, T], row=2, col=1, title="t")
    st = res.steps[0]
    _base_layout(fig, title or f"{STAGE_AR['block']} 1: {len(st.cols)} مرشح ← {len(st.kept)} محتفظ به", 560)
    return _play_controls(fig, names, labels, duration=1100)


def _taus_of(res: sim.Result) -> list[int]:
    if "_all_taus" not in res.__dict__:
        res.__dict__["_all_taus"] = _recover_taus(res)
    return res.__dict__["_all_taus"]


def _recover_taus(res: sim.Result) -> list[int]:
    # first non-zero row of each candidate column = its date
    D = res.D
    out = []
    for j in range(D.shape[1]):
        nz = np.flatnonzero(np.abs(D[:, j]) > 1e-12)
        out.append(int(nz[0]) if len(nz) else 0)
    return out


def _kinds_of(res: sim.Result) -> list[str]:
    return res.__dict__.get("_all_kinds") or ["SIS"] * res.D.shape[1]


def run_search(y, X, sets, alpha):
    res = sim.saturate(y, X, sets, alpha=alpha)
    res.__dict__["_all_kinds"] = [s[0] for s in sets for _ in s[2]]
    res.__dict__["_all_taus"] = [tau for s in sets for tau in s[2]]
    return res


# --------------------------------------------------------------------------- result figure


def result_figure(t, y, res: sim.Result, mu_true=None, title: str = "", height: int = 430) -> go.Figure:
    k = res.X.shape[1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=y, mode="lines+markers", marker=dict(size=4, color=COL["data"]),
                             line=dict(color=COL["data"], width=1), name="البيانات / data"))
    if mu_true is not None:
        fig.add_trace(go.Scatter(x=t, y=mu_true, mode="lines", line=dict(color=COL["true"], dash="dot", width=2.2),
                                 name="الحقيقة / truth"))
    fig.add_trace(go.Scatter(x=t, y=res.fit.fitted, mode="lines", line=dict(color=COL["fit"], width=2.6),
                             name="النموذج المشبَّع / saturated fit"))
    kinds = _kinds_of(res)
    for j, tau in zip(res.selected, res.taus):
        kd = kinds[j] if j < len(kinds) else "SIS"
        fig.add_vline(x=tau, line=dict(color=COL.get(kd, "#1c7ed6"), dash="dash", width=1.4),
                      annotation_text=f"{kd} {tau}", annotation_position="top",
                      annotation_font=dict(size=11, color=COL.get(kd, "#1c7ed6")))
    fig.update_xaxes(title="t")
    return _base_layout(fig, title, height)


# --------------------------------------------------------------------------- why: bias animation


def break_bias_animation(T: int = 80, tau: int = 50, sizes=np.linspace(0, 5, 11), seed: int = 7) -> go.Figure:
    rng = np.random.default_rng(seed)
    e = rng.normal(size=T)
    t = np.arange(T)
    fig = go.Figure()
    y0 = 1 + e
    fig.add_trace(go.Scatter(x=t, y=y0, mode="markers", marker=dict(color=COL["data"], size=6), name="البيانات / data"))
    fig.add_trace(go.Scatter(x=t, y=np.full(T, 1.0), mode="lines", line=dict(color=COL["true"], width=3),
                             name="المستوى الحقيقي / true level"))
    fig.add_trace(go.Scatter(x=t, y=np.full(T, y0.mean()), mode="lines", line=dict(color=COL["fit"], width=3, dash="dash"),
                             name="متوسط OLS بدون كسر / OLS mean"))
    frames = []
    for s in sizes:
        mu = 1 + s * (t >= tau)
        y = mu + e
        frames.append(go.Frame(data=[
            go.Scatter(x=t, y=y), go.Scatter(x=t, y=mu), go.Scatter(x=t, y=np.full(T, y.mean()))],
            name=f"{s:.1f}",
            layout=go.Layout(title=dict(text=f"حجم الكسر λ = {s:.1f}:  متوسط OLS = {y.mean():.2f} "
                                             f"بينما المستوى قبل الكسر 1 وبعده {1 + s:.1f}"))))
    fig.frames = frames
    fig.update_yaxes(range=[-2.5, 9])
    _base_layout(fig, "حجم الكسر λ = 0.0", 430)
    return _play_controls(fig, [f.name for f in frames], [f.name for f in frames], duration=600)


def outlier_slope_animation(T: int = 40, sizes=np.linspace(0, 12, 13), seed: int = 3) -> go.Figure:
    rng = np.random.default_rng(seed)
    x = np.sort(rng.uniform(0, 10, T))
    e = rng.normal(size=T)
    base = 1 + 0.5 * x + e
    idx = T - 3
    xx = np.linspace(0, 10, 50)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=base, mode="markers", marker=dict(color=COL["data"], size=7), name="البيانات / data"))
    fig.add_trace(go.Scatter(x=[x[idx]], y=[base[idx]], mode="markers", marker=dict(color=COL["IIS"], size=14,
                             symbol="star"), name="القيمة الشاذة / outlier"))
    b = np.polyfit(x, base, 1)
    fig.add_trace(go.Scatter(x=xx, y=np.polyval(b, xx), mode="lines", line=dict(color=COL["fit"], width=3),
                             name="خط OLS"))
    fig.add_trace(go.Scatter(x=xx, y=1 + 0.5 * xx, mode="lines", line=dict(color=COL["true"], dash="dot", width=2.5),
                             name="الخط الحقيقي / truth"))
    frames = []
    for s in sizes:
        yy = base.copy()
        yy[idx] -= s
        b = np.polyfit(x, yy, 1)
        frames.append(go.Frame(data=[go.Scatter(x=x, y=yy), go.Scatter(x=[x[idx]], y=[yy[idx]]),
                                     go.Scatter(x=xx, y=np.polyval(b, xx))], traces=[0, 1, 2], name=f"{s:.0f}",
                               layout=go.Layout(title=dict(text=f"حجم الشذوذ = {s:.0f}:  الميل المقدَّر = {b[0]:.2f}  (الحقيقي 0.50)"))))
    fig.frames = frames
    fig.update_yaxes(range=[-10, 10])
    fig.update_xaxes(title="x")
    _base_layout(fig, "حجم الشذوذ = 0", 430)
    return _play_controls(fig, [f.name for f in frames], [f.name for f in frames], duration=500)


# --------------------------------------------------------------------------- GETS elimination animation


def gets_animation(seed: int = 4, n: int = 80, k: int = 10, relevant=(0, 3, 6), alpha: float = 0.05) -> go.Figure:
    rng = np.random.default_rng(seed)
    Z = rng.normal(size=(n, k))
    beta = np.zeros(k)
    for j, v in zip(relevant, (0.6, -0.5, 0.45)):
        beta[j] = v
    y = 1 + Z @ beta + rng.normal(size=n)
    X0 = np.ones((n, 1))
    names = [f"x{j + 1}" for j in range(k)]
    cur = list(range(k))
    c = sim.crit(alpha, n - k - 1)
    frames, labels = [], []
    while True:
        f = sim.ols(y, np.column_stack([X0, Z[:, cur]]))
        tv = np.abs(f.t[1:])
        full_t = np.zeros(k)
        for jj, tt in zip(cur, tv):
            full_t[jj] = tt
        colors = []
        for j in range(k):
            if j not in cur:
                colors.append("#e9ecef")
            elif full_t[j] > c:
                colors.append(COL["SIS"])
            else:
                colors.append("#fab005")
        jmin = int(np.argmin(tv)) if cur else -1
        txt = (f"النموذج الحالي يضم {len(cur)} متغيرًا؛ أضعفها {names[cur[jmin]]} (|t| = {tv[jmin]:.2f})"
               if cur and tv[jmin] < c else f"كل المتغيرات المتبقية معنوية: النموذج النهائي ({', '.join(names[j] for j in cur)})")
        frames.append(go.Frame(data=[go.Bar(x=names, y=full_t, marker_color=colors)], traces=[0],
                               name=str(len(frames)), layout=go.Layout(title=dict(text=txt))))
        labels.append(f"{len(cur)}")
        if not cur or tv[jmin] >= c:
            break
        cur = cur[:jmin] + cur[jmin + 1:]
    fig = go.Figure(data=[frames[0].data[0]])
    fig.add_trace(go.Scatter(x=[names[0], names[-1]], y=[c, c], mode="lines", line=dict(color=COL["crit"], dash="dash"),
                             name=f"c = {c:.2f}"))
    fig.frames = frames
    fig.update_yaxes(range=[0, max(max(f.data[0].y) for f in frames) * 1.2], title="|t|")
    _base_layout(fig, frames[0].layout.title.text, 420)
    return _play_controls(fig, [f.name for f in frames], labels, duration=1200)


# --------------------------------------------------------------------------- gauge


def gauge_hist(counts: np.ndarray, alpha: float, T: int) -> go.Figure:
    lam = alpha * T
    mx = int(max(counts.max(), lam * 3 + 4))
    xs = np.arange(0, mx + 1)
    emp = np.array([(counts == v).mean() for v in xs])
    fig = go.Figure()
    fig.add_trace(go.Bar(x=xs, y=emp, marker_color=COL["SIS"], name="المحاكاة / simulated", opacity=0.85))
    fig.add_trace(go.Scatter(x=xs, y=stats.poisson.pmf(xs, lam), mode="lines+markers",
                             line=dict(color=COL["IIS"], width=2.5), name=f"Poisson(αT = {lam:.2f})"))
    fig.update_xaxes(title="عدد المؤشرات الزائفة المحتفظ بها / false impulses retained")
    fig.update_yaxes(title="الاحتمال")
    return _base_layout(fig, f"توزيع عدد المؤشرات الزائفة: المتوسط المحاكى {counts.mean():.2f} مقابل αT = {lam:.2f}", 400)


def potency_curve(sizes, potency, gauge) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=sizes, y=potency, mode="lines+markers", line=dict(color=COL["SIS"], width=3),
                             name="القوة / potency"), secondary_y=False)
    fig.add_trace(go.Scatter(x=sizes, y=gauge, mode="lines+markers", line=dict(color=COL["IIS"], width=2, dash="dot"),
                             name="المقياس / gauge"), secondary_y=True)
    fig.update_xaxes(title="حجم الكسر بوحدات σ / break size")
    fig.update_yaxes(title="Potency", range=[0, 1.05], secondary_y=False)
    fig.update_yaxes(title="Gauge", secondary_y=True)
    return _base_layout(fig, "القوة ترتفع مع حجم الكسر بينما يبقى المقياس قريبًا من α", 400)


def efficiency_curve() -> go.Figure:
    al = np.linspace(0.001, 0.2, 120)
    eff = [sim.jn_factors(a)["eff"] for a in al]
    xi = [sim.jn_factors(a)["xi"] for a in al]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=al, y=eff, line=dict(color=COL["TIS"], width=3), name="كفاءة β / efficiency"), secondary_y=False)
    fig.add_trace(go.Scatter(x=al, y=xi, line=dict(color=COL["MIS"], width=3, dash="dash"), name="معامل الاتساق ξ"), secondary_y=True)
    fig.update_xaxes(title="α (target size)")
    fig.update_yaxes(title="Efficiency 1/η²", secondary_y=False)
    fig.update_yaxes(title="ξ", secondary_y=True)
    return _base_layout(fig, "ثمن التأمين ضد القيم الشاذة: فقدان كفاءة صغير جدًا (Johansen & Nielsen 2009)", 400)


# --------------------------------------------------------------------------- timeline


def timeline(events: list[tuple[int, str, str, str]]) -> go.Figure:
    """events: (year, short label, description, group)."""
    groups = sorted(set(e[3] for e in events))
    gy = {g: i for i, g in enumerate(groups)}
    pal = ["#1c7ed6", "#e8590c", "#2f9e44", "#ae3ec9", "#f08c00", "#d6336c", "#0ca678"]
    fig = go.Figure()
    for i, g in enumerate(groups):
        ev = [e for e in events if e[3] == g]
        fig.add_trace(go.Scatter(
            x=[e[0] for e in ev], y=[gy[g]] * len(ev), mode="markers+text", text=[e[1] for e in ev],
            textposition="top center", marker=dict(size=16, color=pal[i % len(pal)], line=dict(color="white", width=2)),
            hovertext=[f"<b>{e[0]} — {e[1]}</b><br>{e[2]}" for e in ev], hoverinfo="text", name=g))
    fig.update_yaxes(tickvals=list(gy.values()), ticktext=list(gy.keys()), range=[-0.6, len(groups) - 0.3])
    fig.update_xaxes(dtick=2, title="")
    return _base_layout(fig, "", 470)
