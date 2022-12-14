import os
import setuptools


here_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here_dir, "README.rst"), encoding="utf-8") as file:
    readme = file.read()

with open(os.path.join(here_dir, "requirements.txt"), encoding="utf-8") as file:
    requirements = file.read().splitlines()

setuptools.setup(
    name="pyncd",
    version="0.1.0",
    author="BoCong Deng",
    author_email="bocongdeng@gmail.com",
    description="A Python Library for Network Community Detection",
    long_description=readme,
    long_description_content_type="text/x-rst",
    license="BSD-2",
    url="https://github.com/DengBoCong/pyncd",
    keywords=["community detection", "deep community detection", "deep community detection",
              "deep learning", "network analysis", "graph mining"],
    packages=setuptools.find_packages(exclude=['test']),
    include_package_data=True,
    install_requires=requirements,
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: BSD License",
    ],
)