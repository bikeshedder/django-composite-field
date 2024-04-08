import math
import unittest

import django
import django.test
from django.test import TestCase
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from django.utils import translation

from composite_field_test.models import Place
from composite_field_test.models import PlaceWithDefaultCoord
from composite_field_test.models import Direction
from composite_field_test.models import LocalizedFoo
from composite_field_test.models import ComplexTuple
from composite_field_test.models import ComplexTupleWithDefaults
from composite_field_test.models import TranslatedModelA
from composite_field_test.models import TranslatedModelB
from composite_field_test.models import TranslatedNonAbstractBase
from composite_field_test.models import TranslatedModelC
from composite_field_test.models import TranslatedModelD


class CompositeFieldTestCase(TestCase):

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

    def test_modelform(self):
        from django import forms

        class DirectionForm(forms.ModelForm):
            class Meta:
                model = Direction
                exclude = ()
        form = DirectionForm()
        form = DirectionForm({})
        form.is_valid()

    def test_modelform_with_exclude(self):
        from django import forms

        class LocalizedFooForm(forms.ModelForm):
            class Meta:
                model = LocalizedFoo
                exclude = ()
        form = LocalizedFooForm()
        form = LocalizedFooForm({})
        self.assertFalse(form.is_valid())
        form = LocalizedFooForm({'name_de': 'Banane', 'name_en': 'Banana'})
        self.assertTrue(form.is_valid())
        foo = form.save(commit=False)
        self.assertEqual(foo.name.de, 'Banane')
        self.assertEqual(foo.name.en, 'Banana')

    def test_modelform_with_fields(self):
        from django import forms

        class LocalizedFooForm(forms.ModelForm):
            class Meta:
                model = LocalizedFoo
                fields = ('name_de', 'name_en')
        form = LocalizedFooForm()
        form = LocalizedFooForm({})
        self.assertFalse(form.is_valid())
        form = LocalizedFooForm({'name_de': 'Banane', 'name_en': 'Banana'})
        self.assertTrue(form.is_valid())
        foo = form.save(commit=False)
        self.assertEqual(foo.name.de, 'Banane')
        self.assertEqual(foo.name.en, 'Banana')

    def test_full_clean(self):
        place = Place(name='Answer', coord_x=12.0, coord_y=42.0)
        place.full_clean()

    def test_default_kwarg(self):
        place = PlaceWithDefaultCoord()
        self.assertEqual(place.coord.x, 1.0)
        self.assertEqual(place.coord.y, 2.0)

    def test_assign_dict(self):
        place = Place(name='Answer', coord_x=12.0, coord_y=42.0)
        place.coord = {'x': 1.0, 'y': 2.0}
        self.assertEqual(place.coord.x, 1.0)
        self.assertEqual(place.coord.y, 2.0)

    def test_assign_incomplete_dict(self):
        place = Place(name='Answer', coord_x=12.0, coord_y=42.0)
        with self.assertRaises(KeyError):
            place.coord = {'x': 0.0}

    def test_bool(self):
        place = Place(name='Answer')
        self.assertFalse(place.coord)
        place.coord = {'x': 0.0, 'y': None}
        self.assertFalse(place.coord)
        place.coord = {'x': None, 'y': 0.0}
        self.assertFalse(place.coord)
        place.coord = {'x': 0.0, 'y': 0.0}
        self.assertTrue(place.coord)

    def test_parent_verbose_name(self):
        get_field = Place._meta.get_field
        self.assertEqual(str(get_field("coord_y").verbose_name), "coord_verbose yyy")


class LocalizedFieldTestCase(TestCase):
    def test_general(self):
        foo = LocalizedFoo()
        self.assertEqual(len(LocalizedFoo._meta.fields), 4)

        foo.name_de = 'Mr.'
        foo.name_en = 'Herr'
        self.assertEqual(foo.name.de, 'Mr.')
        self.assertEqual(foo.name.en, 'Herr')

    def test_verbose_name(self):
        foo = LocalizedFoo()
        get_field = foo._meta.get_field
        self.assertEqual(str(get_field('name').verbose_name), 'name')
        self.assertEqual(str(get_field('name_de').verbose_name), 'name (de)')
        self.assertEqual(str(get_field('name_en').verbose_name), 'name (en)')

    def test_get_current(self):
        foo = LocalizedFoo(name_de='Bier', name_en='Beer')
        with translation.override('de'):
            self.assertEqual(foo.name.current, 'Bier')
        with translation.override('en'):
            self.assertEqual(foo.name.current, 'Beer')

    def test_set_current(self):
        foo = LocalizedFoo()
        with translation.override('de'):
            foo.name.current = 'Bier'
        with translation.override('en'):
            foo.name.current = 'Beer'
        self.assertEqual(foo.name_de, 'Bier')
        self.assertEqual(foo.name_en, 'Beer')

    def test_set_all(self):
        foo = LocalizedFoo()
        foo.name.all = 'Felix'
        self.assertEqual(foo.name_de, 'Felix')
        self.assertEqual(foo.name_en, 'Felix')

    def test_filter(self):
        foo1 = LocalizedFoo(name_de='eins', name_en='one')
        foo2 = LocalizedFoo(name_de='zwei', name_en='two')
        try:
            foo1.save()
            foo2.save()
            with translation.override('de'):
                self.assertEqual(LocalizedFoo.objects.get(name='eins'), foo1)
                self.assertRaises(LocalizedFoo.DoesNotExist, LocalizedFoo.objects.get, name='one')
            with translation.override('en'):
                self.assertEqual(LocalizedFoo.objects.get(name='one'), foo1)
                self.assertRaises(LocalizedFoo.DoesNotExist, LocalizedFoo.objects.get, name='eins')
            with translation.override('de'):
                self.assertEqual(LocalizedFoo.objects.get(name='zwei'), foo2)
                self.assertRaises(LocalizedFoo.DoesNotExist, LocalizedFoo.objects.get, name='two')
            with translation.override('en'):
                self.assertEqual(LocalizedFoo.objects.get(name='two'), foo2)
                self.assertRaises(LocalizedFoo.DoesNotExist, LocalizedFoo.objects.get, name='zwei')
        finally:
            foo1.delete()
            foo2.delete()

    def test_order_by(self):
        foo1 = LocalizedFoo(name_de='Erdnuss', name_en='peanut')
        foo2 = LocalizedFoo(name_de='Schinken', name_en='ham')
        try:
            foo1.save()
            foo2.save()
            with translation.override('de'):
                self.assertEqual(
                        list(LocalizedFoo.objects.all().order_by('name')),
                        [foo1, foo2])
            with translation.override('en'):
                self.assertEqual(
                        list(LocalizedFoo.objects.all().order_by('name')),
                        [foo2, foo1])
        finally:
            foo1.delete()
            foo2.delete()

    def test_raw_sql(self):
        foo = LocalizedFoo(name_de='Antwort', name_en='answer')
        try:
            foo.save()
            foo2 = LocalizedFoo.objects.raw('SELECT * FROM composite_field_test_localizedfoo')[0]
            with translation.override('de'):
                self.assertEqual(str(foo2.name), 'Antwort')
            with translation.override('en'):
                self.assertEqual(str(foo2.name), 'answer')
        finally:
            foo.delete()

    def test_bool(self):
        foo = LocalizedFoo()
        self.assertFalse(foo.name)
        foo.name_de = 'test'
        self.assertTrue(foo.name)


class ComplexFieldTestCase(TestCase):

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


class InheritanceTestCase(TestCase):

    def test_abstract_inheritance(self):
        a = TranslatedModelA(name_de='Max Mustermann', name_en='John Doe')
        b = TranslatedModelB(name_en='Petra Musterfrau', name_de='Jane Doe')
        get_a_field = a._meta.get_field
        get_b_field = b._meta.get_field
        self.assertIs(get_a_field('name').model, TranslatedModelA)
        self.assertIs(get_a_field('name_de').model, TranslatedModelA)
        self.assertIs(get_a_field('name_en').model, TranslatedModelA)
        self.assertIs(get_b_field('name').model, TranslatedModelB)
        self.assertIs(get_b_field('name_de').model, TranslatedModelB)
        self.assertIs(get_b_field('name_en').model, TranslatedModelB)

    def test_non_abstract_inheritance(self):
        c = TranslatedModelC(name_de='Max Mustermann', name_en='John Doe')
        d = TranslatedModelD(name_en='Petra Musterfrau', name_de='Jane Doe')
        get_c_field = c._meta.get_field
        get_d_field = d._meta.get_field
        self.assertIs(get_c_field('name').model, TranslatedNonAbstractBase)
        self.assertIs(get_c_field('name_de').model, TranslatedNonAbstractBase)
        self.assertIs(get_c_field('name_en').model, TranslatedNonAbstractBase)
        self.assertIs(get_d_field('name').model, TranslatedNonAbstractBase)
        self.assertIs(get_d_field('name_de').model, TranslatedNonAbstractBase)
        self.assertIs(get_d_field('name_en').model, TranslatedNonAbstractBase)


class RunChecksTestCase(TestCase):

    def test_checks(self):
        django.setup()
        from django.core import checks
        all_issues = checks.run_checks()
        errors = [str(e) for e in all_issues if e.level >= checks.ERROR]
        if errors:
            self.fail('checks failed:\n' + '\n'.join(errors))


class AdminTestCase(django.test.TestCase):

    def setUp(self):
        from django.contrib.auth.models import User
        self.factory = django.test.RequestFactory()
        self.user = self.user = User.objects.create_superuser(
                username='john.doe',
                email='john.doe@example.com',
                password='xxx12345')

    def test_login(self):
        self.assertTrue(self.client.login(username='john.doe', password='xxx12345'))

    def test_admin_index(self):
        self.client.login(username='john.doe', password='xxx12345')
        self.client.get('/admin/')

    def test_translated_model_a(self):
        self.client.login(username='john.doe', password='xxx12345')
        response = self.client.get('/admin/composite_field_test/translatedmodela/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/admin/composite_field_test/translatedmodela/add/')
        self.assertEqual(response.status_code, 200)
        obj = TranslatedModelA.objects.create(name_de='Foo', name_en='Foo')
        response = self.client.get('/admin/composite_field_test/translatedmodela/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/admin/composite_field_test/translatedmodela/%s/change/' % obj.pk)
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/admin/composite_field_test/translatedmodela/%s/delete/' % obj.pk)
        self.assertEqual(response.status_code, 200)

    def test_crud_direction(self):
        self.client.login(username='john.doe', password='xxx12345')
        # create
        response = self.client.get('/admin/composite_field_test/direction/add/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/admin/composite_field_test/direction/add/', {
            'source_x': '0.25',
            'source_y': '0.5',
            'distance': str(math.sqrt(2.0)),
            'target_x': '1.25',
            'target_y': '1.5',
        })
        direction = Direction.objects.get()
        self.assertEqual(direction.source_x, 0.25)
        self.assertEqual(direction.source_y, 0.5)
        self.assertAlmostEqual(direction.distance, math.sqrt(2))
        self.assertEqual(direction.target_x, 1.25)
        self.assertEqual(direction.target_y, 1.5)
        self.assertEqual(response.status_code, 302)
        # read
        response = self.client.get('/admin/composite_field_test/direction/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/admin/composite_field_test/direction/1/change/')
        self.assertEqual(response.status_code, 200)
        # update
        response = self.client.post('/admin/composite_field_test/direction/1/change/', {
            'source_x': '0.5',
            'source_y': '0.75',
            'distance': str(math.sqrt(2.0)/2.0),
            'target_x': '1.0',
            'target_y': '1.25',
        })
        direction = Direction.objects.get()
        self.assertEqual(direction.source_x, 0.5)
        self.assertEqual(direction.source_y, 0.75)
        self.assertAlmostEqual(direction.distance, math.sqrt(2)/2.0)
        self.assertEqual(direction.target_x, 1.0)
        self.assertEqual(direction.target_y, 1.25)
        self.assertEqual(response.status_code, 302)
        # delete
        response = self.client.get('/admin/composite_field_test/direction/1/delete/')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/admin/composite_field_test/direction/1/delete/', {
            'post': 'yes',
        })
        self.assertEqual(response.status_code, 302)

    def test_readonly(self):
        self.client.login(username='john.doe', password='xxx12345')

        place = PlaceWithDefaultCoord.objects.create()

        response = self.client.get(reverse('admin:composite_field_test_placewithdefaultcoord_change', args=(place.id,)))
        self.assertEqual(response.status_code, 200)
