from setuptools import setup

setup(
    name="pc_jamf",
    version="0.3.2",
    description="Wrapper library to connect to a JAMF Pro Server using the beta and classic API",
    url="https://github.com/pinecrest/pc_jamf",
    author="Sean Tibor",
    author_email="sean.tibor@pinecrest.edu",
    license="GPLv3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators"
    ],
    packages=["pc_jamf"],
    install_requires=["requests", "python-decouple"],
    zip_safe=False,
)
