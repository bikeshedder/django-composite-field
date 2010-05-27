from copy import deepcopy

from django.conf import settings 
from django.db.models.fields import Field, CharField, TextField, FloatField
from django.utils.functional import lazy

from . import CompositeField


LANGUAGES = map(lambda lang: lang[0], getattr(settings, 'LANGUAGES', ()))


class LocalizedField(CompositeField):

    def __init__(self, field_class, languages=LANGUAGES, **kwargs):
        if not languages:
            raise RuntimeError('Set LANGUAGES in your settings.py or pass a non empty "languages" argument before using LocalizedCharField')
        super(LocalizedField, self).__init__()
        self.verbose_name = kwargs.pop('verbose_name', None)
        for language in languages:
            self[language] = field_class(**kwargs)

    def contribute_to_class(self, cls, field_name):
        if self.verbose_name is None:
            self.verbose_name = field_name.replace('_', ' ')
        for language in self:
            # verbose_name must be lazy in order for the admin to show the
            # translated verbose_names of the fields
            self[language].verbose_name = lazy(lambda language: u'%s (%s)' % (
                    self.verbose_name, language), unicode)(language)
        super(LocalizedField, self).contribute_to_class(cls, field_name)

    def get_proxy(self, model):
        return LocalizedField.Proxy(self, model)

    class Proxy(CompositeField.Proxy):

        def __nonzero__(self):
            return bool(unicode(self))

        def __unicode__(self):
            from django.utils.translation import get_language
            language = get_language()
            translation = None
            # 1. complete language code
            translation = getattr(self, language, None)
            if translation is not None:
                return translation
            # 2. base of language code
            if '-' in language:
                base_lang = language.split('-')[0]
                translation = getattr(self, base_lang, None)
                if translation is not None:
                    return translation
            # 3. first available translation
            for language in settings.LANGUAGES:
                getattr(self, base_lang, None)
                if translation is not None:
                    return translation
            return None


class LocalizedCharField(LocalizedField):

    def __init__(self, **kwargs):
        super(LocalizedCharField, self).__init__(CharField, **kwargs)


class LocalizedTextField(LocalizedField):

    def __init__(self, **kwargs):
        super(LocalizedTextField, self).__init__(TextField, **kwargs)
