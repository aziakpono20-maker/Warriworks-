from django.contrib import admin
from .models import ArtisanVerification, VerificationAuditLog

class VerificationAuditInline(admin.TabularInline):
    model = VerificationAuditLog
    extra = 0
    can_delete = False
    readonly_fields = ('actor', 'action', 'previous_status', 'new_status', 'reason', 'metadata', 'created_at')

@admin.register(ArtisanVerification)
class ArtisanVerificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'artisan', 'status', 'submitted_at', 'reviewed_by')
    list_filter = ('status', 'id_type', 'review_method')
    search_fields = ('artisan__display_name', 'legal_name', 'contact_phone', 'artisan__user__email')
    readonly_fields = ('submitted_at', 'reviewed_at', 'consent_at')
    inlines = [VerificationAuditInline]

@admin.register(VerificationAuditLog)
class VerificationAuditLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'verification', 'actor', 'action', 'created_at')
    readonly_fields = ('verification', 'actor', 'action', 'previous_status', 'new_status', 'reason', 'metadata', 'created_at')
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False
