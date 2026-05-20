from setuptools import setup, find_packages

setup(
    name="brax-agent",
    version="1.0.0",
    description="Open Source Multi-Agent AI Dev Team",
    packages=find_packages(include=["brax", "brax.*"]),
    include_package_data=True,
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.0.0",
        "httpx>=0.25.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "gitpython>=3.1.0",
        "textual>=0.52.0",
    ],
    extras_require={
        "all": [
            "anthropic>=0.30.0",
            "openai>=1.0.0",
            "groq>=0.5.0",
            "ollama>=0.1.0",
        ],
        "anthropic": ["anthropic>=0.30.0"],
        "openai": ["openai>=1.0.0"],
        "groq": ["groq>=0.5.0"],
        "ollama": ["ollama>=0.1.0"],
    },
    entry_points={
        "console_scripts": [
            "brax=brax.cli.main:app"
        ]
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Code Generators",
    ],
)
