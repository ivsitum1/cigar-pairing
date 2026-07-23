# Statsmodels: discrete outcomes

## Logistic (binary)

```python
from statsmodels.discrete.discrete_model import Logit

X = sm.add_constant(X_data)
results = Logit(y_binary, X).fit()
odds_ratios = np.exp(results.params)
probs = results.predict(X)
```

Report OR with 95% CI; evaluate calibration/AUC if prediction is in scope.

## Count / multinomial

Use appropriate discrete model classes; check convergence warnings.

Marginal effects: `results.get_margeff().summary()` when interpretability requires.

## Parent skills (auto)

- [[SKILL_statsmodels-python]]

## Related playbooks (auto)

- [[linear_models]]
- [[glm]]
- [[time_series]]
- [[stats_diagnostics]]
