import setuptools

from pycot.version import __version__

with open("README.md", "r") as ld:
    long_description = ld.read()

setuptools.setup(
    name="pycot-reports",
    version=__version__,
    packages=["pycot"],
    include_package_data=True,
    install_requires=["pandas", "requests", "python-dotenv"],
    url="https://github.com/philsv/pycot",
    license="MIT",
    author="philsv",
    author_email="frphsv@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords=["commitment of traders", "cot data", "cftc", "python"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "License :: OSI Approved :: MIT License",
    ],
)
