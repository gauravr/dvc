import importlib.util
import os
import sys

from setuptools import find_packages, setup
from setuptools.command.build_py import build_py as _build_py

# Prevents pkg_resources import in entry point script,
# see https://github.com/ninjaaron/fast-entry_points.
# This saves about 200 ms on startup time for non-wheel installs.
import fastentrypoints  # noqa: F401


# Read package meta-data from version.py
# see https://packaging.python.org/guides/single-sourcing-package-version/
pkg_dir = os.path.dirname(os.path.abspath(__file__))
version_path = os.path.join(pkg_dir, "dvc", "version.py")
spec = importlib.util.spec_from_file_location("dvc.version", version_path)
dvc_version = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dvc_version)
version = dvc_version.__version__  # noqa: F821


# To achieve consistency between the build version and the one provided
# by your package during runtime, you need to **pin** the build version.
#
# This custom class will replace the version.py module with a **static**
# `__version__` that your package can read at runtime, assuring consistency.
#
# References:
#   - https://docs.python.org/3.7/distutils/extending.html
#   - https://github.com/python/mypy
class build_py(_build_py):
    def pin_version(self):
        path = os.path.join(self.build_lib, "dvc")
        self.mkpath(path)
        with open(os.path.join(path, "version.py"), "w") as fobj:
            fobj.write("# AUTOGENERATED at build time by setup.py\n")
            fobj.write('__version__ = "{}"\n'.format(version))

    def run(self):
        self.execute(self.pin_version, ())
        _build_py.run(self)


install_requires = [
    "python-dateutil<2.8.1,>=2.1",  # Consolidates azure-blob-storage and boto3
    "ply>=3.9",  # See https://github.com/pyinstaller/pyinstaller/issues/1945
    "colorama>=0.3.9",
    "configobj>=5.0.6",
    "gitpython>3",
    "setuptools>=34.0.0",
    "nanotime>=0.5.2",
    "pyasn1>=0.4.1",
    "voluptuous>=0.11.7",
    "jsonpath-ng>=1.4.3",
    "requests>=2.22.0",
    "grandalf==0.6",
    "distro>=1.3.0",
    "appdirs>=1.4.3",
    "treelib>=1.5.5",
    "inflect>=2.1.0,<4",
    "humanize>=0.5.1",
    "PyYAML>=5.1.2,<5.2",  # Compatibility with awscli
    "ruamel.yaml>=0.16.1",
    "funcy>=1.14",
    "pathspec>=0.6.0",
    "shortuuid>=0.5.0",
    "tqdm>=4.40.0,<5",
    "packaging>=19.0",
    "zc.lockfile>=1.2.1",
    "flufl.lock>=3.2",
    "win-unicode-console>=0.5; sys_platform == 'win32'",
    "pywin32>=225; sys_platform == 'win32'",
    "networkx>=2.1,<2.4",
    "pydot>=1.2.4",
    "speedcopy>=2.0.1",
    "pyfastcopy>=1.0.3",
    "flatten_json>=0.1.6",
    "texttable>=0.5.2",
]


# Extra dependencies for remote integrations

gs = ["google-cloud-storage==1.19.0"]
gdrive = ["pydrive2>=1.4.5"]
s3 = ["boto3>=1.9.201"]
azure = ["azure-storage-blob==2.1.0"]
oss = ["oss2==2.6.1"]
ssh = ["paramiko>=2.5.0"]
hdfs = ["pyarrow==0.15.1"]
# gssapi should not be included in all_remotes, because it doesn't have wheels
# for linux and mac, so it will fail to compile if user doesn't have all the
# requirements, including kerberos itself. Once all the wheels are available,
# we can start shipping it by default.
ssh_gssapi = ["paramiko[gssapi]>=2.5.0"]
all_remotes = gs + s3 + azure + ssh + oss + gdrive + hdfs

# Extra dependecies to run tests
tests_requirements = [
    "wheel>=0.31.1",
    # Test requirements:
    "pytest>=4.6.0",
    "pytest-timeout>=1.3.3",
    "pytest-cov>=2.6.1",
    "pytest-xdist>=1.26.1",
    "pytest-mock==1.11.2",
    "flaky>=3.5.3",
    "mock>=3.0.0",
    "xmltodict>=0.11.0",
    "awscli>=1.16.297",
    "google-compute-engine==2.8.13",
    "Pygments",  # required by collective.checkdocs,
    "collective.checkdocs",
    "flake8",
    "psutil",
    "flake8-docstrings",
    "pydocstyle<4.0",
    "jaraco.windows==3.9.2",
    "mock-ssh-server>=0.6.0",
    "moto==1.3.14.dev464",
    "rangehttpserver==1.2.0",
]

if (sys.version_info) >= (3, 6):
    tests_requirements.append("black==19.10b0")

setup(
    name="dvc",
    version=version,
    description="Git for data scientists - manage your code and data together",
    long_description=open("README.rst", "r").read(),
    author="Dmitry Petrov",
    author_email="dmitry@dvc.org",
    download_url="https://github.com/iterative/dvc",
    license="Apache License 2.0",
    install_requires=install_requires,
    extras_require={
        "all": all_remotes,
        "gs": gs,
        "gdrive": gdrive,
        "s3": s3,
        "azure": azure,
        "oss": oss,
        "ssh": ssh,
        "ssh_gssapi": ssh_gssapi,
        "hdfs": hdfs,
        "tests": tests_requirements,
    },
    keywords="data science, data version control, machine learning",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    url="http://dvc.org",
    entry_points={"console_scripts": ["dvc = dvc.main:main"]},
    cmdclass={"build_py": build_py},
    zip_safe=False,
)
