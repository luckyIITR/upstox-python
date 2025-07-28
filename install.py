#!/usr/bin/env python3
"""
Installation script for Upstox Python client.

This script helps users install the Upstox client library and its dependencies.
"""

import subprocess
import sys
import os


def install_requirements():
    """Install required dependencies."""
    print("Installing required dependencies...")

    requirements = [
        "requests>=2.25.0",
        "websocket-client>=1.0.0",
        "six>=1.15.0",
        "python-dateutil>=2.8.0",
    ]

    for requirement in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", requirement])
            print(f"✓ Installed {requirement}")
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {requirement}")
            return False

    return True


def install_package():
    """Install the Upstox package."""
    print("Installing Upstox Python client...")

    try:
        subprocess.check_call([sys.executable, "setup.py", "install"])
        print("✓ Upstox Python client installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install Upstox Python client")
        return False


def main():
    """Main installation function."""
    print("=== Upstox Python Client Installation ===\n")

    # Check Python version
    if sys.version_info < (3, 7):
        print("✗ Python 3.7 or higher is required")
        sys.exit(1)

    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

    # Install requirements
    if not install_requirements():
        print("\n✗ Failed to install dependencies")
        sys.exit(1)

    # Install package
    if not install_package():
        print("\n✗ Failed to install package")
        sys.exit(1)

    print("\n=== Installation completed successfully! ===")
    print("\nYou can now use the Upstox Python client:")
    print(
        """
    from upstox import Upstox
    
    # Initialize client
    upstox = Upstox(api_key="your_api_key")
    
    # Get login URL
    login_url = upstox.get_login_url("your_redirect_uri")
    
    # For more examples, check the examples/ directory
    """
    )


if __name__ == "__main__":
    main()
