from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="model-agnostic-text-to-sql",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy>=2.0.0",
    ],
    extras_require={
        "test": [
            "pytest>=8.0.0",
        ]
    },
    author="Adnan Ahmad",
    description="A model-agnostic, database-agnostic Text-to-SQL Python library.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
)
