import streamlit as st

from lib import ui

ui.hero("المكتبة", "المراجع", "References",
        "المراجع الأساسية مرتبة حسب الموضوع. لا تحتاج أن تقرأها كلها: ابدأ بالمراجع المقترحة أدناه، ثم توسع حسب سؤالك البحثي.",
        "gray")
with ui.box("tip", "من أين تبدأ القراءة؟"):
    st.markdown(
        """
1. **للفكرة والتطبيق**: Castle, Doornik, Hendry & Pretis (2015) عن SIS — واضحة وفيها أمثلة.
2. **للبرمجة**: Pretis, Reade & Sucarrat (2018) — حزمة gets في R خطوة بخطوة.
3. **للاختبارات**: Jiao & Pretis (2022) — اختبارات القيم الشاذة.
4. **للنظرية**: Johansen & Nielsen (2016) — المقياس وتوزيعاته.
"""
    )

R = {
    "الأسس والخوارزميات": [
        "Hendry, D.F. (1999). An econometric analysis of US food expenditure, 1931–1989. In Magnus & Morgan (eds), *Methodology and Tacit Knowledge*. Wiley.",
        "Hoover, K.D. and S.J. Perez (1999). Data mining reconsidered. *Econometrics Journal* 2: 167–191.",
        "Hendry, D.F., S. Johansen and C. Santos (2008). Automatic selection of indicators in a fully saturated regression. *Computational Statistics* 23: 317–335.",
        "Doornik, J.A. (2009). Autometrics. In Castle & Shephard (eds), *The Methodology and Practice of Econometrics*. OUP.",
        "Castle, J.L., J.A. Doornik and D.F. Hendry (2012). Model selection when there are multiple breaks. *Journal of Econometrics* 169: 239–246.",
        "Castle, J.L. and D.F. Hendry (2019). *Modelling our Changing World*. Palgrave Texts in Econometrics.",
    ],
    "النظرية": [
        "Johansen, S. and B. Nielsen (2009). An analysis of the indicator saturation estimator as a robust regression estimator. In Castle & Shephard (eds). OUP.",
        "Johansen, S. and B. Nielsen (2013). Outlier detection in regression using an iterated one-step approximation to the Huber-skip estimator. *Econometrics* 1: 53–70.",
        "Johansen, S. and B. Nielsen (2016). Asymptotic theory of outlier detection algorithms for linear time series regression models. *Scandinavian Journal of Statistics* 43: 321–348.",
        "Nielsen, B. and M. Qian (2025). Asymptotic properties of the gauge and power of step-indicator saturation. University of Oxford.",
        "Jiao, X. and F. Pretis (2022). Testing the presence of outliers in regression models. *Oxford Bulletin of Economics and Statistics*.",
    ],
    "الأنواع": [
        "Doornik, J.A., D.F. Hendry and F. Pretis (2013). Step-indicator saturation. Oxford Economics Discussion Paper 658.",
        "Castle, J.L., J.A. Doornik, D.F. Hendry and F. Pretis (2015). Detecting location shifts during model selection by step-indicator saturation. *Econometrics* 3: 240–264.",
        "Ericsson, N.R. (2011). Justifying empirical macro-econometric evidence in practice. Federal Reserve Board.",
        "Kitov, O.I. and M.N. Tabor (2015). Detecting structural changes in linear models: a variable selection approach using multiplicative indicator saturation. University of Oxford.",
        "Pretis, F., L. Schneider, J.E. Smerdon and D.F. Hendry (2016). Detecting volcanic eruptions in temperature reconstructions by designed break-indicator saturation. *Journal of Economic Surveys* 30: 403–429.",
        "Kurle, J.K. (2025). A Monte Carlo study of super saturation for detecting outliers and location shifts. SSRN 5583830.",
    ],
    "التطبيقات والتنبؤ": [
        "Ericsson, N.R. and E.L. Reisman (2012). Evaluating a global vector autoregression for forecasting. RPF Working Paper 2012-006.",
        "Marczak, M. and T. Proietti (2016). Outlier detection in structural time series models: the indicator saturation approach. *International Journal of Forecasting* 32: 180–202.",
        "Castle, J.L., J.A. Doornik and D.F. Hendry (2020). Robust discovery of regression models. Oxford Working Paper 2020-W04.",
        "Ericsson, N.R., M.H.I. Dore and H. Butt (2022). Detecting and quantifying structural breaks in climate. *Econometrics* 10: 33.",
        "Stillwagon, J.R. (2025). Tracking shifts in U.S. monetary policy: comparing multiplicative indicator saturation with three alternatives. SSRN 6806799.",
        "Castle, J.L., J.A. Doornik and D.F. Hendry (2026). A novel approach to forecasting after large forecast errors. *Journal of Forecasting* 45: 837–849.",
    ],
    "البرمجيات": [
        "Pretis, F., J.J. Reade and G. Sucarrat (2018). Automated general-to-specific regression modeling and indicator saturation for outliers and structural breaks. *Journal of Statistical Software* 86(3).",
        "Sucarrat, G. (2020). User-specified general-to-specific and indicator saturation methods. *The R Journal* 12(2): 251–265.",
        "Roudane, M. (2026). indsat: indicator saturation library for Stata. https://github.com/merwanroudane/indsat",
    ],
}
for sec, items in R.items():
    st.markdown(f"### {sec}")
    st.markdown("\n".join(f"- {it}" for it in items))
st.divider()
st.caption("أُعدّت هذه المحاضرة التفاعلية لتعليم تشبع المؤشرات من الصفر — د. مروان رودان")
