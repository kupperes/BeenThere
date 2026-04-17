from django.contrib.auth.models import User
from rest_framework import serializers

from .models import HistoricSite, ImportRun, SourceFeed, UserVisit


class SourceFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceFeed
        fields = [
            'id',
            'name',
            'slug',
            'jurisdiction_level',
            'jurisdiction_name',
            'source_type',
            'homepage_url',
            'download_url',
            'license',
            'refresh_strategy',
            'is_active',
        ]


class HistoricSiteSerializer(serializers.ModelSerializer):
    distance_miles = serializers.FloatField(read_only=True)
    source_feed = SourceFeedSerializer(read_only=True)
    visited = serializers.SerializerMethodField()

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
            'source_feed',
            'source_name',
            'source_id',
            'wikipedia_url',
            'reference_url',
            'image_url',
            'is_verified',
            'distance_miles',
            'visited',
        ]

    def get_visited(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return False
        return getattr(obj, 'visited', None) or obj.user_visits.filter(user=user).exists()


class ImportRunSerializer(serializers.ModelSerializer):
    source_feed = SourceFeedSerializer(read_only=True)

    class Meta:
        model = ImportRun
        fields = [
            'id',
            'source_feed',
            'status',
            'imported_count',
            'created_count',
            'updated_count',
            'failed_count',
            'notes',
            'error_log',
            'started_at',
            'finished_at',
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'first_name', 'last_name']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserVisitSerializer(serializers.ModelSerializer):
    historic_site = HistoricSiteSerializer(read_only=True)

    class Meta:
        model = UserVisit
        fields = ['id', 'historic_site', 'visited_at']
