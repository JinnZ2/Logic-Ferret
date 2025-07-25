# setup.py

from setuptools import setup, find_packages

setup(
    name="logic-ferret-gui",
    version="0.1.0",
    author="JinnZ2",
    description="A sarcastic bullshit detector GUI that flags fallacies in speech or writing.",
    packages=find_packages(),
    install_requires=[
        "tk",  # native, but keep it here as a reminder
    ],
    entry_points={
        "console_scripts": [
            "logic-ferret=gui.fallacy_gui:main"
        ]
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
