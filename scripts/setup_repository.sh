#!/bin/bash

# Upstox Python Client - Repository Setup Script
# This script helps set up the repository for publishing to GitHub and PyPI

set -e

echo "🚀 Setting up Upstox Python Client repository..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

print_status "Checking prerequisites..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi

# Check if python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3 first."
    exit 1
fi

print_success "Prerequisites check passed"

# Install development dependencies
print_status "Installing development dependencies..."
pip3 install build twine pytest black flake8 mypy

# Initialize git repository if not already done
if [ ! -d ".git" ]; then
    print_status "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: Upstox Python Client"
    print_success "Git repository initialized"
else
    print_status "Git repository already exists"
fi

# Build the package
print_status "Building package..."
python3 -m build

# Test the build
print_status "Testing package installation..."
pip3 install dist/*.whl --force-reinstall
python3 -c "import upstox; print('✅ Package installation test successful!')"

# Run tests
print_status "Running tests..."
python3 -m pytest tests/ -v

# Run code quality checks
print_status "Running code quality checks..."
python3 -m black --check .
python3 -m flake8 .
python3 -m mypy upstox/

print_success "All checks passed!"

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    print_warning ".gitignore file not found. Please create one manually."
fi

# Display next steps
echo ""
echo "🎉 Repository setup complete!"
echo ""
echo "Next steps:"
echo "1. Create a GitHub repository at https://github.com/new"
echo "2. Add your GitHub repository as remote:"
echo "   git remote add origin https://github.com/your-username/upstox-python.git"
echo "3. Push to GitHub:"
echo "   git push -u origin main"
echo "4. Set up GitHub Secrets (PYPI_API_TOKEN) in repository settings"
echo "5. Create your first release:"
echo "   git tag v1.0.0"
echo "   git push origin v1.0.0"
echo ""
echo "📚 For detailed instructions, see PUBLISHING_GUIDE.md"
echo "🔧 For development guidelines, see CONTRIBUTING.md"
echo "" 