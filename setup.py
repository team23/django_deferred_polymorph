from setuptools import setup, find_packages

setup(
    name = "django_deferred_polymorph",
    version = "0.2.0",
    description = 'Polymorphic models based on django deferred models',
    author = 'David Danier',
    author_email = 'david.danier@team23.de',
    url = 'https://github.com/ddanier/django_deferred_polymorph',
    long_description=open('README.rst', 'r').read(),
    packages = [
        'django_deferred_polymorph',
    ],
    install_requires = [
        'Django >=1.4',
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

