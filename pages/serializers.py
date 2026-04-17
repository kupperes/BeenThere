from rest_framework import serializers

from .models import HistoricSite


class HistoricSiteSerializer(serializers.ModelSerializer):
    distance_miles = serializers.FloatField(read_only=True)

    class Meta:
        model = HistoricSite
        fields = [
            'id',
            'name',
            'summary',
            'description',
            'latitude',
            'longitude',
            'address',
            'city',
            'state',
            'category',
            'designation',
            'era',
            'source_name',
            'source_id',
            'wikipedia_url',
            'reference_url',
            'image_url',
            'is_verified',
            'distance_miles',
        ]
