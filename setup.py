from setuptools import setup, find_packages

setup(
    name="gdpr_obfuscator",
    version="0.1.0",
    author="Your Name",
    description="A tool for obfuscating sensitive data in files stored on S3.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pandas",
        "boto3",
        "fastparquet",
    ],
    python_requires=">=3.9",
)