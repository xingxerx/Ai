"""
Setup script for the AGI Agent.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="agi-agent",
    version="0.1.0",
    author="AGI Agent Development Team",
    author_email="dev@agi-agent.com",
    description="A general-purpose artificial general intelligence agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/agi-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.11.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "web": [
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
            "jinja2>=3.1.0",
        ],
        "full": [
            "selenium>=4.15.0",
            "neo4j>=5.12.0",
            "torch>=2.0.0",
            "transformers>=4.30.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "agi-agent=agi_agent.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "agi_agent": [
            "templates/*.yaml",
            "config/*.json",
        ],
    },
)
