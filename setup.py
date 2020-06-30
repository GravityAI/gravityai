import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as rqf:
    reqs = rqf.readlines()

setuptools.setup(
    name="gravityai",
    version="0.0.8",
    author="Jon Huss",
    author_email="jon@gravity-ai.com",
    description="The gravity-ai.com helper package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GravityAI/gravityai",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=reqs,
)
