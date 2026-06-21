from setuptools import setup, find_packages

setup(
    name="text_to_sql",
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
    python_requires=">=3.8",
)
