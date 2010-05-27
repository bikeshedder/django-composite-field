from copy import deepcopy

from django.db.models.fields import Field
from django.utils.datastructures import SortedDict


class CompositeFieldBase(type):
    '''Metaclass for all composite fields.'''

    def __new__(cls, name, bases, attrs):
        super_new = super(CompositeFieldBase, cls).__new__
        # If this isn't a subclass of CompositeField, don't do anything special.
        if not any(isinstance(b, CompositeFieldBase) for b in bases):
            return super_new(cls, name, bases, attrs)

        # Prepare attributes.
        fields = []
        for field_name, field in attrs.items():
            if hasattr(field, 'contribute_to_class'):
                fields.append((field_name, field))
                del attrs[field_name]
        fields.sort(key=lambda x: x[1].creation_counter)
        attrs['subfields'] = SortedDict(fields)

        # Create the class.
        new_class = super_new(cls, name, bases, attrs)
        return new_class


class CompositeField(object):
    __metaclass__ = CompositeFieldBase

    def contribute_to_class(self, cls, field_name):
        self.field_name = field_name
        if self.prefix is None:
            self.prefix = '%s_' % field_name
        for subfield_name, subfield in self.subfields.iteritems():
            name = self.prefix + subfield_name
            if hasattr(cls, name):
                raise RuntimeError('contribute_to_class for %s.%s failed due to ' \
                        'duplicate field name %s' % (cls.__name__, field_name, name))
            subfield.contribute_to_class(cls, name)
        setattr(cls, field_name, property(self.get, self.set))

    def __init__(self, prefix=None):
        self.prefix = prefix
        self.subfields = deepcopy(self.subfields)
        for subfield in self.subfields.itervalues():
            subfield.creation_counter = Field.creation_counter
            Field.creation_counter += 1

    def __getitem__(self, name):
        return self.subfields[name]

    def __setitem__(self, name, subfield):
        self.subfields[name] = subfield

    def __contains__(self, name):
        return name in self.subfields

    def __iter__(self):
        return self.subfields.iterkeys()

    def get_proxy(self, model):
        return CompositeField.Proxy(self, model)

    def get(self, model):
        return self.get_proxy(model)

    def set(self, model, value):
        self.get_proxy(model)._set(value)

    class Proxy(object):

        def __init__(self, composite_field, model):
            object.__setattr__(self, '_composite_field', composite_field)
            object.__setattr__(self, '_model', model)

        def _subfield_name(self, name):
            if not name in self._composite_field:
                raise AttributeError('%r object has no attribute %r' % (
                        self._composite_field.__class__.__name__, name))
            return self._composite_field.prefix + name

        def _set(self, values):
            for name in self._composite_field:
                subfield_name = self._composite_field.prefix + name
                setattr(self._model, subfield_name, getattr(values, name))

        def __setattr__(self, name, value):
            setattr(self._model, self._subfield_name(name), value)

        def __getattr__(self, name):
            return getattr(self._model, self._subfield_name(name))

        def __cmp__(self, another):
            for name in self._composite_field:
                pred = cmp(getattr(self, name),
                         getattr(another, name))
                if pred != 0:
                    return pred
            return 0

        def __repr__(self):
            fields = ', '.join(
                '%s=%r' % (name, getattr(self, name))
                        for name in self._composite_field
            )
            return '%s(%s)' % (self._composite_field.__class__.__name__, fields)
