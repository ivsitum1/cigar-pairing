# Test Suite - Agent Rules Project

This directory contains tests for Python modules in the project. We use **pytest** with advanced plugins for improved testing.

## 📦 Installation

Install all required packages:

```bash
pip install -r requirements.txt
```

Or only test packages:

```bash
pip install pytest pytest-xdist pytest-randomly pytest-cov pytest-instafail pytest-tldr pytest-timeout pytest-mpl
```

## 🚀 Running Tests

### ⚡ Watch Mode (Recommended for Development)

**Automatically runs tests when you save a file!**

```bash
# Install pytest-watch (if not already installed)
pip install pytest-watch

# Run watch mode (recommended)
python -m pytest_watch

# Or directly (if ptw is on PATH)
ptw

# With additional options
python -m pytest_watch --runner "pytest -v"
python -m pytest_watch --runner "pytest -n auto"  # Parallel execution
python -m pytest_watch --runner "pytest --tldr"   # Minimal output
```

**When it runs:** Automatically when you save any Python file in the project

**Benefits:**
- ✅ Instant feedback - see errors immediately
- ✅ No need to run tests manually
- ✅ Focus on code, not commands
- ✅ Detects changes in test files and source files

**To stop:** Press `Ctrl+C`

### Basic running (manual)

```bash
# Run all tests
pytest

# Run tests with detailed output
pytest -v

# Run tests in a specific directory
pytest 40_operations/tests/30_system/behavior_rules/

# Run a specific test file
pytest 40_operations/tests/30_system/behavior_rules/tools/test_check_ai_plagiarism.py
```

### Advanced options

```bash
# Parallel execution (uses multiple CPU cores)
pytest -n auto

# Run only fast tests (without @pytest.mark.slow)
pytest -m "not slow"

# Run only unit tests
pytest -m unit

# Run with coverage report
pytest --cov=behavior_rules --cov=reference_library --cov-report=html

# Minimal output (only tracebacks for failed 40_operations/tests)
pytest --tldr

# Run tests with timeout (prevents infinite loops)
pytest --timeout=30
```

## 🔧 Pytest Plugins

### 1. **pytest-xdist** - Parallel execution
Speeds up tests using multiple CPU cores.

```bash
# Automatically determines number of workers
pytest -n auto

# Use specific number of processes
pytest -n 4
```

**Benefits:**
- Faster test execution
- Automatic distribution of tests across available processors

### 2. **pytest-randomly** - Random test order
Reduces risk of inter-test dependencies.

```bash
# Automatically active (in pytest.ini)
pytest

# With specific seed (for reproducibility)
pytest --randomly-seed=12345
```

**Benefits:**
- Reveals hidden dependencies between tests
- Helps identify issues with global state

### 3. **pytest-cov** - Coverage reporting
Shows which parts of code are covered by tests.

```bash
# Terminal report
pytest --cov=behavior_rules --cov-report=term-missing

# HTML report (open htmlcov/index.html)
pytest --cov=behavior_rules --cov-report=html

# XML report (for CI/CD)
pytest --cov=behavior_rules --cov-report=xml
```

**Benefits:**
- Identifies untested code
- Helps maintain high coverage

### 4. **pytest-instafail** - Show errors immediately
Shows errors as soon as they occur instead of waiting for all tests to finish.

```bash
# Automatically active (in pytest.ini)
pytest --instafail
```

**Benefits:**
- Faster problem diagnosis
- No need to wait for all tests to complete

### 5. **pytest-tldr** - Minimal output
Limits output to tracebacks for failed tests only.

```bash
pytest --tldr
```

**Benefits:**
- Cleaner output
- Focus on errors

### 6. **pytest-timeout** - Timeout for tests
Stops tests that run too long (likely infinite loops).

```bash
# Global timeout (30 seconds - set in pytest.ini)
pytest --timeout=30

# Timeout for specific test
@pytest.mark.timeout(10)
def test_slow_function():
    ...
```

**Benefits:**
- Prevents infinite loops
- Identifies slow tests

### 7. **pytest-mpl** - Matplotlib testing
Tests Matplotlib figures through image comparison.

```bash
# Generate baseline images
pytest --mpl-generate-path=40_operations/tests/baseline

# Compare with baseline images
pytest --mpl
```

**Benefits:**
- Automatic visualization testing
- Detects unexpected changes in plots

## 📁 Test Structure

```
40_operations/tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── README.md                # This file
├── 30_system/behavior_rules/
│   └── tools/
│       ├── test_check_ai_plagiarism.py
│       └── test_track_versions.py
├── 20_knowledge/reference_library/
│   └── tools/
│       └── test_catalog_pdfs.py
├── unit/                    # Fast, isolated tests
└── integration/             # Slower, integration tests
```

## 🏷️ Markers

Use markers to categorize tests:

```python
@pytest.mark.unit
def test_fast_function():
    """Fast unit test."""
    pass

@pytest.mark.integration
def test_api_call():
    """Slower integration test."""
    pass

@pytest.mark.slow
def test_heavy_computation():
    """Slow test."""
    pass

@pytest.mark.api
def test_external_api():
    """Test requiring API access."""
    pass
```

Running tests by markers:

```bash
# Only unit tests
pytest -m unit

# Without slow tests
pytest -m "not slow"

# Only API tests
pytest -m api
```

## 🔍 Test Examples

### Unit Test Example

```python
def test_calculate_ai_score():
    """Test for calculate_basic_ai_score function."""
    from check_ai_plagiarism import calculate_basic_ai_score
    
    text = "Short text."
    score = calculate_basic_ai_score(text)
    
    assert score == 0.0
    assert 0.0 <= score <= 1.0
```

### Test with Fixture

```python
def test_with_temp_dir(temp_dir):
    """Test using temporary directory."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("content")
    
    assert test_file.exists()
    assert test_file.read_text() == "content"
```

### Test with Mock

```python
from unittest.mock import patch

@patch('check_ai_plagiarism.requests.get')
def test_api_call(mock_get):
    """Test with mocked API call."""
    mock_get.return_value.json.return_value = {"status": "ok"}
    
    # Test code here
    ...
```

## 📊 Coverage Targets

- **Minimum:** 70% coverage
- **Target:** 80%+ coverage
- **Ideal:** 90%+ coverage

Check coverage:

```bash
pytest --cov=behavior_rules --cov=reference_library --cov-report=term-missing --cov-report=html
```

Open `htmlcov/index.html` in browser for detailed report.

## 🐛 Debugging Tests

```bash
# Run with debug output
pytest -vv --tb=long

# Run with pdb debugger (for interactive debugging)
pytest --pdb

# Run only last failed test
pytest --lf  # last failed
```

## 🔄 CI/CD Integration

For automatic test runs in CI/CD pipeline:

```yaml
# Example for GitHub Actions
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest --cov=behavior_rules --cov=reference_library --cov-report=xml --junitxml=test-results.xml
```

## 📝 Best Practices

1. **Naming:** Test files should start with `test_`
2. **Isolation:** Each test should be independent
3. **Fixtures:** Use fixtures for shared resources
4. **Markers:** Mark tests with markers for easier filtering
5. **Documentation:** Add docstrings to tests
6. **Assert messages:** Use descriptive assert messages

## 🆘 Troubleshooting

### Problem: Tests do not run
```bash
# Check if pytest is installed
pytest --version

# Check if test files are in the right place
pytest --collect-only
```

### Problem: Import errors
```bash
# Add project to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Problem: Slow tests
```bash
# Use parallel execution
pytest -n auto

# Identify slow tests
pytest --durations=10
```

## 📚 Additional Resources

- [Pytest documentation](https://docs.pytest.org/)
- [Pytest-xdist documentation](https://pytest-xdist.readthedocs.io/)
- [Pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Pytest best practices](https://docs.pytest.org/en/stable/goodpractices.html)

---

**Note:** This test suite is designed to be continuously extended. Add new tests as the project grows!

## Related Hubs

- [Folder index hub](../../30_system/docs/FOLDER_INDEX.md)
- [All notes index](../../30_system/docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
