from django.db import models
from django.utils import timezone

from patients.models import Patient
from doctor_app.models import Doctor
from laboratory.models import Laboratory
from hospital_app.models import Hospital


# =========================
# Encounter
# =========================
class Encounter(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="encounters"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="encounters"
    )

    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="encounters"
    )

    reason = models.CharField(max_length=255)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Encounter #{self.id} - {self.patient}"


# =========================
# Observation
# =========================
class Observation(models.Model):
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.CASCADE,
        related_name="observations"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="observations"
    )

    code = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, null=True, blank=True)

    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code}: {self.value}{self.unit or ''}"


# =========================
# Diagnostic Report
# =========================
class Report(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("explained", "Explained"),
    )

    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.CASCADE,
        related_name="reports",
        null=True,
        blank=True
    )

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="reports"
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reports"
    )

    # ✅ KEEP NULL=True for SQLite safety
    laboratory = models.ForeignKey(
        Laboratory,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="reports"
    )

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="reports/", null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        null=True,          # IMPORTANT for existing rows
        blank=True
    )

    def __str__(self):
        return f"Report: {self.title} ({self.patient})"


# =========================
# Prescription
# =========================
class Prescription(models.Model):
    encounter = models.ForeignKey(
        Encounter,
        on_delete=models.CASCADE,
        related_name="prescriptions",
        null=True,
        blank=True
    )

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="prescriptions"
    )

    medicines = models.TextField()
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def patient(self):
        return self.encounter.patient if self.encounter else None

    def __str__(self):
        return f"Prescription - {self.patient}"
