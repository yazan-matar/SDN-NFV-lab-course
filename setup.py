from setuptools import find_packages, setup


setup(
    name="policonf",
    description="PoliMi SDN Python project",
    version="0.0.0",

    author="ADVA Optical Networking :: Stefan Zimmermann",
    author_email="szimmermann@adva.com",

    install_requires=open("requirements.txt").read(),
    packages=find_packages(include=["polimi", "polimi.*"]),

    entry_points={'console_scripts': ["policonf=policonf.__main__:run"]},
)
