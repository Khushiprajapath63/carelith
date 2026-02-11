from django.contrib import admin
from .models import Laboratory

@admin.register(Laboratory)
class LaboratoryAdmin(admin.ModelAdmin):
    list_display =  ("name", "phone", "address", "location")
