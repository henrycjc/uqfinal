import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(os.path.dirname(here), 'README.md')).read()

install_deps = [
    'boto3',
    'Flask',
    'requests',
    'lxml',
]

setup(
    name='uqfinalapi',
    version='0.1',
    description='API to power UQ Final',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Flask",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Mitchell Grice',
    author_email='mitch@gricey.net',
    url='https://uqfinal.com',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_deps,
)
