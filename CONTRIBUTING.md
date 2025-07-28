# Contributing to Upstox Python Client

Thank you for your interest in contributing to the Upstox Python Client! This document provides guidelines and information for contributors.

## Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/upstox-python.git
   cd upstox-python
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```
5. **Install development dependencies**:
   ```bash
   pip install pytest pytest-cov black flake8 mypy
   ```

## Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking

### Running Code Quality Checks

```bash
# Format code
black .

# Check formatting
black --check --diff .

# Lint code
flake8 .

# Type checking
mypy upstox/
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=upstox --cov-report=html

# Run specific test file
pytest tests/test_upstox.py

# Run specific test
pytest tests/test_upstox.py::test_specific_function
```

### Writing Tests

- Tests should be in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external API calls
- Use fixtures for common setup

Example test structure:
```python
import pytest
from unittest.mock import Mock, patch
from upstox import Upstox

class TestUpstoxClient:
    def setup_method(self):
        self.client = Upstox(api_key="test_key")
    
    def test_successful_api_call(self):
        # Test implementation
        pass
    
    def test_api_error_handling(self):
        # Test error handling
        pass
```

## Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit them:
   ```bash
   git add .
   git commit -m "Add feature: description of changes"
   ```

3. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Create a Pull Request** on GitHub

### Pull Request Guidelines

- **Title**: Clear, descriptive title
- **Description**: Explain what the PR does and why
- **Tests**: Include tests for new functionality
- **Documentation**: Update docs if needed
- **Code Quality**: Ensure all checks pass

### Commit Message Format

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

## Release Process

### For Maintainers

1. **Update version** in `pyproject.toml` and `setup.py`
2. **Update CHANGELOG.md** with new changes
3. **Create a release** on GitHub
4. **Tag the release** with version number
5. **Publish to PyPI** (automated via GitHub Actions)

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

## Documentation

### Updating Documentation

- Update `README.md` for user-facing changes
- Update docstrings for API changes
- Update examples in `examples/` directory
- Update API reference in `docs/API_REFERENCE.md`

### Building Documentation

```bash
# Install documentation dependencies
pip install sphinx sphinx-rtd-theme

# Build documentation
cd docs
make html
```

## Getting Help

- **Issues**: Create an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Code Review**: All PRs require review before merging

## Code of Conduct

Please be respectful and inclusive in all interactions. We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/0/code_of_conduct/).

## License

By contributing, you agree that your contributions will be licensed under the MIT License. 