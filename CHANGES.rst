Changelog
=========

0.2.1
-----

* Fix for Django 1.8 which uses unicode for model names in the Meta._meta
  object. That broke the dynamic class creation with ``type()``.

0.2.0
-----

* Django 1.8 support.
