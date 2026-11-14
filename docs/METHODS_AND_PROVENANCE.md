# Methods, denominator definitions and provenance

## Official synthetic benchmark

**Systems:** `null_ar`, `weak_ar`, `strong_ar`, `common_driver`, `null_logistic`, `coupled_logistic`. True X→Y direct links occur in weak AR, strong AR and coupled logistic; the common-driver system contains **no direct X→Y link**.

**Calendar length:** 138 months for the evaluation segment, after 500 burn-in time steps. A common set of synthetic realizations/seeds was reused for all methods. Six empirical observation masks were selected independently of significance results; their counts were 90, 0, 82, 94, 0, 104.

**Strategies:** one complete-data control for each realization; `empirical` (original masked calendar); `weather_month_matched` (preserves each calendar month's observed-count total but selects observations using simulated X, plus random noise). The last is a synthetic driver-dependent selection stress test, not an observed cloud mechanism.

**Methods:** official pyEDM CCM E=3, Tp=-1, tau=-1, 12-month temporal exclusion, 10 library samples. The forward-minus-reverse CCM skill statistic was calibrated against 120 independent *finite* null scores per estimable family/mask/strategy; no p-value is reported below that reference gate.

Tigramite PCMCI/ParCorr used PC alpha 0.2 and 1–3 month lags, with a usable MCI sample-count gate of 40 in both tested directions. Pairwise Granger used three autoregressive and predictor lags. A Z-conditioned lag OLS test is reported as a **separate exploratory comparator**, not renamed PCMCI. Nominal threshold was 0.05 in reported synthetic detection summaries.

**Denominators:** `attempted` counts all scheduled configurations; `eligible` is actual method-specific numerical support; `detected` means a p-value below nominal threshold among eligible. Report both `detected/eligible` and `detected/attempted`.

**Uncertainty:** 1,500 replicate-cluster bootstrap draws for contrasts between driver-conditioned and empirical masks, paired on independent simulation ID and mask. Reported intervals are exploratory, not familywise-adjusted. The 13 evaluations per simulation are dependent repeated tests; the independent unit is the simulated realization.

## Original field analysis (separate evidence)

- SPEI PM(3) → SSMI1: 21 of 36 climate-to-soil links with stored robust CCM diagnostic support.
- SSMI1 → NDVI anomaly: only one of 36 estimable; 0 supported.
- SPEI PM(3) → NDVI anomaly: 0 estimable in saved primary field configuration.
- Matched-Hargreaves forcing comparison: 22/36 ERA5 and 8/36 NASA-based support, with 6 common. Both involve ERA5-Land soil targets; **not** independent observation truth.
- Irrigation/AEZ interpretations are exploratory, not confirmed national buffering mechanisms.

The original 40,000-attempt simulation benchmark includes additional mask treatments (random, compression and interpolation). The new official 15,600-record experiment **does not rerun those original scenarios**, so do not replace the original study's results with these figures without distinction.

**Inference boundary:** CCM/Granger/PCMCI diagnostics and synthetic truth-known tests do not prove a complete Bangladesh field propagation chain.
