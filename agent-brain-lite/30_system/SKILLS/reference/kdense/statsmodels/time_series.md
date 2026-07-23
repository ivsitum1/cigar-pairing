# Statsmodels: time series

## Stationarity

```python
from statsmodels.tsa.stattools import adfuller
adf_result = adfuller(y_series)
```

Difference or transform if non-stationary before ARIMA order selection.

## ARIMA

```python
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

model = ARIMA(y_series, order=(p, d, q))
results = model.fit()
forecast = results.forecast(steps=h)
```

Document chosen (p,d,q) with ACF/PACF or information criteria; report forecast intervals.

Clinical ICU series: justify alignment with clinical events; avoid spurious seasonality claims.

## Parent skills (auto)

- [[SKILL_statsmodels-python]]

## Related playbooks (auto)

- [[linear_models]]
- [[glm]]
- [[discrete_choice]]
- [[stats_diagnostics]]
