from . import CompositeField
from . import FloatField


class ComplexField(CompositeField):

    real = FloatField()
    imag = FloatField()

    def __init__(self, verbose_name=None, blank=False, null=False, default=None):
        super(ComplexField, self).__init__()
        self.verbose_name = verbose_name
        for field in (self['real'], self['imag']):
            field.blank = blank
            field.null = blank
        if default is not None:
            self['real'].default = default.real
            self['imag'].default = default.imag

    def contribute_to_class(self, cls, field_name):
        if self.verbose_name is None:
            self.verbose_name = field_name.replace('_', ' ')
        self['real'].verbose_name = 'Re(%s)' % self.verbose_name
        self['imag'].verbose_name = 'Im(%s)' % self.verbose_name
        super(ComplexField, self).contribute_to_class(cls, field_name)

    def get(self, model):
        proxy = self.get_proxy(model)
        real, imag = proxy.real, proxy.imag
        if real is None and imag is None:
            return None
        return complex(real or 0, imag or 0)

    def set(self, model, value):
        proxy = self.get_proxy(model)
        if value is None:
            proxy.real = None
            proxy.imag = None
        else:
            proxy.real = value.real
            proxy.imag = value.imag
