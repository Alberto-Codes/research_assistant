from setuptools import setup, find_packages

# Read version from __init__.py
with open("src/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"\'')
            break
    else:
        version = "0.1.0"  # Default if version not found

setup(
    name="research_agent",
    version=version,
    description="A simple research agent using pydantic-graph",
    author="Alberto-Codes",
    author_email="94092485+Alberto-Codes@users.noreply.github.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "pydantic-graph",
        "pydantic-ai",
        "streamlit",
    ],
    extras_require={
        "dev": [
            "black",
            "isort",
            "pytest",
            "pytest-asyncio",
            "pylint",
            "flake8",
            "bandit",
            "mypy",
            "build",
            "wheel",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        "console_scripts": [
            "research_agent=hello_world.cli.commands:cli_entry",
        ],
    },
) 