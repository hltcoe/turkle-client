import os
import setuptools


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), "r") as fh:
        return fh.read()


with open("turkle_client/__version__.py") as fp:
    ns = {}
    exec(fp.read(), ns)

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="turkle-client",
    version=ns['__version__'],
    description="Client for the Turkle REST API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="BSD",
    python_requires=">=3.7",
    packages=setuptools.find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=read("requirements.txt"),
    entry_points={
        "console_scripts": [
            "turkle-client = turkle_client.bin:main",
        ]
    }
)
