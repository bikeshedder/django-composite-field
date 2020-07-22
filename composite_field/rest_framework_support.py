from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .base import CompositeField


class CompositeFieldSerializer(serializers.Field):

    def to_representation(self, obj):
        return obj.to_dict()

    def to_internal_value(self, data):
        # FIXME add validation of max_length parameter
        return data


# Make CompositeFieldSerializer the default serializer for CompositeField
ModelSerializer.serializer_field_mapping[CompositeField] = CompositeFieldSerializer


class CompositeFieldModelSerializerMixin(object):

    def build_property_field(self, field_name, model_class):
        from composite_field.base import CompositeField
        model_field = model_class._meta.get_field(field_name)
        if isinstance(model_field, CompositeField):
            field_class = CompositeFieldSerializer
            field_kwargs = {}
            return field_class, field_kwargs
        return super(CompositeFieldModelSerializerMixin, self) \
            .build_property_field(field_name, model_class)


class ModelSerializer(CompositeFieldModelSerializerMixin, serializers.ModelSerializer):
    pass
