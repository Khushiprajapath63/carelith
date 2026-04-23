import random
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import Receptionist
from doctor_app.models import Doctor
from patients.models import Patient
from hospital_app.models import Hospital
from records.models import Encounter
from access_control.models import PatientAccess


# ============================================================
# RECEPTIONIST DASHBOARD
# ============================================================
@login_required
def receptionist_dashboard(request):
    try:
        receptionist = Receptionist.objects.get(user=request.user)
    except Receptionist.DoesNotExist:
        messages.error(request, "No receptionist profile found.")
        return redirect('/accounts/login/')

    doctors = Doctor.objects.all().select_related('user', 'hospital')
    patients = Patient.objects.all().select_related('user', 'hospital')
    appointments = Encounter.objects.all().order_by('-started_at')[:20]

    return render(request, 'receptionist/dashboard.html', {
        'receptionist': receptionist,
        'doctors': doctors,
        'patients': patients,
        'appointments': appointments,
        'current_time': timezone.now(),
        'total_doctors': doctors.count(),
        'total_patients': patients.count(),
        'total_appointments': Encounter.objects.count(),
    })


# ============================================================
# REGISTER PATIENT
# ============================================================
@login_required
def register_patient(request):
    try:
        receptionist = Receptionist.objects.get(user=request.user)
    except Receptionist.DoesNotExist:
        return redirect('/accounts/login/')

    hospitals = Hospital.objects.all()

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        age = request.POST.get('age', '').strip()
        gender = request.POST.get('gender', '').strip()
        hospital_id = request.POST.get('hospital', '').strip()

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'receptionist/register_patient.html', {'hospitals': hospitals, 'receptionist': receptionist})

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists.")
            return render(request, 'receptionist/register_patient.html', {'hospitals': hospitals, 'receptionist': receptionist})

        user = User.objects.create_user(username=username, email=email, password=password)
        hospital = Hospital.objects.filter(id=hospital_id).first()

        Patient.objects.create(
            user=user,
            age=age if age else None,
            gender=gender,
            hospital=hospital,
        )

        messages.success(request, f"Patient '{username}' registered successfully!")
        return redirect('receptionist:receptionist_dashboard')

    return render(request, 'receptionist/register_patient.html', {
        'hospitals': hospitals,
        'receptionist': receptionist,
    })


# =============