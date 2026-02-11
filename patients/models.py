from django.db import models
from django.contrib.auth.models import User


class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile'
    )

    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='M'
    )

    age = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        help_text="Patient registered mobile number (for OTP)"
    )

    def __str__(self):
        return self.user.username


class Appointment(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    doctor = models.ForeignKey(
        'doctor_app.Doctor',
        on_delete=models.CASCADE,
        related_name='appointments'
    )

    date = models.DateField()
    time = models.TimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.user.username} → {self.doctor.user.username} ({self.date})"
