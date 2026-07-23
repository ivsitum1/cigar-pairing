# Reproducibility Setup (MANDATORY)

**CRITICAL RULE:** When generating code for statistical analyses (RCTs, meta-analyses, data processing), you MUST automatically create a complete reproducibility environment. This is not optional.

## What to Generate Automatically

### For R Projects

#### 1. renv initialization code (at project start)

```r
# Initialize renv if not already done
if (!requireNamespace("renv", quietly = TRUE)) {
  install.packages("renv")
}
if (!file.exists("renv/renv.lock")) {
  renv::init()
}
renv::activate()
```

#### 2. Session info at end of EVERY analysis script

```r
# SESSION INFO - DO NOT REMOVE
# Save session info to file
library(here)
PROJECT_ROOT <- here()
# Alternative: Manual path if here::here() doesn't work
# PROJECT_ROOT <- "C:/path/to/your/project"  # CHANGE THIS

session_dir <- file.path(PROJECT_ROOT, "session_info")
if (!dir.exists(session_dir)) dir.create(session_dir, recursive = TRUE)
session_file <- file.path(session_dir, paste0("session_info_", format(Sys.Date(), "%Y%m%d"), ".txt"))
sink(session_file)
cat("=== SESSION INFO ===\n")
cat("Date:", format(Sys.time(), "%Y-%m-%d %H:%M:%S"), "\n")
cat("R version:", R.version.string, "\n")
cat("Platform:", R.version$platform, "\n")
cat("Working directory:", getwd(), "\n")
print(sessionInfo(), locale = FALSE)
sink()

# Also print to console
sessionInfo()
```

#### 3. renv snapshot reminder in script header

```r
# REPRODUCIBILITY:
# - Run renv::snapshot() after installing new packages
# - Session info saved to session_info/session_info_YYYYMMDD.txt
```

### For Python Projects

#### 1. environment.yml file (MUST create if not exists)

```yaml
name: [project_name]
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pandas>=2.0.0
  - numpy>=1.24.0
  - scipy>=1.11.0
  - statsmodels>=0.14.0
  - scikit-learn>=1.3.0
  - matplotlib>=3.7.0
  - seaborn>=0.12.0
  - jupyter
  - pip
  - pip:
    - pingouin>=0.5.3
```

#### 2. Environment setup code at start of analysis scripts

```python
#!/usr/bin/env python3
"""
Setup instructions:
1. Create conda environment: conda env create -f environment.yml
2. Activate: conda activate [project_name]
3. Verify: python --version
"""

import sys
import platform
import os
from datetime import datetime

# Save environment info
def save_environment_info():
    """Save Python environment information for reproducibility."""
    PROJECT_ROOT = os.getcwd()
    # Alternative: Manual path if needed
    # PROJECT_ROOT = r"C:\path\to\your\project"  # CHANGE THIS
    
    env_dir = os.path.join(PROJECT_ROOT, "session_info")
    os.makedirs(env_dir, exist_ok=True)
    
    env_file = os.path.join(env_dir, f"python_env_{datetime.now().strftime('%Y%m%d')}.txt")
    with open(env_file, 'w') as f:
        f.write("=== PYTHON ENVIRONMENT INFO ===\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Python version: {sys.version}\n")
        f.write(f"Platform: {platform.platform()}\n")
        f.write(f"Architecture: {platform.architecture()}\n")
        f.write(f"Working directory: {os.getcwd()}\n")
        f.write("\n=== INSTALLED PACKAGES ===\n")
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                              capture_output=True, text=True)
        f.write(result.stdout)
    
    print(f"Environment info saved to {env_file}")

# Call at start of analysis
save_environment_info()
```

#### 3. requirements.txt backup (also generate)

```txt
# Python package requirements
# Primary: Use environment.yml for conda
# This file is a backup for pip-only installations

pandas>=2.0.0
numpy>=1.24.0
scipy>=1.11.0
statsmodels>=0.14.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
pingouin>=0.5.3
```

### README.md Setup Instructions (MUST include)

Always generate or update README.md with:

```markdown
## Environment Setup

### R Environment
1. Install R (version 4.3.0 or higher recommended)
2. Install renv: `install.packages("renv")`
3. Restore packages: `renv::restore()`
4. Verify: Check `session_info/session_info_YYYYMMDD.txt` after running analysis

**Note:** Working directory paths can be set manually using `setwd()` or `here::here()`. 
All reviewers should know how to set paths in R.

### Python Environment
1. Install Miniconda or Anaconda
2. Create environment: `conda env create -f environment.yml`
3. Activate: `conda activate [project_name]`
4. Verify: `python --version` and check `session_info/python_env_YYYYMMDD.txt`

### Reproducibility
- R: `renv/renv.lock` contains all package versions
- Python: `environment.yml` contains all package versions
- Session info: Saved automatically in `session_info/` directory
- Random seeds: Set at start of each analysis script
```

### Software citation (JMLR Open Source Software)

When using packages that have a **Journal of Machine Learning Research (JMLR) Machine Learning Open Source Software** paper, cite that paper in project documentation and methods (e.g. README, supplementary, or methods section). Examples: TorchCP (conformal prediction), skglm (regularized GLMs), BoFire (Bayesian optimization), PFLlib (federated learning). Full list: [JMLR](https://www.jmlr.org/) → Papers → filter by Open Source Software. This supports reproducibility and gives proper credit to peer-reviewed software.

## Checklist Before Code Generation

- [ ] renv initialization code included (R 10_projects/projects)
- [ ] environment.yml created (Python 10_projects/projects)
- [ ] sessionInfo() code at end of R scripts
- [ ] Python environment info saving code included
- [ ] README.md includes setup instructions
- [ ] Random seed set in every script
- [ ] All package versions documented
- [ ] No hardcoded absolute paths (use PROJECT_ROOT variable with here::here())
- [ ] PROJECT_ROOT set using here::here() or manual path (adjustable for each project)

## What NOT to Generate

- ❌ Docker files (not needed for statistical analyses)
- ❌ Complex containerization setup
- ❌ System-level dependencies (assume standard R/Python installation)

## Related Hubs

- [Folder index hub](../../../docs/FOLDER_INDEX.md)
- [All notes index](../../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../../docs/GRAPH_CONNECTIVITY_MAP.md)
