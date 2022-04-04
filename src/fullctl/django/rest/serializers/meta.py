from rest_framework import serializers

from fullctl.django.rest.serializers import ModelSerializer


class Data(ModelSerializer):

    ref_tag = "meta_data"
    meta_source = None

    data = serializers.SerializerMethodField()

    class Meta:
        fields = ["id", "data"]

    def get_data(self, obj):
        return obj.data.get(self.meta_source, {})
