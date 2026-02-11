from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Encounter, Prescription, Report


def get_or_create_encounter(patient, doctor=None):
    encounter = Encounter.objects.filter(
        patient=patient,
        doctor=doctor
    ).order_by('-started_at').first()

    if not encounter:
        encounter = Encounter.objects.create(
            patient=patient,
            doctor=doctor
        )

    return encounter


@receiver(post_save, sender=Prescription)
def attach_encounter_to_prescription(sender, instance, created, **kwargs):
    if created and instance.encounter is None:
        encounter = get_or_create_encounter(
            patient=instance.doctor.patient_profile,
            doctor=instance.doctor
        )
        instance.encounter = encounter
        instance.save()


@receiver(post_save, sender=Report)
def attach_encounter_to_report(sender, instance, created, **kwargs):
    if created and instance.encounter is None:
        encounter = get_or_create_encounter(
            patient=instance.patient,
            doctor=instance.doctor
        )
        instance.encounter = encounter
        instance.save()