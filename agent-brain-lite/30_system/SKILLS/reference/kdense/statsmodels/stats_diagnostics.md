# Statsmodels: diagnostics

## Residual checks

- Residuals vs fitted scatter
- Breusch-Pagan for heteroskedasticity (linear models)
- Normality of residuals (supplementary; large n → visual)

## Influence

- Outliers in predictor space; large Cook's distance where supported

## Time series

- Ljung-Box on residuals after ARIMA fit
- Compare AIC/BIC across candidate orders

## Reporting rule

Do not interpret coefficients until diagnostics are run and summarized in output.

Optional repo helper: `python 40_operations/python/statistics/assumption_checks.py` for column-level screening only.

## Parent skills (auto)

- [[SKILL_statsmodels-python]]

## Related playbooks (auto)

- [[linear_models]]
- [[glm]]
- [[discrete_choice]]
- [[time_series]]
