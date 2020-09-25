import pathlib
from setuptools import setup,find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()
DESCRIPTION="Easy to use Python client for IBM Security Identity Manager (ISIM/ITIM) web services (SOAP and REST APIs) "

setup(
  name="pyisim",
  version="0.0.1",
  description=DESCRIPTION,
  long_description=README,
  long_description_content_type="text/markdown",
  author="Camilo Andrés Zamora",
  author_email="cazdlt@gmail.com",
  license="MIT",
  packages=find_packages(),
  zip_safe=False
)