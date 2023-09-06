import io
import os

from setuptools import find_namespace_packages, setup

DEPENDENCIES = "urllib3<2.0"

package_root = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(package_root, "daaily/version.py")) as fp:
    exec(fp.read(), version)
version = version["__version__"]

with io.open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="daaily",
    version=version,
    author="DAAily Platforms",
    author_email="dev@daaily.com",
    description="Daaily API Library",
    long_description=long_description,
    url="https://github.com/DAAily/daailyapis-python-client",
    # package_dir = {"": "src"},
    # packages = setuptools.find_packages(where="src"),
    packages=find_namespace_packages(exclude=("tests*", "samples*")),
    install_requires=DEPENDENCIES,
    # extras_require=extras,
    python_requires=">=3.10",
    license="Apache 2.0",
)
