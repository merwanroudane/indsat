"""Lightweight indicator-saturation engine for the lecture demos.

Implements the split-half / block algorithm of Hendry, Johansen & Santos (2008),
generalised to several blocks, with a final backward elimination on the union of
block survivors.  It is deliberately simple and fast so that every slider move can
re-run the search live.  The full multi-path search is in the Stata library `indsat`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy import stats

# --------------------------------------------------------------------------- indicators


def impulses(T: int) -> tuple[np.ndarray, list[int]]:
    return np.eye(T), list(range(T))


def steps(T: int, form: str = "up") -> tuple[np.ndarray, list[int]]:
    t = np.arange(T)[:, None]
    if form == "down":
        j = np.arange(T - 1)[None, :]
        return (t <= j).astype(float), list(range(T - 1))
    j = np.arange(1, T)[None, :]
    return (t >= j).astype(float), list(range(1, T))


def trends(T: int, power: int = 1) -> tuple[np.ndarray, list[int]]:
    t = np.arange(T)[:, None]
    j = np.arange(1, T)[None, :]
    M = np.where(t >= j, (t - j + 1.0) ** power, 0.0)
    return M / M.max(axis=0, keepdims=True), list(range(1, T))


def diff_impulses(T: int) -> tuple[np.ndarray, list[int]]:
    M = np.zeros((T, T - 1))
    for c, j in enumerate(range(1, T)):
        M[j, c] = 1.0
        M[j - 1, c] = -1.0
    return M, list(range(1, T))


def pair_impulses(T: int, h: int = 1) -> tuple[np.ndarray, list[int]]:
    M = np.zeros((T, T - h))
    for i in range(T - h):
        M[i, i] = 1.0
        M[i + h, i] = 1.0
    return M, list(range(T - h))


def designed(T: int, shape: np.ndarray) -> tuple[np.ndarray, list[int]]:
    L = len(shape)
    M = np.zeros((T, T))
    for j in range(T):
        for k in range(L):
            if j + k < T:
                M[j + k, j] = shape[k]
    return M, list(range(T))


def multiplicative(x: np.ndarray) -> tuple[np.ndarray, list[int]]:
    S, taus = steps(len(x))
    return S * x[:, None], taus


def volcanic_shape(gamma: float = 0.5, L: int = 3) -> np.ndarray:
    """Pretis et al. (2016) eq. (31) with response time 1, scaled to max |d| = 1."""
    t = np.arange(1, L + 1, dtype=float)
    if abs(gamma - 1) < 1e-10:
        d = t * np.exp(-t)
    else:
        a = 1 - 1 / gamma
        d = np.exp(-t) * (np.exp(t * a) - 1) / a
    return d / np.abs(d).max()


def tc_shape(delta: float = 0.7, L: int = 12) -> np.ndarray:
    return delta ** np.arange(L)


def ramp_shape(L: int = 4) -> np.ndarray:
    return (L - np.arange(L)) / L


INDICATOR_LABELS = {
    "IIS": ("نبضة", "Impulse"),
    "SIS": ("درجة (تحوّل مستوى)", "Step"),
    "TIS": ("اتجاه منكسر", "Broken trend"),
    "QIS": ("اتجاه تربيعي منكسر", "Broken quadratic trend"),
    "DIS": ("نبضة مفرَّقة", "Differenced impulse"),
    "PIS": ("نبضة زوجية", "Pairwise impulse"),
    "BIS": ("دالة كسر مصمَّمة", "Designed break"),
    "MIS": ("كسر في المعامل", "Multiplicative indicator"),
}


def build_set(kind: str, T: int, x: np.ndarray | None = None, **kw) -> tuple[np.ndarray, list[int]]:
    if kind == "IIS":
        return impulses(T)
    if kind == "SIS":
        return steps(T, kw.get("form", "up"))
    if kind == "TIS":
        return trends(T, 1)
    if kind == "QIS":
        return trends(T, 2)
    if kind == "DIS":
        return diff_impulses(T)
    if kind == "PIS":
        return pair_impulses(T, kw.get("h", 1))
    if kind == "BIS":
        return designed(T, kw.get("shape", volcanic_shape()))
    if kind == "MIS":
        if x is None:
            raise ValueError("MIS needs a regressor x")
        return multiplicative(x)
    raise ValueError(kind)


# --------------------------------------------------------------------------- OLS


@dataclass
class Fit:
    b: np.ndarray
    se: np.ndarray
    t: np.ndarray
    resid: np.ndarray
    fitted: np.ndarray
    sigma: float
    df: int


def ols(y: np.ndarray, X: np.ndarray) -> Fit:
    n, k = X.shape
    XtX = X.T @ X
    XtXi = np.linalg.pinv(XtX)
    b = XtXi @ X.T @ y
    fitted = X @ b
    e = y - fitted
    df = max(n - k, 1)
    s2 = float(e @ e) / df
    se = np.sqrt(np.clip(np.diag(XtXi) * s2, 1e-300, None))
    return Fit(b, se, b / se, e, fitted, math.sqrt(s2), df)


def crit(alpha: float, df: int = 10_000) -> float:
    return float(stats.t.ppf(1 - alpha / 2, df))


# --------------------------------------------------------------------------- search


@dataclass
class Step:
    stage: str               # "block", "union", "final"
    cols: list[int]          # candidate columns (indices into D) examined at this stage
    tvals: list[float]       # their |t|
    kept: list[int]          # survivors at this stage
    fitted: np.ndarray       # fitted values of the stage regression


@dataclass
class Result:
    selected: list[int]
    taus: list[int]
    kinds: list[str]
    fit: Fit
    X: np.ndarray
    D: np.ndarray
    steps: list[Step] = field(default_factory=list)
    crit: float = 0.0


def saturate(y: np.ndarray, X: np.ndarray, sets: list[tuple[str, np.ndarray, list[int]]],
             alpha: float = 0.01, nblocks: int | None = None) -> Result:
    """Block saturation: blocks of candidates added to the model with X kept;
    |t| > c survives; union re-estimated; backward elimination to |t| > c."""
    T, k = X.shape
    D = np.column_stack([s[1] for s in sets]) if sets else np.zeros((T, 0))
    taus = [tau for s in sets for tau in s[2]]
    kinds = [s[0] for s in sets for _ in s[2]]
    m = D.shape[1]
    c = crit(alpha, max(T - k - 1, 5))
    steps_: list[Step] = []
    if m == 0:
        f = ols(y, X)
        return Result([], [], [], f, X, D, steps_, c)
    max_block = max(2, int(0.5 * (T - k)) - 1)
    if nblocks is None:
        nblocks = max(2, math.ceil(m / max_block))
    edges = np.linspace(0, m, nblocks + 1).astype(int)
    survivors: list[int] = []
    for b0, b1 in zip(edges[:-1], edges[1:]):
        cols = list(range(b0, b1))
        if not cols:
            continue
        Z = np.column_stack([X, D[:, cols]])
        keep_idx = _independent(Z)
        Z = Z[:, keep_idx]
        cols_ok = [cols[i - k] for i in keep_idx if i >= k]
        f = ols(y, Z)
        tv0 = np.abs(f.t[k:])
        # single-path GETS inside the block: delete the least significant until all |t| > c
        cur_b = list(cols_ok)
        while cur_b:
            fb = ols(y, np.column_stack([X, D[:, cur_b]]))
            tvb = np.abs(fb.t[k:])
            j = int(np.argmin(tvb))
            if tvb[j] >= c:
                break
            cur_b = cur_b[:j] + cur_b[j + 1:]
        kept = cur_b
        fk = ols(y, np.column_stack([X, D[:, kept]])) if kept else ols(y, X)
        steps_.append(Step("block", cols_ok, list(tv0), kept, fk.fitted))
        survivors += kept
    # union and backward elimination (collinear combinations dropped first, in candidate order)
    cur = sorted(set(survivors))
    if cur:
        ind = _independent(np.column_stack([X, D[:, cur]]))
        cur = [cur[i - k] for i in ind if i >= k]
    while True:
        Z = np.column_stack([X, D[:, cur]]) if cur else X
        f = ols(y, Z)
        if not cur:
            break
        tv = np.abs(f.t[k:])
        steps_.append(Step("union" if len(steps_) == nblocks else "eliminate", list(cur), list(tv),
                           [cc for cc, tt in zip(cur, tv) if tt > c], f.fitted))
        j = int(np.argmin(tv))
        if tv[j] >= c:
            break
        cur = cur[:j] + cur[j + 1:]
    Z = np.column_stack([X, D[:, cur]]) if cur else X
    f = ols(y, Z)
    steps_.append(Step("final", list(cur), list(np.abs(f.t[k:])) if cur else [], list(cur), f.fitted))
    return Result(cur, [taus[i] for i in cur], [kinds[i] for i in cur], f, X, D, steps_, c)


def _independent(Z: np.ndarray, tol: float = 1e-8) -> list[int]:
    keep: list[int] = []
    Q = np.zeros((Z.shape[0], 0))
    for j in range(Z.shape[1]):
        v = Z[:, j]
        nv = np.linalg.norm(v)
        if nv == 0:
            continue
        r = v - Q @ (Q.T @ v) if Q.shape[1] else v
        nr = np.linalg.norm(r)
        if nr > tol * nv:
            Q = np.column_stack([Q, r / nr])
            keep.append(j)
    return keep


# --------------------------------------------------------------------------- DGPs


def dgp(T: int = 100, seed: int = 1, mu: float = 1.0, sigma: float = 1.0,
        outliers: list[tuple[int, float]] | None = None,
        shifts: list[tuple[int, float]] | None = None,
        trend_breaks: list[tuple[int, float]] | None = None,
        beta: float = 0.0, beta_shift: tuple[int, float] | None = None,
        rho: float = 0.0, shape_shock: tuple[int, float, np.ndarray] | None = None):
    """Return (t, y, x, mu_t) with the deterministic path mu_t known."""
    rng = np.random.default_rng(seed)
    t = np.arange(T)
    x = rng.normal(size=T)
    e = rng.normal(scale=sigma, size=T)
    mu_t = np.full(T, mu, dtype=float)
    for tau, size in shifts or []:
        mu_t[t >= tau] += size
    for tau, slope in trend_breaks or []:
        mu_t += slope * np.clip(t - tau + 1, 0, None)
    if shape_shock is not None:
        tau, size, shape = shape_shock
        for k, d in enumerate(shape):
            if tau + k < T:
                mu_t[tau + k] += size * d
    b_t = np.full(T, beta, dtype=float)
    if beta_shift is not None:
        b_t[t >= beta_shift[0]] += beta_shift[1]
    u = np.zeros(T)
    for i in range(T):
        u[i] = (rho * u[i - 1] if i > 0 else 0.0) + e[i]
    y = mu_t + b_t * x + u
    for tau, size in outliers or []:
        y[tau] += size
    return t, y, x, mu_t


# --------------------------------------------------------------------------- theory


def jn_factors(alpha: float) -> dict[str, float]:
    """Johansen-Nielsen quantities for a two-sided normal cut-off."""
    c = stats.norm.ppf(1 - alpha / 2)
    phi = stats.norm.pdf(c)
    psi = 1 - alpha
    tau = psi - 2 * c * phi
    rho = 2 * c * phi / psi
    eta2 = ((1 / psi) ** 2 + 2 * rho / psi) * tau + rho ** 2
    return {"c": c, "psi": psi, "tau": tau, "xi": math.sqrt(psi / tau), "eta": math.sqrt(eta2),
            "eff": 1 / eta2}


def iis_gauge_mc(T: int, alpha: float, reps: int, seed: int = 0) -> np.ndarray:
    """Number of false impulses retained by split-half IIS under the null."""
    rng = np.random.default_rng(seed)
    out = np.empty(reps)
    X = np.ones((T, 1))
    D, taus = impulses(T)
    for r in range(reps):
        y = rng.normal(size=T)
        res = saturate(y, X, [("IIS", D, taus)], alpha=alpha, nblocks=2)
        out[r] = len(res.selected)
    return out


def sis_potency_mc(T: int, alpha: float, size: float, reps: int, seed: int = 0, window: int = 2):
    rng = np.random.default_rng(seed)
    X = np.ones((T, 1))
    D, taus = steps(T)
    tau0 = T // 2
    hits = 0
    false = 0
    for r in range(reps):
        y = rng.normal(size=T) + size * (np.arange(T) >= tau0)
        res = saturate(y, X, [("SIS", D, taus)], alpha=alpha)
        near = [abs(t - tau0) <= window for t in res.taus]
        hits += any(near)
        false += sum(not n for n in near)
    return hits / reps, false / (reps * (T - 2))


def vargauge(alpha: float, T: int, m: int = 1) -> float:
    """Variance of the IIS gauge (Johansen-Nielsen 2016; gets::vargaugeiis)."""
    c = abs(stats.norm.ppf(alpha / 2))
    fc = stats.norm.pdf(c)
    psi = 1 - alpha
    tau = psi - 2 * c * fc
    chi = 3 * psi - 2 * c * (c ** 2 + 3) * fc
    rho = (c ** 2 - tau / psi) * c * fc / tau
    k = 3
    m1 = m - 1
    eta1 = (((1 - rho ** m1) / ((1 - rho) * tau)) ** 2 + 2 * ((1 - rho ** m1) / ((1 - rho) * tau)) * rho ** m1) \
        * (chi - tau ** 2 / psi) / (k - 1) + rho ** (2 * m1)
    etag = (c * fc) ** 2 * eta1 * (k - 1) + 2 * c * fc * rho ** (m - 1) * (tau - psi)
    return (psi * (1 - psi) + etag) / T


def biascorr(b: np.ndarray, se: np.ndarray, alpha: float, T: int) -> tuple[np.ndarray, np.ndarray]:
    """One- and two-step bias correction (Hendry & Krolzig 2005; gets::biascorr)."""
    c = abs(stats.t.ppf(alpha / 2, T))
    bt = b / se

    def r(x):
        return (stats.norm.pdf(c - x) - stats.norm.pdf(-c - x)) / (1 - stats.norm.cdf(c - x) + stats.norm.cdf(-c - x))

    dr = r(bt)
    drbar = r(bt - dr)
    big = np.abs(bt) > c
    b1 = np.where(big, b * (1 - dr / bt), b)
    b2 = np.where(big, b * (1 - drbar / bt), b)
    return b1, b2
