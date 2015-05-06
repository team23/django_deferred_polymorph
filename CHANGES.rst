Changelog
=========

0.2.1
-----

* Dropping support for Django 1.5.x and lower as we had to adept to Django's
  naming scheme for ``get_queryset`` instead of ``get_query_set`` in managers.
* Fix for Django 1.8 which uses unicode for model names in the Meta._meta
  object. That broke the dynamic class creation with ``type()``.

0.2.0
-----

* Django 1.8 support.
