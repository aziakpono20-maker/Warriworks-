from rest_framework import serializers
from .models import ArtisanProfile, ServiceCategory


class ArtisanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtisanProfile
        fields = [
            'id', 'display_name', 'skill', 'location', 'bio', 'verified',
            'verification_status', 'profile_image', 'portfolio',
            'years_experience', 'is_available',
        ]
        read_only_fields = ['verified', 'verification_status']


class ArtisanProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtisanProfile
        fields = [
            'display_name', 'skill', 'location', 'bio', 'phone_public',
            'years_experience', 'is_available',
        ]

    def validate_display_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError('Enter a name with at least 2 characters.')
        return value

    def validate_skill(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Your primary skill is required.')
        return value

    def validate_location(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Your service location is required.')
        return value


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'slug', 'description', 'icon_key']
