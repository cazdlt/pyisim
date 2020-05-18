import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="isimws",
    version="0.1",
    author="Andrés Zamora",
    author_email="cazdlt@gmail.com",
    description="Cliente para los webservice de IBM SIM",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cazdlt/isimws",
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
)