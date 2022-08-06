import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DAMS-dicom-anonymizer",
    version="0.1.0",
    author="R. M. Sandu",
    author_email="raluca-sandu@rwth-aachen.de",
    description="Anonymize DICOM Files using PyDicom",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/raluca-san/DAMS-dicom-anonymizer",
    packages=setuptools.find_packages(),
    install_requires = [
        "numpy>=1.19",
        "openpyxl>=3.0.5",
        "pandas>=1.1",
        "xlrd>=1.2.0",
        "pydicom>=1.2.2",
        "untangle==1.2.1"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL :: 3 ",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)