from setuptools import setup, find_packages

# Read the requirements from requirements.txt
with open('../requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="exalt_fr_lib",
    version="1.0.0",
    packages=find_packages(
        where='.',
        exclude=["back"]
    ),
    install_requires=requirements,
)
