from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # 🔥 FHIR Link
    fhir_organization_id = models.CharField(max_length=200, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name