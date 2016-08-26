from django.contrib import admin

from . import models


admin.site.register(models.Place)
admin.site.register(models.Direction)
admin.site.register(models.ComplexTuple)
admin.site.register(models.ComplexTupleWithDefaults)
admin.site.register(models.TranslatedModelA)
admin.site.register(models.TranslatedModelB)
admin.site.register(models.TranslatedModelC)
admin.site.register(models.TranslatedModelD)
