from django.conf import settings
from django.db import models
from django.utils import timezone

class ArtisanVerification(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        UNDER_REVIEW = 'under_review', 'Under review'
        MORE_INFO = 'more_info_required', 'More information required'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
        SUSPENDED = 'suspended', 'Suspended'

    class IDType(models.TextChoices):
        NIN = 'nin', 'NIN slip/card'
        VOTER = 'voter_card', "Voter's card"
        DRIVER = 'drivers_license', "Driver's licence"
        PASSPORT = 'passport', 'International passport'
        OTHER = 'other', 'Other government-issued ID'

    class ReviewMethod(models.TextChoices):
        IN_PERSON = 'in_person', 'In-person inspection'
        VIDEO = 'video_call', 'Live video inspection'

    artisan = models.ForeignKey('marketplace.ArtisanProfile', on_delete=models.CASCADE, related_name='verification_applications')
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING, db_index=True)
    legal_name = models.CharField(max_length=160)
    contact_phone = models.CharField(max_length=24)
    operating_address = models.CharField(max_length=255)
    id_type = models.CharField(max_length=24, choices=IDType.choices)
    id_last_four = models.CharField(max_length=4, blank=True, help_text='Only last four characters; never store full ID number.')
    review_method = models.CharField(max_length=16, choices=ReviewMethod.choices)
    consent_given = models.BooleanField(default=False)
    consent_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='artisan_verification_reviews')
    admin_notes = models.TextField(blank=True)
    artisan_message = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    resubmission_count = models.PositiveSmallIntegerField(default=0)

    # Manual checks. These record what an authorised reviewer actually completed;
    # they are not claims of an external registry/database match.
    phone_confirmed = models.BooleanField(default=False)
    identity_document_reviewed = models.BooleanField(default=False)
    live_person_id_match_confirmed = models.BooleanField(default=False)
    professional_profile_reviewed = models.BooleanField(default=False)
    location_reviewed = models.BooleanField(default=False)
    reference_checked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.artisan.display_name} – {self.get_status_display()}'

    @property
    def all_required_checks_complete(self):
        return all((self.phone_confirmed, self.identity_document_reviewed,
                    self.live_person_id_match_confirmed, self.professional_profile_reviewed,
                    self.location_reviewed, self.reference_checked))


class VerificationAuditLog(models.Model):
    verification = models.ForeignKey(ArtisanVerification, on_delete=models.CASCADE, related_name='audit_logs')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=40)
    previous_status = models.CharField(max_length=24, blank=True)
    new_status = models.CharField(max_length=24, blank=True)
    reason = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.action} – verification #{self.verification_id}'
