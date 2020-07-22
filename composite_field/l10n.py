from django.conf import settings
from django.db import models
from django.utils import translation
from django.utils.functional import lazy
from django.utils.translation import get_language

from .base import CompositeField


LANGUAGES = [lang[0] for lang in getattr(settings, 'LANGUAGES', [])]


class LocalizedField(CompositeField):

    def __init__(self, field_class, verbose_name=None, *args, **kwargs):
        self.languages = kwargs.pop('languages', LANGUAGES)
        if not self.languages:
            raise RuntimeError(
                'Set LANGUAGES in your settings.py or pass a non empty '
                '"languages" argument before using LocalizedCharField'
            )
        super(LocalizedField, self).__init__()
        self.verbose_name = verbose_name
        kwargs['verbose_name'] = verbose_name
        for language in self.languages:
            self[language] = field_class(*args, **kwargs)

    def contribute_to_class(self, cls, field_name):
        if self.verbose_name is None:
            self.verbose_name = field_name.replace('_', ' ')
        for language in self:
            # verbose_name must be lazy in order for the admin to show the
            # translated verbose_names of the fields
            self[language].verbose_name = lazy(lambda language: self.verbose_name + ' (' + language + ')', str)(language)
        super(LocalizedField, self).contribute_to_class(cls, field_name)

    def get_col(self, alias, output_field=None):
        current_field = self.current_field
        return current_field.get_col(alias, current_field)

    @property
    def current_field(self):
        language = get_language() or settings.LANGUAGE_CODE
        base_lang = language.split('-')[0]
        return self[base_lang]

    @property
    def help_text(self):
        return self.current_field.help_text

    @property
    def choices(self):
        return self.current_field.choices

    @property
    def max_length(self):
        return self.current_field.max_length

    def set(self, model, value):
        from django.utils.functional import Promise
        # XXX is there a better way to detect ugettext_lazy objects?
        if isinstance(value, Promise):
            d = {}
            for language in self:
                with translation.override(language):
                    d[language] = str(value)
            value = d
        return super(LocalizedField, self).set(model, value)

    class Proxy(CompositeField.Proxy):

        def __bool__(self):
            return bool(self.current_with_fallback)

        def __str__(self):
            # Current_with_fallback can be a non-string type when using
            # the localized field with a non-string Field. e.g.
            # LocalizedField(IntegerField) is possilbe and would result
            # in an error if leaving out the text_type(...) call.
            return str(self.current_with_fallback)

        def __setattr__(self, name, value):
            if name == 'current':
                language = get_language() or settings.LANGUAGE_CODE
                base_lang = language.split('-')[0]
                return setattr(self, base_lang, value)
            if name == 'all':
                for language in self._composite_field.languages:
                    setattr(self, language, value)
                return value
            else:
                return super(LocalizedField.Proxy, self).__setattr__(name, value)

        @property
        def current(self):
            language = get_language() or settings.LANGUAGE_CODE
            base_lang = language.split('-')[0]
            return getattr(self, base_lang)

        @property
        def current_with_fallback(self):
            language = get_language() or settings.LANGUAGE_CODE
            translation = None
            # 1. complete language code
            translation = getattr(self, language, None)
            if translation:
                return translation
            # 2. base of language code
            if '-' in language:
                base_lang = language.split('-')[0]
                translation = getattr(self, base_lang, None)
                if translation:
                    return translation
            # 3. first available translation
            for language in settings.LANGUAGES:
                base_lang = language[0].split('-')[0]
                translation = getattr(self, base_lang, None)
                if translation:
                    return translation
            return u''


class LocalizedCharField(LocalizedField):

    def __init__(self, *args, **kwargs):
        super(LocalizedCharField, self).__init__(models.CharField, *args, **kwargs)


class LocalizedTextField(LocalizedField):

    def __init__(self, *args, **kwargs):
        super(LocalizedTextField, self).__init__(models.TextField, *args, **kwargs)
