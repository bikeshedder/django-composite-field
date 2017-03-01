from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from composite_field import CompositeField
from composite_field import LocalizedCharField
from composite_field import ComplexField


class CoordField(CompositeField):
    x = models.FloatField()
    y = models.FloatField()


class Place(models.Model):
    name = models.CharField(max_length=10)
    coord = CoordField()


class PlaceWithDefaultCoord(models.Model):
    name = models.CharField(max_length=10)
    coord = CoordField(default={'x': 1.0, 'y': 2.0})


class Direction(models.Model):
    source = CoordField()
    distance = models.FloatField()
    target = CoordField()


@python_2_unicode_compatible
class LocalizedFoo(models.Model):
    id = models.AutoField(primary_key=True)
    name = LocalizedCharField(languages=('de', 'en'), max_length=50)

    def __str__(self):
        return self.name.current


class ComplexTuple(models.Model):
    x = ComplexField(blank=True, null=True)
    y = ComplexField(blank=False, null=False, verbose_name='Y')
    z = ComplexField(verbose_name='gamma')


class ComplexTupleWithDefaults(models.Model):
    x = ComplexField(blank=True, null=True, default=None)
    y = ComplexField(blank=False, null=False, default=42)
    z = ComplexField(default=42j)


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
