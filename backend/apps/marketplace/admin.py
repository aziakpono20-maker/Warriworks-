from django.contrib import admin
from .models import ArtisanProfile,ServiceCategory
@admin.register(ArtisanProfile)
class ArtisanAdmin(admin.ModelAdmin): list_display=('display_name','skill','location','verified','verification_status','is_available'); list_filter=('verified','verification_status','skill'); search_fields=('display_name','skill','location','user__email')
admin.site.register(ServiceCategory)

# Verification applications and immutable audit history are managed in the dedicated verification app.
