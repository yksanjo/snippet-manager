#!/usr/bin/env python3
"""Setup script for Snippet Manager."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="snippet-manager",
    version="1.0.0",
    author="Developer",
    description="Save, tag, and quickly retrieve code snippets with fuzzy search and syntax highlighting",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/snippet-manager",
    py_modules=["snippet_manager"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pygments>=2.15.0",
        "pyperclip>=1.8.0",
    ],
    entry_points={
        "console_scripts": [
            "snippet=snippet_manager:main",
        ],
    },
)
