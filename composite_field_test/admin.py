from django.contrib import admin

from . import models


class PlaceWithDefaultCoordAdmin(admin.ModelAdmin):
    fields = ('coord',)
    readonly_fields = ('coord',)


class TranslatedModelAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(models.Place)
admin.site.register(models.PlaceWithDefaultCoord, PlaceWithDefaultCoordAdmin)
admin.site.register(models.Direction)
admin.site.register(models.ComplexTuple)
admin.site.register(models.ComplexTupleWithDefaults)
admin.site.register(models.TranslatedModelA, TranslatedModelAdmin)
admin.site.register(models.TranslatedModelB, TranslatedModelAdmin)
admin.site.register(models.TranslatedModelC, TranslatedModelAdmin)
admin.site.register(models.TranslatedModelD, TranslatedModelAdmin)
