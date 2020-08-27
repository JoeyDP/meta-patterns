import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

version = os.environ.get("VERSION", "0.0.1")

setuptools.setup(
    name="meta-patterns",
    version=str(version),
    author="JoeyDP",
    author_email="joeydepauw@gmail.com",
    description="Design patterns for Python implemented with decorators and classes.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JoeyDP/meta-patterns",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
) 
