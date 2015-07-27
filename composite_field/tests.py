import unittest

import django
from django.db import models
from django.utils.encoding import force_text

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
        self.assertEqual(repr(place.coord), 'CoordField(x=12.0, y=42.0)')

    def test_cmp(self):
        place1 = Place(coord_x=12.0, coord_y=42.0)
        place2 = Place(coord_x=42.0, coord_y=12.0)
        self.assertNotEqual(place1.coord, place2.coord)
        place2.coord.x = 12.0
        place2.coord.y = 42.0
        self.assertEqual(place1.coord, place2.coord)

    def test_assign(self):
        place1 = Place(coord_x=12.0, coord_y=42.0)
        place2 = Place()
        place2.coord = place1.coord
        self.assertEqual(place1.coord, place2.coord)
        place2 = Place(coord=place1.coord)
        self.assertEqual(place1.coord, place2.coord)

    def test_setattr(self):
        place = Place()
        place.coord.x = 12.0
        place.coord.y = 42.0
        self.assertEqual(place.coord_x, 12.0)
        self.assertEqual(place.coord_y, 42.0)
        self.assertEqual(place.coord.x, 12.0)
        self.assertEqual(place.coord.y, 42.0)

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
        # XXX Enable this test once the virtual field is added.
        # The behavior changed from Django >= 1.8 and virtual
        # fields are now part of the fields list.
        #if django.VERSION >= (1, 8):
        #    self.assertEqual(len(LocalizedFoo._meta.fields), 4)
        #else:
        #    self.assertEqual(len(LocalizedFoo._meta.fields), 3)
        self.assertEqual(len(LocalizedFoo._meta.fields), 3)
        foo.name_de = 'Mr.'
        foo.name_en = 'Herr'
        self.assertEqual(foo.name.de, 'Mr.')
        self.assertEqual(foo.name.en, 'Herr')

    def test_verbose_name(self):
        foo = LocalizedFoo()
        get_field = foo._meta.get_field
        self.assertEqual(force_text(get_field('name_de').verbose_name), 'name (de)')
        self.assertEqual(force_text(get_field('name_en').verbose_name), 'name (en)')

    # XXX Enable this test once the virtual field is added.
    #@unittest.skipIf(django.VERSION <= (1, 8), 'get_fields returns virtual fields since Django 1.8')
    #def test_verbose_name_1_8(self):
    #    foo = LocalizedFoo()
    #    get_field = foo._meta.get_field
    #    self.assertEqual(force_text(get_field('name').verbose_name), 'name')


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
        self.assertEqual(get_field('x_real').blank, True)
        self.assertEqual(get_field('x_real').null, True)
        self.assertEqual(get_field('x_imag').blank, True)
        self.assertEqual(get_field('x_imag').null, True)
        self.assertEqual(get_field('y_real').blank, False)
        self.assertEqual(get_field('y_real').null, False)
        self.assertEqual(get_field('y_imag').blank, False)
        self.assertEqual(get_field('y_imag').null, False)
        self.assertEqual(get_field('z_real').blank, False)
        self.assertEqual(get_field('z_real').null, False)
        self.assertEqual(get_field('z_imag').blank, False)
        self.assertEqual(get_field('z_imag').null, False)

    def test_null(self):
        t = ComplexTuple()
        self.assertEqual(t.x, None)
        self.assertEqual(t.y, None)
        self.assertEqual(t.y, None)
        t.x = None
        t.y = None
        t.z = None
        self.assertEqual(t.x, None)
        self.assertEqual(t.y, None)
        self.assertEqual(t.y, None)

    def test_assignment(self):
        t = ComplexTuple(x=42, y=42j, z=42+42j)
        self.assertEqual(t.x, 42)
        self.assertEqual(t.y, 42j)
        self.assertEqual(t.z, 42+42j)
        t.x = complex(21, 0)
        self.assertEqual(t.x, 21)
        t.y = complex(0, 21)
        self.assertEqual(t.y, 21j)
        t.z = complex(21, 21)
        self.assertEqual(t.z, 21+21j)

    def test_calculation(self):
        t = ComplexTuple(x=1, y=1j)
        t.z = t.x * t.y
        self.assertEqual(t.z, 1j)
        t.y *= t.y
        self.assertEqual(t.y, -1)
        t.z = t.x * t.y
        self.assertEqual(t.x, 1)
        self.assertEqual(t.y, -1)
        self.assertEqual(t.z, -1)

    def test_defaults(self):
        t = ComplexTupleWithDefaults()
        self.assertEqual(t.x, None)
        self.assertEqual(t.y, 42)
        self.assertEqual(t.z, 42j)

    def test_verbose_name(self):
        t = ComplexTuple()
        get_field = t._meta.get_field
        self.assertEqual(get_field('x_real').verbose_name, 'Re(x)')
        self.assertEqual(get_field('x_imag').verbose_name, 'Im(x)')
        self.assertEqual(get_field('y_real').verbose_name, 'Re(Y)')
        self.assertEqual(get_field('y_imag').verbose_name, 'Im(Y)')
        self.assertEqual(get_field('z_real').verbose_name, 'Re(gamma)')
        self.assertEqual(get_field('z_imag').verbose_name, 'Im(gamma)')


class TranslatedAbstractBase(models.Model):
    name = LocalizedCharField(languages=('de', 'en'), max_length=50)

    class Meta:
        abstract = True

class TranslatedModelA(TranslatedAbstractBase):
    pass

class TranslatedModelB(TranslatedAbstractBase):
    pass

class TranslatedNonAbstractBase(models.Model):
    name = LocalizedCharField(languages=('de', 'en'), max_length=50)

    class Meta:
        abstract = False

class TranslatedModelC(TranslatedNonAbstractBase):
    pass

class TranslatedModelD(TranslatedNonAbstractBase):
    pass

class InheritanceTestCase(unittest.TestCase):

    def test_abstract_inheritance(self):
        a = TranslatedModelA(name_de='Max Mustermann', name_en='John Doe')
        b = TranslatedModelB(name_en='Petra Musterfrau', name='Jane Doe')
        get_a_field = a._meta.get_field
        get_b_field = b._meta.get_field
        #if django.VERSION >= (1, 8):
        #    self.assertIs(get_a_field('name').model, TranslatedModelA)
        self.assertIs(get_a_field('name_de').model, TranslatedModelA)
        self.assertIs(get_a_field('name_en').model, TranslatedModelA)
        #if django.VERSION >= (1, 8):
        #    self.assertIs(get_b_field('name').model, TranslatedModelB)
        self.assertIs(get_b_field('name_de').model, TranslatedModelB)
        self.assertIs(get_b_field('name_en').model, TranslatedModelB)

    def test_non_abstract_inheritance(self):
        c = TranslatedModelC(name_de='Max Mustermann', name_en='John Doe')
        d = TranslatedModelD(name_en='Petra Musterfrau', name='Jane Doe')
        get_c_field = c._meta.get_field
        get_d_field = d._meta.get_field
        #if django.VERSION >= (1, 8):
        #    self.assertIs(get_c_field('name').model, TranslatedNonAbstractBase)
        self.assertIs(get_c_field('name_de').model, TranslatedNonAbstractBase)
        self.assertIs(get_c_field('name_en').model, TranslatedNonAbstractBase)
        #if django.VERSION >= (1, 8):
        #    self.assertIs(get_d_field('name').model, TranslatedNonAbstractBase)
        self.assertIs(get_d_field('name_de').model, TranslatedNonAbstractBase)
        self.assertIs(get_d_field('name_en').model, TranslatedNonAbstractBase)


class RunChecksTestCase(unittest.TestCase):

    @unittest.skipIf(django.VERSION <= (1, 7), 'checks were introduced in Django 1.7+')
    def test_checks(self):
        django.setup()
        from django.core import checks
        all_issues = checks.run_checks()
        errors = [str(e) for e in all_issues if e.level >= checks.ERROR]
        if errors:
            self.fail('checks failed:\n' + '\n'.join(errors))
