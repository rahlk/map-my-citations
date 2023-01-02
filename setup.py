from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='citemap',
    version='0.0.0',
    url="https://github.com/rahlk/map-my-citations",
    author="Rahul Krishna <imralk+oss@gmail.com>",
    description="A small python app to generate and plot your Google Scholar citations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
        "requests",
        "parsel",
        "lxml",
        "beautifulsoup4",
        "google-search-results",
        "openpyxl~=3.0.10",
        "rich==12.6.0",
        "plotly~=5.11.0",
        "ip2geotools~=0.1.6",
        "typer~=0.7.0",
        "pandas~=1.5.1",
        "typing~=3.7.4.3",
        "setuptools~=65.5.1",
        "rich-click"
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    extras_require={
        "dev": [
            "nose==1.3.7"
            , "pinocchio==0.4.3"
            , "coverage==6.3.2"
            , "pylint==2.13"
            , "py2neo==2021.2.3"
            , "flake8==4.0.1"
            , "black==22.3.0"
            , "tox==3.24.5"
            , "ipdb"

        ],
    },
    entry_points={
        'console_scripts': [
            'citemap = citemap.cli:cli'
        ],
    },
)
