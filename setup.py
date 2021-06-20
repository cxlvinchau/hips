from distutils.core import setup
import setuptools

with open("requirements.txt") as file:
      requirements = file.readlines()

setup(name="hips-mip",
      version="0.3dev",
      author="Calvin Chau",
      author_email="calvin.chau@tum.de",
      package_dir={"": "src"},
      packages = setuptools.find_packages(where="hips"),
      python_requires=">=3.8",
      install_requires=requirements
      )
