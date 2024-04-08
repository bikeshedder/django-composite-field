from collections import OrderedDict
from copy import deepcopy

from django.db.models.fields import Field


class CompositeFieldBase(type):
    '''Metaclass for all composite fields.'''

    def __new__(cls, name, bases, attrs):
        super_new = super(CompositeFieldBase, cls).__new__
        # If this isn't a subclass of CompositeField, don't do anything special.
        if not any(isinstance(b, CompositeFieldBase) for b in bases):
            return super_new(cls, name, bases, attrs)

        # Prepare attributes.
        fields = []
        for field_name, field in list(attrs.items()):
            if hasattr(field, 'contribute_to_class'):
                fields.append((field_name, field))
                del attrs[field_name]
        fields.sort(key=lambda x: x[1].creation_counter)
        attrs['subfields'] = OrderedDict(fields)

        # Create the class.
        new_class = super_new(cls, name, bases, attrs)
        return new_class


class CompositeField(object, metaclass=CompositeFieldBase):
    is_relation = False
    concrete = False
    column = None
    remote_field = None
    unique = False
    auto_created = False
    editable = False
    serialize = False
    blank = True
    empty_values = []
    primary_key = False
    flatchoices = []

    # Field flags
    hidden = False

    many_to_many = None
    many_to_one = None
    one_to_many = None
    one_to_one = None
    related_model = None
    generated = False

    def contribute_to_class(self, cls, name):
        self.name = name
        self.field_name = name
        self.attname = name
        if self.verbose_name is None and self.name:
            self.verbose_name = self.name.replace('_', ' ')
        # Only add the subfields for non-abstract models and use the model
        # attribute to detect non-abstract inheritance. Without this check
        # the subfields would be added multiple times.
        if not cls._meta.abstract and not self.model:
            self.model = cls
            if self.prefix is None:
                self.prefix = '%s_' % name
            for subfield_name, subfield in self.subfields.items():
                subfield_name = self.prefix + subfield_name

                if subfield.verbose_name:
                    # If subfields have a verbose_name set, attempt substitution
                    # of parent_verbose_name.

                    subfield.verbose_name = subfield.verbose_name % {
                        "parent_verbose_name": self.verbose_name
                    }

                subfield.contribute_to_class(cls, subfield_name)
            setattr(cls, name, property(self.get, self.set))
        cls._meta.add_field(self, private=True)

    def __init__(self, prefix=None, default=None, verbose_name=None):
        self.verbose_name = verbose_name
        self.default = default or {}
        self.prefix = prefix
        self.model = None
        self.subfields = deepcopy(self.subfields)
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1
        for subfield in self.subfields.values():
            subfield.creation_counter = Field.creation_counter
            Field.creation_counter += 1
        for name, value in self.default.items():
            self.subfields[name].default = value

    def __getitem__(self, name):
        return self.subfields[name]

    def __setitem__(self, name, subfield):
        self.subfields[name] = subfield

    def __contains__(self, name):
        return name in self.subfields

    def __iter__(self):
        return iter(self.subfields.keys())

    def __eq__(self, other):
        if isinstance(other, (CompositeField, Field)):
            return self.creation_counter == other.creation_counter
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, (CompositeField, Field)):
            return self.creation_counter < other.creation_counter
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, (CompositeField, Field)):
            return self.creation_counter > other.creation_counter
        return NotImplemented

    def __hash__(self):
        return hash(self.creation_counter)

    def get_proxy(self, model):
        return self.Proxy(self, model)

    def get(self, model):
        return self.get_proxy(model)

    def set(self, model, value):
        self.get_proxy(model)._set(value)

    def clean(self, value, model):
        return value

    def formfield(self, form):
        from django import forms
        return forms.CharField()

    def get_attname_column(self):
        return self.attname, None

    class Proxy(object):

        def __init__(self, composite_field, model):
            object.__setattr__(self, '_composite_field', composite_field)
            object.__setattr__(self, '_model', model)

        def _subfield_name(self, name):
            if name not in self._composite_field:
                raise AttributeError('%r object has no attribute %r' % (
                        self._composite_field.__class__.__name__, name))
            return self._composite_field.prefix + name

        def _set(self, values):
            if isinstance(values, dict):
                for name in self._composite_field:
                    subfield_name = self._composite_field.prefix + name
                    setattr(self._model, subfield_name, values[name])
            else:
                for name in self._composite_field:
                    subfield_name = self._composite_field.prefix + name
                    setattr(self._model, subfield_name, getattr(values, name))

        def __setattr__(self, name, value):
            setattr(self._model, self._subfield_name(name), value)

        def __getattr__(self, name):
            return getattr(self._model, self._subfield_name(name))

        def __eq__(self, other):
            try:
                attrs_eq = [getattr(self, f) == getattr(other, f) for f in
                            self._composite_field]
            except AttributeError:
                return False
            return isinstance(other, self.__class__) and all(attrs_eq)

        def __ne__(self, other):
            return not self.__eq__(other)

        def __repr__(self):
            fields = ', '.join(
                '%s=%r' % (name, getattr(self, name))
                for name in self._composite_field
            )
            return '%s(%s)' % (self._composite_field.__class__.__name__, fields)

        def __bool__(self):
            return True

        def __nonzero__(self):
            return self.__bool__()

        def to_dict(self):
            return {
                name: getattr(self, name)
                for name in self._composite_field
            }
