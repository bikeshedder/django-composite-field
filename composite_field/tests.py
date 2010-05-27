import unittest

from django.db import models

from . import CompositeField
from . import LocalizedCharField
from . import ComplexField


class CoordField(CompositeField):
    x = models.FloatField()
    y = models.FloatField()


class Place(models.Model):
    name = models.CharField(max_length=10)
    coord = CoordField()


class Direction(models.Model):
    source = CoordField()
    distance = models.FloatField()
    target = CoordField()


class CompositeFieldTestCase(unittest.TestCase):

    def test_repr(self):
        place = Place(coord_x=12.0, coord_y=42.0)
        self.assertEquals(repr(place.coord), 'CoordField(x=12.0, y=42.0)')

    def test_cmp(self):
        place1 = Place(coord_x=12.0, coord_y=42.0)
        place2 = Place(coord_x=42.0, coord_y=12.0)
        self.assertNotEquals(place1.coord, place2.coord)
        place2.coord.x = 12.0
        place2.coord.y = 42.0
        self.assertEquals(place1.coord, place2.coord)

    def test_assign(self):
        place1 = Place(coord_x=12.0, coord_y=42.0)
        place2 = Place()
        place2.coord = place1.coord
        self.assertEquals(place1.coord, place2.coord)
        place2 = Place(coord=place1.coord)
        self.assertEquals(place1.coord, place2.coord)

    def test_setattr(self):
        place = Place()
        place.coord.x = 12.0
        place.coord.y = 42.0
        self.assertEquals(place.coord_x, 12.0)
        self.assertEquals(place.coord_y, 42.0)
        self.assertEquals(place.coord.x, 12.0)
        self.assertEquals(place.coord.y, 42.0)

    def test_field_order(self):
        fields = Place._meta.fields
        get_field = Place._meta.get_field
        name = get_field('name')
        coord_x = get_field('coord_x')
        coord_y = get_field('coord_y')
        self.assertTrue(fields.index(name) < fields.index(coord_x))
        self.assertTrue(fields.index(coord_x) < fields.index(coord_y))

    def test_field_order2(self):
        fields = Direction._meta.fields
        get_field = Direction._meta.get_field
        source_x = get_field('source_x')
        source_y = get_field('source_y')
        distance = get_field('distance')
        target_x = get_field('target_x')
        target_y = get_field('target_y')
        self.assertTrue(fields.index(source_x) < fields.index(source_y))
        self.assertTrue(fields.index(source_y) < fields.index(distance))
        self.assertTrue(fields.index(distance) < fields.index(target_x))
        self.assertTrue(fields.index(target_x) < fields.index(target_y))


class LocalizedFoo(models.Model):
    id = models.AutoField(primary_key=True)
    name = LocalizedCharField(languages=('de', 'en'), max_length=50)


class LocalizedFieldTestCase(unittest.TestCase):

    def test_general(self):
        foo = LocalizedFoo()
        self.assertEquals(len(LocalizedFoo._meta.fields), 3)
        foo.name_de = 'Mr.'
        foo.name_en = 'Herr'
        self.assertEquals(foo.name.de, 'Mr.')
        self.assertEquals(foo.name.en, 'Herr')


class ComplexTuple(models.Model):
    x = ComplexField(blank=True, null=True)
    y = ComplexField(blank=False, null=False, verbose_name='Y')
    z = ComplexField(verbose_name='gamma')

class ComplexTupleWithDefaults(models.Model):
    x = ComplexField(blank=True, null=True, default=None)
    y = ComplexField(blank=False, null=False, default=42)
    z = ComplexField(default=42j)

class ComplexFieldTestCase(unittest.TestCase):

    def test_attributes(self):
        t = ComplexTuple()
        get_field = t._meta.get_field
        self.assertEquals(get_field('x_real').blank, True)
        self.assertEquals(get_field('x_real').null, True)
        self.assertEquals(get_field('x_imag').blank, True)
        self.assertEquals(get_field('x_imag').null, True)
        self.assertEquals(get_field('y_real').blank, False)
        self.assertEquals(get_field('y_real').null, False)
        self.assertEquals(get_field('y_imag').blank, False)
        self.assertEquals(get_field('y_imag').null, False)
        self.assertEquals(get_field('z_real').blank, False)
        self.assertEquals(get_field('z_real').null, False)
        self.assertEquals(get_field('z_imag').blank, False)
        self.assertEquals(get_field('z_imag').null, False)

    def test_null(self):
        t = ComplexTuple()
        self.assertEquals(t.x, None)
        self.assertEquals(t.y, None)
        self.assertEquals(t.y, None)
        t.x = None
        t.y = None
        t.z = None
        self.assertEquals(t.x, None)
        self.assertEquals(t.y, None)
        self.assertEquals(t.y, None)

    def test_assignment(self):
        t = ComplexTuple(x=42, y=42j, z=42+42j)
        self.assertEquals(t.x, 42)
        self.assertEquals(t.y, 42j)
        self.assertEquals(t.z, 42+42j)
        t.x = complex(21, 0)
        self.assertEquals(t.x, 21)
        t.y = complex(0, 21)
        self.assertEquals(t.y, 21j)
        t.z = complex(21, 21)
        self.assertEquals(t.z, 21+21j)

    def test_calculation(self):
        t = ComplexTuple(x=1, y=1j)
        t.z = t.x * t.y
        self.assertEquals(t.z, 1j)
        t.y *= t.y
        self.assertEquals(t.y, -1)
        t.z = t.x * t.y
        self.assertEquals(t.x, 1)
        self.assertEquals(t.y, -1)
        self.assertEquals(t.z, -1)

    def test_defaults(self):
        t = ComplexTupleWithDefaults()
        self.assertEquals(t.x, None)
        self.assertEquals(t.y, 42)
        self.assertEquals(t.z, 42j)

    def test_verbose_name(self):
        t = ComplexTuple()
        get_field = t._meta.get_field
        self.assertEquals(get_field('x_real').verbose_name, 'Re(x)')
        self.assertEquals(get_field('x_imag').verbose_name, 'Im(x)')
        self.assertEquals(get_field('y_real').verbose_name, 'Re(Y)')
        self.assertEquals(get_field('y_imag').verbose_name, 'Im(Y)')
        self.assertEquals(get_field('z_real').verbose_name, 'Re(gamma)')
        self.assertEquals(get_field('z_imag').verbose_name, 'Im(gamma)')
