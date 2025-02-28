from setuptools import setup, find_packages

setup(
    name="research_agent",
    version="0.1.0",
    description="A simple research agent using pydantic-graph",
    author="Alberto-Codes",
    author_email="94092485+Alberto-Codes@users.noreply.github.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
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
            "research_agent=main:main",
        ],
    },
) 