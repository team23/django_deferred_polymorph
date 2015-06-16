Changelog
=========

0.3.2
-----

* Fix for Django 1.8 that did not set ``_base_manager`` correctly for
  subclasses of ``DeferredPolymorphBaseModel``. That broke the
  ``Model.delete()`` method in some cases.

0.3.1
-----

* Adding MANIFEST.in file to define which files get included in the source
  distribution. CHANGES.rst was missing from that and caused an error on
  install.

0.3.0
-----

* Dropping support for Django 1.5.x and lower as we had to adept to Django's
  naming scheme for ``get_queryset`` instead of ``get_query_set`` in managers.
* Fix for Django 1.8 which uses unicode for model names in the Meta._meta
  object. That broke the dynamic class creation with ``type()``.

0.2.0
-----

* Django 1.8 support.
