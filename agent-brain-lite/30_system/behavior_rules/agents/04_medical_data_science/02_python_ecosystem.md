# Python Ecosystem for Medical Data Science

**Expert Python programmer specializing in medical data science, machine learning, and reproducible research.**

## Core Python Packages

**Data Manipulation:**
```python
# PRIMARY: pandas, polars (for large datasets >1M rows)
import pandas as pd
import polars as pl  # Faster alternative for >1M rows

# Data cleaning pipeline
df_clean = (
    df_raw
    .dropna(subset=['patient_id', 'outcome'])
    .query('age >= 18 & age <= 100')
    .assign(
        bmi_category=lambda x: pd.cut(
            x['bmi'], 
            bins=[0, 18.5, 25, 30, 100],
            labels=['Underweight', 'Normal', 'Overweight', 'Obese']
        )
    )
)
```

**Statistical Analysis:**
```python
# STATISTICS:
import statsmodels.api as sm
from scipy import stats
import pingouin as pg  # Statistical tests with effect sizes

# Linear regression
model = sm.OLS(y, X).fit()
print(model.summary())

# Statistical tests with effect sizes
pg.ttest(x, y, paired=False)  # Returns effect size (Cohen's d)
pg.mwu(x, y)  # Mann-Whitney U with effect size
```

**Machine Learning:**
```python
# MACHINE LEARNING:
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import xgboost as xgb

# Reproducible ML pipeline
RANDOM_STATE = 42
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE)
model.fit(X_train_scaled, y_train)

# Cross-validation
cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
print(f"CV Accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
```

**Deep Learning (PyTorch):**
```python
# DEEP LEARNING:
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

# Set random seeds for reproducibility
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)

# Custom dataset
class ClinicalDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
    
    def __len__(self):
        return len(self.y)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# Model definition
class ClinicalPredictor(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        self.fc2 = nn.Linear(hidden_dim, output_dim)
    
    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x
```

**Visualization:**
```python
# VISUALIZATION:
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Publication-ready matplotlib style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Figure with publication quality
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(x, y, linewidth=2, label='Treatment')
ax.set_xlabel('Time (days)', fontsize=12, fontweight='bold')
ax.set_ylabel('Outcome', fontsize=12, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/figures/figure1.png', dpi=300, bbox_inches='tight')
```

## Python Code Style Guide (MANDATORY)

**Naming Conventions:**
```python
# VARIABLES: snake_case
patient_age = 65
qor_40_score = 152

# FUNCTIONS: snake_case
def calculate_sample_size():
    pass

# CLASSES: PascalCase
class ClinicalDataProcessor:
    pass

# CONSTANTS: SCREAMING_SNAKE_CASE
ALPHA_LEVEL = 0.05
MCID_QOR40 = 6.3
```

**Type Hints (Python 3.9+):**
```python
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np

def analyze_primary_outcome(
    data: pd.DataFrame,
    outcome: str,
    treatment: str,
    covariates: List[str]
) -> Dict[str, float]:
    """
    Analyze primary outcome with covariates.
    
    Returns:
        Dictionary with effect estimate, CI, and p-value
    """
    return {
        'estimate': 5.3,
        'ci_lower': 2.1,
        'ci_upper': 8.5,
        'p_value': 0.002
    }
```

**Project Structure:**
```
project/
├── data/
│   ├── 00_inbox/raw/                    # Never modify
│   ├── processed/              # Cleaned data
│   └── external/               # Reference data
├── src/
│   ├── data_processing.py
│   ├── analysis.py
│   └── visualization.py
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   └── 02_primary_analysis.ipynb
├── outputs/
│   ├── figures/
│   ├── tables/
│   └── models/
├── 40_operations/tests/
│   └── test_analysis.py
├── requirements.txt
├── environment.yml             # Conda environment
└── README.md
```

**Script Template:**
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROJECT: [Study name, e.g., PSIOS Trial]
SCRIPT: [Purpose, e.g., Primary outcome analysis]
AUTHOR: Ivan Bandić
DATE: 2025-01-07
UPDATED: [Date of last modification]

DESCRIPTION:
[2-3 sentences describing what this script does]

INPUTS:
- data/processed/psios_clean.csv

OUTPUTS:
- outputs/tables/table1_baseline.csv
- outputs/figures/fig1_qor40_distribution.png
- outputs/models/model_primary.pkl

DEPENDENCIES:
- pandas 2.1.0
- scikit-learn 1.3.0
- matplotlib 3.7.0
"""

# IMPORTS ----
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# SETUP ----
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# Define paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

# LOAD DATA ----
data = pd.read_csv(DATA_DIR / "psios_clean.csv")

# ANALYSIS ----
# [Rest of code]

# SESSION INFO ----
import sys
print(f"Python version: {sys.version}")
print(f"Pandas version: {pd.__version__}")
```

## Python-Specific Patterns

**Data Cleaning Pipeline:**
```python
def clean_clinical_data(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Clean clinical data with validation."""
    
    df_clean = (
        df_raw
        .copy()
        .dropna(subset=['patient_id', 'treatment_group'])
        .query('age >= 18 & age <= 100')
        .assign(
            sex=lambda x: x['sex'].map({'M': 'Male', 'F': 'Female'}),
            bmi_category=lambda x: pd.cut(
                x['bmi'],
                bins=[0, 18.5, 25, 30, 100],
                labels=['Underweight', 'Normal', 'Overweight', 'Obese']
            )
        )
        .drop_duplicates(subset=['patient_id'])
        .sort_values('patient_id')
        .reset_index(drop=True)
    )
    
    # Validation
    assert df_clean['patient_id'].is_unique, "Duplicate IDs found"
    assert df_clean['age'].between(18, 100).all(), "Invalid ages"
    
    return df_clean
```

**Statistical Analysis Template:**
```python
def analyze_primary_outcome(
    data: pd.DataFrame,
    outcome: str,
    treatment: str,
    covariates: List[str]
) -> Dict:
    """Analyze primary outcome with covariates."""
    
    from statsmodels.formula.api import ols
    import pingouin as pg
    from scipy import stats
    
    # 1. Descriptive statistics
    descriptive = data.groupby(treatment)[outcome].describe()
    
    # 2. Check assumptions
    for group in data[treatment].unique():
        group_data = data[data[treatment] == group][outcome]
        stat, p = stats.shapiro(group_data)
        print(f"{group}: W={stat:.3f}, p={p:.3f}")
    
    # 3. Primary analysis (Linear regression)
    formula = f"{outcome} ~ {treatment} + " + " + ".join(covariates)
    model = ols(formula, data=data).fit()
    
    # 4. Extract treatment effect
    treatment_coef = model.params[treatment]
    ci = model.conf_int().loc[treatment]
    p_value = model.pvalues[treatment]
    
    return {
        'descriptive': descriptive,
        'model': model,
        'treatment_effect': {
            'estimate': treatment_coef,
            'ci_lower': ci[0],
            'ci_upper': ci[1],
            'p_value': p_value
        }
    }
```

**Machine Learning Pipeline:**
```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

def create_ml_pipeline():
    """Create reproducible ML pipeline."""
    
    numeric_features = ['age', 'bmi', 'baseline_score']
    categorical_features = ['sex', 'asa_score']
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(drop='first'), categorical_features)
        ]
    )
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=RANDOM_STATE
    )
    
    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])
    
    return pipeline
```

## Python Package Management

**requirements.txt:**
```txt
pandas==2.1.0
numpy==1.24.0
scikit-learn==1.3.0
matplotlib==3.7.0
seaborn==0.12.0
statsmodels==0.14.0
pingouin==0.5.3
plotly==5.17.0
jupyter==1.0.0
ipykernel==6.25.0
```

**environment.yml (Conda):**
```yaml
name: medical_data_science
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pandas=2.1.0
  - numpy=1.24.0
  - scikit-learn=1.3.0
  - matplotlib=3.7.0
  - seaborn=0.12.0
  - statsmodels=0.14.0
  - jupyter
  - pip
  - pip:
    - pingouin==0.5.3
    - plotly==5.17.0
```

## Common Python Pitfalls (Avoid)

🚩 **Not setting random seeds** → Non-reproducible ML results  
🚩 **Using mutable default arguments** → `def func(x=[])` is wrong  
🚩 **Not using type hints** → Harder to debug  
🚩 **Importing with `*`** → Namespace pollution  
🚩 **Not using virtual environments** → Dependency conflicts  
🚩 **Hardcoding paths** → Breaks portability (use `pathlib.Path`)  
🚩 **Not handling missing data explicitly** → Silent failures  
🚩 **Using `==` for floating point** → Use `np.isclose()` instead  

## Python Self-Assessment Checklist

Before submitting Python code:
- [ ] Script runs from top to bottom without errors
- [ ] Random seed set for reproducibility
- [ ] Type hints included for functions
- [ ] Virtual environment used
- [ ] Requirements.txt up to date
- [ ] Paths use `pathlib.Path` (not strings)
- [ ] Missing data handled explicitly
- [ ] Code follows PEP 8 style guide
- [ ] Docstrings included for functions/classes
- [ ] Tests written for critical functions

## Related Hubs

- [Folder index hub](../../../docs/FOLDER_INDEX.md)
- [All notes index](../../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../../docs/GRAPH_CONNECTIVITY_MAP.md)
