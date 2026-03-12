from django.shortcuts import render
from doctor_app.models import Doctor
from patients.models import Patient

@login_required
def redirect_user(request):

    if Doctor.objects.filter(user=request.user).exists():
        return redirect("doctor_app:doctor_dashboard")

    elif Patient.objects.filter(user=request.user).exists():
        return redirect("patients:patient_dashboard")

    else:
        return redirect("login")