import random
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone

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


# ============================================================
# BOOK APPOINTMENT
# ============================================================
@login_required
def book_appointment(request):
    try:
        receptionist = Receptionist.objects.get(user=request.user)
    except Receptionist.DoesNotExist:
        return redirect('/accounts/login/')

    doctors = Doctor.objects.all().select_related('user', 'hospital')
    patients = Patient.objects.all().select_related('user')

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        patient_id = request.POST.get('patient')
        reason = request.POST.get('reason', 'General Consultation')
        date = request.POST.get('date')

        doctor = get_object_or_404(Doctor, id=doctor_id)
        patient = get_object_or_404(Patient, id=patient_id)

        Encounter.objects.create(
            doctor=doctor,
            patient=patient,
            reason=reason,
            started_at=date if date else timezone.now(),
            hospital=doctor.hospital,
        )

        messages.success(request, f"Appointment booked for {patient.user.username} with Dr. {doctor.user.username}!")
        return redirect('receptionist:receptionist_dashboard')

    return render(request, 'receptionist/book_appointment.html', {
        'doctors': doctors,
        'patients': patients,
        'receptionist': receptionist,
    })


# ============================================================
# GENERATE OTP
# ============================================================
@login_required
def generate_otp(request, patient_id):
    try:
        receptionist = Receptionist.objects.get(user=request.user)
    except Receptionist.DoesNotExist:
        return redirect('/accounts/login/')

    patient = get_object_or_404(Patient, id=patient_id)
    doctors = Doctor.objects.all().select_related('user')

    if request.method == 'POST':
        doctor_id = request.POST.get('doctor')
        doctor = get_object_or_404(Doctor, id=doctor_id)

        otp = str(random.randint(100000, 999999))
        expiry_time = timezone.now() + timedelta(minutes=10)

        PatientAccess.objects.filter(doctor=doctor, patient=patient).delete()

        access_obj = PatientAccess.objects.create(
            doctor=doctor,
            patient=patient,
            otp=otp,
            is_verified=False,
            expires_at=expiry_time,
        )

        messages.success(request, f"OTP generated: {otp} — Valid for 10 minutes.")
        return redirect('receptionist:receptionist_dashboard')

    return render(request, 'receptionist/generate_otp.html', {
        'patient': patient,
        'doctors': doctors,
        'receptionist': receptionist,
    })