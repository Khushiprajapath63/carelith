from django.contrib import admin
from .models import Doctor

admin.site.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'specialization',
        'qualification',
        'contact_number',
        'hospital'
    )
