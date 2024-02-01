# Version 2.0.0, unreleased

* Remove support for outdated Python and Django versions.
* Add support for Django 5.0

# Version 1.1.0, 2020-01-06

* Fix Django admin by adding a `verbose_name` to `CompositeField`
* Make `CompositeFieldSerializer` the default serializer for
  `CompositeField` when using `composite_field.drf_support`

# Version 1.0.0, 2020-01-06

* Remove Python 2 support
* Add Django 3.0 support
* Add Documentation

# Version 0.9.1, 2019-04-09

* Add Python 3.6 and 3,7 support
* Fix Django 2.2 support

# Version 0.9.0, 2017-12-22

* Fix Django 2.0 private field
* Add Python 2.6 support
* Fix `test_settings` for Django 2.0

# Version 0.8.1, 2017-10-14

* Make it simpler to provide a custom proxy
* Fix Python 2.7 compatibility for `bool(LocalizedField)`
* Add test for custom Proxy with `__bool__()`

# Version 0.8.0, 2017-03-02

* Drop support for Python 3.2 and 3.3
* Add tests for modelform with include and exclude meta parameter
* Fix Python 3.x compatibility
* Improve test cases
* Add default kwarg to `CompositeField`
* Drop support for Django < 1.8
* Add docker configuration for running the tests
* Add bitbucket-pipeline to run tests on push

# Version 0.7.6, 2016-07-01

* Add `help_text`, `choices` and `max_length` proxy properties
* Add support for assigning `ugettext_lazy` to localized fields

# Version 0.7.5, 2016-06-16

* Fix Python 3 support
* Add test case for raw SQL query
* Fix ordering query sets by a `LocalizedField`
* Drop support for Python 2.6
* Fix `__eq__` and `__lt__` method of `CompositeField`

# Version 0.7.4, 2016-02-17

* Fix Django 1.9 support
* Add support for dicts as composite field values
* Add `django-rest-framework serializer` support

# Version 0.7.3, 2016-01-21

* Fix Django 1.9 support
* Fix `LocalizedField` for Django 1.8+ when no translation is active
* Add `remote_field=None` to `CompositeField`

# Version 0.7.2, 2015-11-27

* Add empty `flatchoices` attribute to `CompositeField`

# Version 0.7.1, 2015-10-28

* Add `primary_key=False` to `CompositeField`

# Version 0.7.0, 2015-10-26

* Fix `Model.full_clean()` error when using a `CompositeField`
* Add `get_col` method to `LocalizedField` making it possible
  to use it in a `QuerySet`.

# Version 0.6.0, 2015-08-21

* Fix `ModelForm` for models with a `CompositeField`
* Implement `current(_with_default)` and `all` property of
  `LocalizedField`

# Version 0.5, 2015-07-29

* Fix composite proxy `__eq__` method when comparing against
  non composite values
* Fix translation fallback
* Fix `verbose_name` as positional argument in `LocalizedField`

# Version 0.4, 2015-07-29

* Fix Python 3.2 compatibility
* Composite field as virtual field in model

# Version 0.3, 2015-07-23

* Remove deprecation warning

# Version 0.2, 2015-07-23

* Add support for Django 1.4-1.8 and Python 2.x and 3.x
* Tests can be run via tox

# Version 0.1, 2010-05-27

* First release
