# Statsmodels: GLM

```python
import statsmodels.api as sm

X = sm.add_constant(X_data)
model = sm.GLM(y, X, family=sm.families.Gaussian())  # or Poisson(), Gamma(), etc.
results = model.fit()
```

- Check family/link match outcome type.
- Overdispersion for counts: consider negative binomial or quasi-Poisson.
- Report effect on response scale when interpreting for clinicians.

See `discrete_choice.md` for binary/count-specific APIs.

## Parent skills (auto)

- [[SKILL_statsmodels-python]]

## Related playbooks (auto)

- [[linear_models]]
- [[discrete_choice]]
- [[time_series]]
- [[stats_diagnostics]]
