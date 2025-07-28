from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() for line in fh if line.strip() and not line.startswith("#")
    ]

setup(
    name="upstox",
    version="1.0.0",
    author="Upstox Python Client",
    author_email="support@upstox.com",
    description="Python client library for Upstox API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/upstox/upstox-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="upstox, trading, api, finance, stocks, mutual funds",
    project_urls={
        "Bug Reports": "https://github.com/upstox/upstox-python/issues",
        "Source": "https://github.com/upstox/upstox-python",
        "Documentation": "https://upstox.com/developer/api-documentation/open-api",
    },
)
