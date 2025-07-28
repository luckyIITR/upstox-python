# Publishing Guide for Upstox Python Client

This guide covers the complete process of publishing your Python client library to GitHub and PyPI.

## Prerequisites

### 1. GitHub Account Setup
- Create a GitHub account if you don't have one
- Set up SSH keys or use HTTPS for repository access
- Enable two-factor authentication for security

### 2. PyPI Account Setup
- Create an account on [PyPI](https://pypi.org/)
- Create an account on [Test PyPI](https://test.pypi.org/) for testing
- Generate API tokens for both accounts

### 3. Local Development Environment
```bash
# Install required tools
pip install build twine pytest black flake8 mypy

# Verify your setup
python -m build --version
twine --version
```

## Step-by-Step Publishing Process

### Step 1: Prepare Your Repository

1. **Initialize Git** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **Create GitHub Repository**:
   - Go to GitHub and create a new repository
   - Name it `upstox-python` (or your preferred name)
   - Make it public
   - Don't initialize with README (you already have one)

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/your-username/upstox-python.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Configure GitHub Secrets

1. **Go to your repository settings** on GitHub
2. **Navigate to Secrets and variables → Actions**
3. **Add the following secrets**:
   - `PYPI_API_TOKEN`: Your PyPI API token
   - `TEST_PYPI_API_TOKEN`: Your Test PyPI API token (optional)

### Step 3: Test Your Package Locally

1. **Build the package**:
   ```bash
   python -m build
   ```

2. **Test installation**:
   ```bash
   pip install dist/*.whl
   python -c "import upstox; print('Installation successful!')"
   ```

3. **Run tests**:
   ```bash
   pytest tests/
   ```

4. **Check code quality**:
   ```bash
   black --check .
   flake8 .
   mypy upstox/
   ```

### Step 4: Test on Test PyPI

1. **Upload to Test PyPI**:
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. **Test installation from Test PyPI**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ upstox
   ```

### Step 5: Create Your First Release

1. **Update version numbers**:
   - Update `pyproject.toml` version
   - Update `setup.py` version
   - Update `CHANGELOG.md`

2. **Commit and push changes**:
   ```bash
   git add .
   git commit -m "Bump version to 1.0.0"
   git push
   ```

3. **Create and push a tag**:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

4. **Create GitHub Release**:
   - Go to GitHub → Releases → Create a new release
   - Tag: `v1.0.0`
   - Title: `v1.0.0 - Initial Release`
   - Description: Copy from CHANGELOG.md
   - Upload the built files from `dist/`

### Step 6: Publish to PyPI

1. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

2. **Verify on PyPI**:
   - Visit https://pypi.org/project/upstox/
   - Test installation: `pip install upstox`

## Automated Publishing with GitHub Actions

The repository includes GitHub Actions workflows that automate:

### CI/CD Pipeline (`.github/workflows/ci.yml`)
- Runs on every push and pull request
- Tests against multiple Python versions
- Runs linting and type checking
- Generates coverage reports

### Release Pipeline (`.github/workflows/release.yml`)
- Triggers on tag pushes
- Automatically builds and publishes to PyPI
- Creates GitHub releases

### Dependency Review (`.github/workflows/dependency-review.yml`)
- Scans dependencies for security vulnerabilities
- Runs on pull requests

## Maintenance and Updates

### Version Management

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes (1.0.0 → 2.0.0)
- **MINOR**: New features (1.0.0 → 1.1.0)
- **PATCH**: Bug fixes (1.0.0 → 1.0.1)

### Release Process

1. **Update version** in `pyproject.toml` and `setup.py`
2. **Update CHANGELOG.md** with new changes
3. **Commit and push** changes
4. **Create and push tag**: `git tag v1.0.1 && git push origin v1.0.1`
5. **GitHub Actions** will automatically publish to PyPI

### Documentation Updates

- Keep `README.md` updated with new features
- Update examples in `examples/` directory
- Maintain API documentation in `docs/`
- Update `CHANGELOG.md` for each release

## Best Practices

### Code Quality
- Run tests before every commit
- Use pre-commit hooks for automatic formatting
- Maintain high test coverage
- Follow PEP 8 style guidelines

### Security
- Regularly update dependencies
- Monitor for security vulnerabilities
- Use dependency scanning tools
- Keep API keys secure

### Documentation
- Write clear, comprehensive docstrings
- Provide working examples
- Keep README.md up to date
- Document breaking changes clearly

### Community
- Respond to issues promptly
- Review pull requests thoroughly
- Welcome contributions from the community
- Maintain a code of conduct

## Troubleshooting

### Common Issues

1. **Build fails**:
   - Check `pyproject.toml` syntax
   - Verify all dependencies are listed
   - Check for missing `__init__.py` files

2. **Upload fails**:
   - Verify PyPI credentials
   - Check if version already exists
   - Ensure package name is unique

3. **Tests fail**:
   - Check Python version compatibility
   - Verify all dependencies are installed
   - Check for environment-specific issues

4. **Import errors**:
   - Verify package structure
   - Check `__init__.py` files
   - Ensure proper namespace

### Getting Help

- Check existing issues on GitHub
- Review PyPI documentation
- Consult Python packaging guides
- Ask in Python community forums

## Advanced Topics

### Multi-platform Support
- Test on different operating systems
- Use GitHub Actions matrix builds
- Consider platform-specific dependencies

### Performance Optimization
- Profile your code
- Optimize critical paths
- Use appropriate data structures
- Consider async operations

### API Versioning
- Plan for API changes
- Maintain backward compatibility
- Use deprecation warnings
- Document migration guides

## Resources

- [Python Packaging User Guide](https://packaging.python.org/)
- [PyPI Documentation](https://pypi.org/help/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/) 