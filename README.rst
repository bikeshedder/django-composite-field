|Build Status| |PyPI Version| |PyPI License| |Python Versions| |Django Versions| |Read the Docs| |Code Shelter|

CompositeField for Django Models
================================

This is an implementation of a CompositeField for Django. Composite fields
can be used to group fields together and reuse their definitions.

Example
-------

.. code-block:: python

    class CoordField(CompositeField):
        x = models.FloatField()
        y = models.FloatField()

    class Place(models.Model):
        name = models.CharField(max_length=10)
        coord = CoordField()

    p = Place(name='Foo', coord_x=42, coord_y=0)
    q = Place(name='Foo', coord=p.coord)
    q.coord.y = 42


How does it work?
-----------------

The content of composite fields are stored inside the model, so they do
not have to fiddle with any internals of the Django models. In the example
above ``p.coord`` returns a proxy object that maps the fields ``x`` and ``y``
to the model fields ``coord_x`` and ``coord_y``. The proxy object also
makes it possible to assign more than one property at once.

Documentation can be found at `RTFD <http://django-composite-field.readthedocs.io/>`_.

.. |Build Status| image:: https://img.shields.io/github/workflow/status/bikeshedder/django-composite-field/Python%20package
   :target: https://github.com/bikeshedder/django-composite-field/actions?query=workflow%3A%22Python+package%22
.. |PyPI Version| image:: https://img.shields.io/pypi/v/django-composite-field.svg
   :target: https://pypi.python.org/pypi/django-composite-field/
.. |PyPI License| image:: https://img.shields.io/pypi/l/django-composite-field.svg
   :target: https://pypi.python.org/pypi/django-composite-field/
.. |Python Versions| image:: https://img.shields.io/pypi/pyversions/django-composite-field.svg
   :target: https://pypi.python.org/pypi/django-composite-field/
.. |Django Versions| image:: https://img.shields.io/pypi/djversions/django-composite-field.svg
   :target: https://pypi.org/project/django-composite-field/
.. |Read the Docs| image:: https://img.shields.io/readthedocs/django-composite-field.svg
   :target: http://django-composite-field.readthedocs.io/
.. |Code Shelter| image:: https://www.codeshelter.co/static/badges/badge-flat.svg
   :target: https://www.codeshelter.co/
