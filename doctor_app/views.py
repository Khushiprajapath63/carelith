import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Doctor
from records.models import Report, Prescription
from patients.models import Appointment
from access_control.models import PatientAccess


@login_required
def doctor_dashboard(request):
    doctor = get_object_or_404(Doctor, user=request.user)

    appointments = Appointment.objects.filter(
        doctor=doctor
    ).order_by("-date")

    reports = Report.objects.select_related(
        "patient"
    ).order_by("-created_at")

    prescriptions = Prescription.objects.filter(
        doctor=doctor
    )

    return render(request, "doctor_app/dashboard.html", {
        "doctor": doctor,
        "appointments": appointments,
        "reports": reports,
        "prescriptions": prescriptions,
    })


# ✅ THIS WAS MISSING — NOW ADDED
@login_required
def explain_report(request, report_id):
    doctor = get_object_or_404(Doctor, user=request.user)
    report = get_object_or_404(Report, id=report_id)

    if request.method == "POST":
        report.status = "explained"
        report.doctor = doctor
        report.save()
        messages.success(request, "Report explained successfully.")
        return redirect("doctor_dashboard")

    return render(request, "doctor_app/explain_report.html", {
        "report": report
    })


@login_required
def request_patient_access(request, patient_id):
    doctor = get_object_or_404(Doctor, user=request.user)

    otp = str(random.randint(100000, 999999))

    access = PatientAccess.objects.create(
        patient_id=patient_id,
        doctor=doctor,
        otp=otp,
        expires_at=timezone.now() + timezone.timedelta(minutes=10)
    )

    print("========== OTP ==========")
    print("Doctor:", doctor.user.username)
    print("OTP:", otp)
    print("=========================")

    messages.success(request, "OTP generated. Check server console.")
    return redirect("verify_patient_otp", access_id=access.id)


@login_required
def verify_patient_otp(request, access_id):
    access = get_object_or_404(PatientAccess, id=access_id)

    if access.is_expired():
        messages.error(request, "OTP expired.")
        return redirect("doctor_dashboard")

    if request.method == "POST":
        if request.POST.get("otp") == access.otp:
            access.is_verified = True
            access.save()
            messages.success(request, "Access granted.")
            return redirect("doctor_dashboard")
        else:
            messages.error(request, "Invalid OTP.")

    return render(request, "doctor_app/verify_otp.html", {
        "access": access
    })
