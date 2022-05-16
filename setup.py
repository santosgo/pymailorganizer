import pathlib
from setuptools import setup

# The directory containing this file
HOME_DIR = pathlib.Path(__file__).parent

# The text of the README file
README = (HOME_DIR / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="pymailorganizer",
    version="0.6.2",
    description="Python command line mail organizer",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/santosgo/pymailorganizer",
    author="Gonçalo Brandão Coelho dos Santos",
    author_email="goncalo.a.santos@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["pymailorganizer"],
    include_package_data=True,
    install_requires=[
        "halo", 
        "matplotlib", 
        "ntlm-auth",
        "numpy",
        "pandas",
        "pytest",
        "requests",
        "scipy",
        "seaborn",
        "tabulate",
        "tqdm",
        "urllib3",
    ],
    entry_points={
        "console_scripts": [
            "pymailorganizer = pymailorganizer.main:shell",
        ]
    },
)
