ABOUT
=====

django_deferred_polymorph is an implementation of polymorphic models for Django. Like other solutions you can just fetch the base instance from your database and get the right subclass back. This means you always can rely on having all data/methods your child class would provide.

Unlike other solutions additional data is loaded by using a slightly modified version of Django's own deferered mechanisms. This way getting the base classes issues only one SQL query, returning the subclasses with all additional data as defered field. If you attempt to access one of the deferred fields all deferred fields are loaded (unlike for Django's default deferred fields).

django_deferred_polymorph includes two abstract base models:

 * DeferredPolymorphBaseModel as the base for every deferred model
 * SubDeferredPolymorphBaseModel which extends DeferredPolymorphBaseModel to force userd to use a subclass

Installation
============

First::

    pip install django_deferred_polymorph

Then add ``'django_deferred_polymorph'`` to your ``INSTALLED_APPS`` settings.

Running tests
=============

First create a `virtualenv`_, then install package inside the virtualenv and
add the test dependencies with::

    python setup.py develop
    pip install -r requirements.txt

Now you can run the test suite against the currently installed version of
Django with::

    python runtests.py

However we support multiple versions of Django and Python. To test all
relevant combinations at once you can use the following command::

    tox

.. _virtualenv: https://virtualenv.pypa.io/en/latest/
