import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="elasticsearch-aggregation-flatten",
    version="0.0.4",
    author="Gabriel de Biasi",
    author_email="biasi131@gmail.com",
    description="This python package helps to process an aggregation response from Elasticsearch and output it as easy-to-use format, such as json and csv.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gabrielbiasi/elasticsearch-aggregation-flatten",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
