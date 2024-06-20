from setuptools import setup

setup(
    name="hjreborn",
    version="0.1.0",
    packages=[
        "hjreborn",
        "hjreborn.config",
        "hjreborn.core",
        "hjreborn.frontend",
        "hjreborn.i18n"
    ],
    install_requires=["rich", "parse", "click", "jsonschema", "simplejson", "psutil"],
    entry_points={"console_scripts": ["hjreborn = hjreborn.main:group"]},
    author="xiezheyuan",
    author_email="xiezheyuan09@163.com",
    description="A simple CLI offline judge system",
    long_description="A simple CLI offline judge system",
    long_description_content_type="text/plain",
    url="https://github.com/hellojudger/HelloJudgerReborn",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    license="AGPL-3.0",
    python_requires=">=3.8",
)
