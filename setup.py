import setuptools

setuptools.setup(
    name="doiowa",
    version="2020.7.30",
    author="Wesley Teal",
    author_email="wteal@iastate.edu",
    description="A library to manage DOIs at the Iowa State University Library.",
    entry_points={"console_scripts": ["doiowa=doiowa.__main__:main",],},
    install_requires=["crossrefapi", "lxml", "requests"],
    url="https://github.com/isu-meta/doiowa",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
