from django.db import models
from doctor_app.models import Doctor
from patients.models import Patient
from hospital_app.models import Hospital

class PatientAccess(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    from_hospital = models.ForeignKey(
    Hospital,
    related_name="from_requests",
    on_delete=models.CASCADE,
    null=True,
    blank=True
    )

    to_hospital = models.ForeignKey(
    Hospital,
    related_name="to_requests",
    on_delete=models.CASCADE,
    null=True,
    blank=True
    )

    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)

    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)