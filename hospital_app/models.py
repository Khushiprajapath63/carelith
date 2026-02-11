from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length=200)

    city = models.CharField(max_length=100, default="Unknown")
    state = models.CharField(max_length=100, default="Unknown")

    registration_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name
