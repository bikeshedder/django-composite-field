.. _example:

Example
=======

Model definition
----------------

.. code-block:: python

    class CoordField(CompositeField):
        x = models.FloatField()
        y = models.FloatField()

    class Place(models.Model):
        name = models.CharField(max_length=10)
        coord = CoordField()

Usage
-----

.. code-block:: python

    p = Place(name='Foo', coord_x=42, coord_y=0)
    q = Place(name='Foo', coord=p.coord)
    q.coord.y = 42

How does it work?
-----------------

The content of composite fields are stored inside the model, so they do
not have to fiddle with any internals of the Django models. In the example
above ``p.coord`` returns a proxy object that maps the fields ``x`` and ``y``
to the model fields ``coord_x`` and ``coord_y``.

This is roughly equivalent to the following code:

.. code-block:: python

    class CoordProxy:

        def __init__(self, model):
            self.model = model

        def __get__(self, instance):
            return CoordProxy(instance)

        def __set__(self, instance, value):
            instance.coord_x = value.coord_x
            instance.coord_y = value.coord_y

        @property
        def x(self):
            return self.model.coord_x

        @x.setter
        def x(self, value):
            self.model.coord_x = value

        @property
        def y(self):
            return self.model.coord_y

        @y.setter
        def y(self, value):
            self.model.coord_y = value

    class Place(models.Model):
        name = models.CharField(max_length=10)
        coord_x = models.FloatField()
        coord_y = models.FloatField()
        coord = CoordProxy()

Advanced usage
--------------

The proxy object also makes it possible to assign more than one property at
once:

.. code-block:: python

    place1.coord = place2.coord

It also supports using dictionaries for the ``__init__`` method or
assigning them as a value:

.. code-block:: python

    place1 = Place(coord={'x': 42, 'y': 0})
    place1.coord = {'x': 43, 'y': 1}

It is even possible to replace the ``Proxy`` object entirely and
return a custom type. A good example for this is the included
``ComplexField`` which stores a ``complex`` number in two
integer fields.
