from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Patient, Appointment
from records.models import Report, Prescription
from access_control.models import PatientAccess
from django.contrib import messages

@login_required
def patient_dashboard(request):
    """
    Patient main dashboard
    """
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return render(request, 'errors/not_a_patient.html')

    appointments = Appointment.objects.filter(
        patient=patient
    ).order_by('-date')

    reports = Report.objects.filter(
        patient=patient
    ).order_by('-id')

    prescriptions = Prescription.objects.filter(
        encounter__patient=patient
    ).order_by('-id')

    return render(request, 'patients/dashboard.html', {
        'patient': patient,
        'appointments': appointments,
        'reports': reports,
        'prescriptions': prescriptions,
    })


@login_required
def secure_patient_view(request, access_id):
    """
    Secure patient page (patient can view their granted access details)
    URL: /patients/secure/<access_id>/
    """

    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        return render(request, 'errors/not_a_patient.html')

    access = get_object_or_404(
        PatientAccess,
        id=access_id,
        patient=patient,
        is_verified=True,
        expires_at__gt=timezone.now()
    )

    return render(request, 'patients/secure_patient_page.html', {
        'patient': patient,
        'access': access
    })

@login_required
def patient_settings(request):
    try:
        patient = Patient.objects.get(user=request.user)
    except Patient.DoesNotExist:
        messages.error(request, "Patient profile not found.")
        return redirect("patients:patient_dashboard")

    if request.method == "POST":
        patient.age = request.POST.get("age")
        patient.gender = request.POST.get("gender")
        patient.save()
        messages.success(request, "Profile updated successfully")
        return redirect("patients:patient_settings")

    return render(request, "patients/settings.html", {
        "patient": patient
    })  