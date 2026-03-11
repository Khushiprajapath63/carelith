from django.contrib import admin
from .models import Encounter, Report, Prescription, AuditLog


@admin.register(Encounter)
class EncounterAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "started_at")


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "title", "status", "created_at")


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "created_at")


# ⭐ Audit Log Admin
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "action", "ip_address", "timestamp")
    list_filter = ("action", "timestamp")


admin.site.register(AuditLog, AuditLogAdmin)