import codecs
from os import path
from setuptools import setup


def read(*parts):
    return codecs.open(path.join(path.dirname(__file__), *parts),
                       encoding='utf-8').read()


setup(
    name = "django_deferred_polymorph",
    version = "0.3.2",
    description = 'Polymorphic models based on django deferred models',
    author = 'David Danier',
    author_email = 'david.danier@team23.de',
    url = 'https://github.com/ddanier/django_deferred_polymorph',
    long_description = '\n\n'.join((
        read('README.rst'),
        read('CHANGES.rst'))),
    packages = [
        'django_deferred_polymorph',
    ],
    install_requires = [
        'Django >= 1.6',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
