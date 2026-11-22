from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
@admin.register(User)
class WarriWorksUserAdmin(UserAdmin):
 list_display=('email','username','role','phone','is_active','is_staff')
 fieldsets=UserAdmin.fieldsets + (('WarriWorks',{'fields':('role','phone','legacy_password_hash')}),)
