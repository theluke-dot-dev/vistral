# Contributing to Vistral

First off, thank you for considering contributing to Vistral! Your help is greatly appreciated.

## Development Setup

Please refer to the "Development Setup" section in the main `README.md` file for instructions on how to set up your development environment using Poetry.

## Running Tests

Vistral uses `pytest` for running automated tests.

To run the test suite:

```bash
poetry run pytest
```

### Test Coverage

We use `pytest-cov` (via `coverage.py`) to measure test coverage. The configuration for coverage is located in `pyproject.toml` under the `[tool.coverage.run]` and `[tool.coverage.report]` sections.

**To run tests and generate coverage data:**

The primary test task defined in `taskfile.yml` (or its underlying command) already collects coverage data.

```bash
# If using Task Go (taskfile.dev) - this runs pytest with coverage
task test:pytest 

# Or, run the command directly:
poetry run pytest --cov src
```
This command will run all tests and create a `.coverage` data file. It will also print a summary of coverage to the terminal.

**To view the coverage report in the terminal:**

This provides a quick summary of coverage per file.

```bash
# If using Task Go:
task test:coverage-report

# Or, run the command directly:
poetry run coverage report
```

**To generate an HTML coverage report:**

This generates a detailed, interactive HTML report in the `htmlcov/` directory. Open `htmlcov/index.html` in your browser to view it.

```bash
# If using Task Go:
task test:coverage-html

# Or, run the command directly:
poetry run coverage html
```

We encourage contributors to ensure that new code is adequately covered by tests and to check the coverage report to identify areas that may need more testing.

## Coding Standards

*   **Formatting:** We use Black for code formatting and isort for import sorting. Please run these tools before committing.
    *   `poetry run black src tests`
    *   `poetry run isort src tests`
*   **Linting:** We use Ruff and MyPy for linting and type checking.
    *   `poetry run ruff check src tests`
    *   `poetry run mypy --config-file pyproject.toml src`
*   **Taskfile:** You can use `task lint` to run all formatting and linting checks.

## Submitting Changes

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes, including tests and documentation updates.
4.  Ensure all tests and linting checks pass.
5.  Submit a pull request with a clear description of your changes.

Thank you for contributing!
