from django.db import models
from django.contrib.auth.models import User
from hospital_app.models import Hospital

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    qualification = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username



