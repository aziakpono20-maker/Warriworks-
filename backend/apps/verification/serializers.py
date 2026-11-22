from django.utils import timezone
from rest_framework import serializers
from .models import ArtisanVerification, VerificationAuditLog

class ArtisanVerificationSubmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtisanVerification
        fields = ['legal_name', 'contact_phone', 'operating_address', 'id_type', 'id_last_four', 'review_method', 'consent_given']

    def validate_consent_given(self, value):
        if not value:
            raise serializers.ValidationError('Consent is required before submitting verification information.')
        return value

    def validate_id_last_four(self, value):
        if value and (len(value) != 4 or not value.isalnum()):
            raise serializers.ValidationError('Enter only the last four alphanumeric characters, or leave blank.')
        return value

    def create(self, validated_data):
        validated_data['consent_at'] = timezone.now()
        return super().create(validated_data)

class ArtisanVerificationStatusSerializer(serializers.ModelSerializer):
    artisan_name = serializers.CharField(source='artisan.display_name', read_only=True)
    class Meta:
        model = ArtisanVerification
        fields = ['id', 'artisan_name', 'status', 'legal_name', 'contact_phone', 'operating_address', 'id_type', 'review_method', 'submitted_at', 'reviewed_at', 'artisan_message', 'rejection_reason', 'resubmission_count']
        read_only_fields = fields

class AdminVerificationSerializer(serializers.ModelSerializer):
    artisan_name = serializers.CharField(source='artisan.display_name', read_only=True)
    artisan_email = serializers.EmailField(source='artisan.user.email', read_only=True)
    artisan_skill = serializers.CharField(source='artisan.skill', read_only=True)
    artisan_location = serializers.CharField(source='artisan.location', read_only=True)
    class Meta:
        model = ArtisanVerification
        fields = ['id', 'artisan', 'artisan_name', 'artisan_email', 'artisan_skill', 'artisan_location', 'status', 'legal_name', 'contact_phone', 'operating_address', 'id_type', 'id_last_four', 'review_method', 'consent_given', 'submitted_at', 'reviewed_at', 'admin_notes', 'artisan_message', 'rejection_reason', 'resubmission_count', 'phone_confirmed', 'identity_document_reviewed', 'live_person_id_match_confirmed', 'professional_profile_reviewed', 'location_reviewed', 'reference_checked']
        read_only_fields = ['id', 'artisan', 'artisan_name', 'artisan_email', 'artisan_skill', 'artisan_location', 'status', 'submitted_at', 'reviewed_at', 'consent_given', 'resubmission_count']

class VerificationAuditSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source='actor.email', read_only=True)
    class Meta:
        model = VerificationAuditLog
        fields = ['id', 'actor_email', 'action', 'previous_status', 'new_status', 'reason', 'metadata', 'created_at']
