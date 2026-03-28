from django.db import models
from django.contrib.auth.models import User
from hospital_app.models import Hospital

class Receptionist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True)
    contact_number = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"Receptionist: {self.user.username}"