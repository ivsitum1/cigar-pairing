---
aliases:
  - statsmodels OLS
  - statsmodels-linear-models
---

# Statsmodels: linear models (OLS)

```python
import statsmodels.api as sm

X = sm.add_constant(X_data)  # required for intercept
model = sm.OLS(y, X)
results = model.fit()
print(results.summary())
```

- Predictions: `results.get_prediction(X_new).summary_frame()`
- Heteroskedasticity: `statsmodels.stats.diagnostic.het_breuschpagan`
- Use robust SE (`cov_type='HC3'`) when heteroskedasticity is present and justified.

Report coefficients, SE, 95% CI, and R²; pair with residual diagnostics in `stats_diagnostics.md`.

## Parent skills (auto)

- [[SKILL_statsmodels-python]]

## Related playbooks (auto)

- [[glm]]
- [[discrete_choice]]
- [[time_series]]
- [[stats_diagnostics]]
