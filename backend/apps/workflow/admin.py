from django.contrib import admin
from .models import (ServiceRequest,Quote,Payment,Review,PaymentMilestone,Disbursement,LedgerEntry,PaymentWebhookEvent,ArtisanPayoutAccount,ChangeOrder)
@admin.register(ServiceRequest)
class RequestAdmin(admin.ModelAdmin):
    list_display=('id','service_name','customer','artisan','status','created_at')
    list_filter=('status','created_at')
    search_fields=('customer__email','service_name','location')
@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display=('id','service_request','artisan','amount','status','schedule_approved')
    list_filter=('status','schedule_approved')
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display=('id','reference','amount','status','verified_at')
    readonly_fields=('reference','amount_kobo','provider_transaction_id','verified_at')
admin.site.register([PaymentMilestone,Disbursement,LedgerEntry,PaymentWebhookEvent,ArtisanPayoutAccount,ChangeOrder,Review])
