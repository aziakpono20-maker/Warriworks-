from django.conf import settings
from django.db import models
from apps.marketplace.models import ArtisanProfile, ServiceCategory

class ServiceRequest(models.Model):
    class Status(models.TextChoices):
        OPEN='open','Open'; ACCEPTED='accepted','Accepted'; QUOTED='quoted','Quoted'; APPROVED='approved','Quote approved'; PAYMENT_PENDING='payment_pending','Payment pending'; IN_PROGRESS='in_progress','In progress'; COMPLETION_REVIEW='completion_review','Awaiting customer confirmation'; COMPLETED='completed','Completed'; CANCELLED='cancelled','Cancelled'; DISPUTED='disputed','Disputed'
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='service_requests')
    artisan = models.ForeignKey(ArtisanProfile, on_delete=models.PROTECT, related_name='service_requests', null=True, blank=True)
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, null=True, blank=True)
    service_name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=180)
    preferred_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.OPEN)
    customer_phone = models.CharField(max_length=24, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering = ['-created_at']

class Quote(models.Model):
    class Status(models.TextChoices):
        PENDING='pending','Pending'; ACCEPTED='accepted','Accepted'; REVISION='revision_requested','Revision requested'; REJECTED='rejected','Rejected'
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='quotes')
    artisan = models.ForeignKey(ArtisanProfile, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    notes = models.TextField(blank=True)
    cost_breakdown = models.JSONField(default=dict, blank=True)
    payment_schedule = models.JSONField(default=list, blank=True)
    schedule_approved = models.BooleanField(default=False)
    schedule_request_reason = models.TextField(blank=True)
    schedule_review_reason = models.TextField(blank=True)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.PENDING)
    version = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    class Status(models.TextChoices):
        INITIATED='initiated','Initiated'; PENDING='pending','Pending'; SUCCESSFUL='successful','Successful'; PARTIALLY_DISBURSED='partially_disbursed','Partially disbursed'; COMPLETED='completed','Completed'; FAILED='failed','Failed'; REFUNDED='refunded','Refunded'; DISPUTED='disputed','Disputed'
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.PROTECT, related_name='payments')
    quote = models.ForeignKey(Quote, on_delete=models.PROTECT)
    provider = models.CharField(max_length=30, default='paystack')
    reference = models.CharField(max_length=120, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_kobo = models.PositiveBigIntegerField(default=0)
    currency = models.CharField(max_length=3, default='NGN')
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.INITIATED)
    provider_transaction_id = models.CharField(max_length=100, blank=True)
    checkout_url = models.URLField(blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PaymentMilestone(models.Model):
    class Status(models.TextChoices):
        LOCKED='locked','Locked'; READY='ready','Ready'; PROCESSING='processing','Processing'; PAID='paid','Paid'; BLOCKED='blocked','Blocked'; FAILED='failed','Failed'
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name='milestones')
    sequence = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=100)
    percentage = models.PositiveSmallIntegerField()
    amount_kobo = models.PositiveBigIntegerField()
    release_condition = models.TextField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.LOCKED)
    evidence = models.JSONField(default=list, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    class Meta:
        ordering=['sequence']
        constraints=[models.UniqueConstraint(fields=['payment','sequence'], name='unique_payment_milestone_sequence')]

class ArtisanPayoutAccount(models.Model):
    artisan = models.OneToOneField(ArtisanProfile, on_delete=models.PROTECT, related_name='payout_account')
    bank_code = models.CharField(max_length=20)
    account_name = models.CharField(max_length=160)
    recipient_code = models.CharField(max_length=100, blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Disbursement(models.Model):
    class Status(models.TextChoices):
        QUEUED='queued','Queued'; PROCESSING='processing','Processing'; SUCCESSFUL='successful','Successful'; FAILED='failed','Failed'; REVERSED='reversed','Reversed'; CANCELLED='cancelled','Cancelled'
    milestone = models.OneToOneField(PaymentMilestone, on_delete=models.PROTECT, related_name='disbursement')
    artisan = models.ForeignKey(ArtisanProfile, on_delete=models.PROTECT)
    amount_kobo = models.PositiveBigIntegerField()
    reference = models.CharField(max_length=120, unique=True)
    transfer_code = models.CharField(max_length=120, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.QUEUED)
    provider_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LedgerEntry(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name='ledger_entries')
    milestone = models.ForeignKey(PaymentMilestone, on_delete=models.PROTECT, null=True, blank=True)
    entry_type = models.CharField(max_length=40)
    amount_kobo = models.BigIntegerField()
    reference = models.CharField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['created_at']

class PaymentWebhookEvent(models.Model):
    provider_event_key = models.CharField(max_length=160, unique=True)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    processed_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

class ChangeOrder(models.Model):
    class Status(models.TextChoices):
        PENDING='pending','Pending'; ACCEPTED='accepted','Accepted'; REJECTED='rejected','Rejected'
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name='change_orders')
    reason = models.TextField()
    old_amount_kobo = models.PositiveBigIntegerField()
    new_amount_kobo = models.PositiveBigIntegerField()
    proposed_schedule = models.JSONField(default=list)
    artisan_approved_at = models.DateTimeField(null=True, blank=True)
    customer_approved_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='review')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    artisan = models.ForeignKey(ArtisanProfile, on_delete=models.PROTECT)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def clean(self):
        from django.core.exceptions import ValidationError
        if not 1 <= self.rating <= 5:
            raise ValidationError('Rating must be between 1 and 5.')
