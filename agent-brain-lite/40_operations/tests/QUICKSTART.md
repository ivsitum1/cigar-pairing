# Pytest Quick Start Guide

Quick guide for running tests in the project.

## 🚀 Quick Installation

```bash
pip install -r requirements.txt
```

## ▶️ Running Tests

### ⚡ Watch Mode (Recommended - automatically runs tests!)

```bash
# Install pytest-watch
pip install pytest-watch

# Run watch mode - tests run automatically when you save a file!
python -m pytest_watch

# Or directly (if ptw is on PATH)
ptw
```

**To stop:** Press `Ctrl+C`

### Manual run
```bash
pytest
```

### With details
```bash
pytest -v
```

### Parallel (faster)
```bash
pytest -n auto
```

### With coverage report
```bash
pytest --cov=behavior_rules --cov=reference_library --cov-report=html
# Open htmlcov/index.html in browser
```

## 📋 Common Commands

| Command | Description |
|---------|-------------|
| `ptw` | **Watch mode** - automatically runs tests on changes |
| `pytest` | Run all tests (manual) |
| `pytest -v` | Verbose output |
| `pytest -n auto` | Parallel execution |
| `pytest --tldr` | Minimal output |
| `pytest -m unit` | Only unit tests |
| `pytest --lf` | Run last failed tests |
| `pytest --cov` | Coverage report |
| `pytest --timeout=30` | Timeout for tests |

## 🎯 Examples

```bash
# Test specific module
pytest 40_operations/tests/30_system/behavior_rules/tools/

# Test specific function
pytest 40_operations/tests/30_system/behavior_rules/tools/test_check_ai_plagiarism.py::TestCalculateBasicAIScore

# Test with coverage
pytest --cov=30_system/behavior_rules/tools --cov-report=term-missing

# Test without slow tests
pytest -m "not slow"
```

## 📖 More Information

See [40_operations/tests/README.md](index.md) for detailed instructions.

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
