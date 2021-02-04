import setuptools, os

with open(os.path.join(os.path.dirname(__file__), "bwpy", "__init__.py"), "r") as f:
    for line in f:
        if "__version__ = " in line:
            exec(line.strip())
            break

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bwpy",
    version=__version__,
    author="Robin De Schepper",
    author_email="robingilbert.deschepper@unipv.it",
    description="Library to interact with BrainWave's BRW and BXR files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Helveg/bwpy",
    license="GPLv3",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=["h5py<3.0.0", "numpy"],
    extras_require={"dev": ["sphinx", "furo"]},
)
