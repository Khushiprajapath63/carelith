import random
import os
from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

from .models import Doctor
from records.models import Encounter, Report, Prescription
from patients.models import Patient
from access_control.models import PatientAccess

from fhir.utils import (
    get_document_references,
    upload_document_reference,
    check_patient_exists,
    create_fhir_patient
)


# ============================================================
# DOCTOR DASHBOARD
# ============================================================
@login_required
def doctor_dashboard(request):

    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, "No Doctor profile found.")
        return redirect("login")

    # appointments
    appointments = Encounter.objects.filter(
        doctor=doctor
    ).order_by("-started_at")

    # verified patients
    verified_patients = PatientAccess.objects.filter(
        doctor=doctor,
        is_verified=True,
        expires_at__gt=timezone.now()
    ).values_list("patient_id", flat=True)

    # reports
    reports = Report.objects.select_related("patient").filter(
        patient_id__in=verified_patients
    )

    # prescriptions
    prescriptions = Prescription.objects.filter(
        encounter__patient_id__in=verified_patients
    )

    # ALL PATIENTS (for dashboard list)
    all_patients = Patient.objects.all()

    # patients doctor has access to
    patients = Patient.objects.filter(id__in=verified_patients)

    # ========================================================
    # FHIR REPORT FETCH
    # ========================================================
    fhir_reports = []

    for p in patients:

        if not p.fhir_patient_id:
            continue

        try:
            data = get_document_references(p.fhir_patient_id)

            if not data or "entry" not in data:
                continue

            filtered_entries = []

            for entry in data["entry"]:

                resource = entry.get("resource", {})
                description = resource.get("description", "")
                authors = resource.get("author", [])

                is_current_doctor_report = False

                for author in authors:
                    display = author.get("display", "")

                    if doctor.user.username in display or doctor.user.get_full_name() in display:
                        is_current_doctor_report = True
                        break

                if not is_current_doctor_report:
                    if doctor.user.username.lower() in description.lower():
                        is_current_doctor_report = True

                if is_current_doctor_report:
                    filtered_entries.append(entry)

            if filtered_entries:
                fhir_reports.append({
                    "patient": p,
                    "reports": filtered_entries
                })

        except Exception as e:
            print(f"[FHIR ERROR] {e}")
            continue

    return render(request, "doctor_app/dashboard.html", {
        "doctor": doctor,
        "appointments": appointments,
        "reports": reports,
        "prescriptions": prescriptions,
        "fhir_reports": fhir_reports,
        "patients": all_patients,
        "current_time": timezone.now(),
    })


# ============================================================
# EXPLAIN REPORT
# ============================================================
@login_required
def explain_report(request, report_id):

    doctor = get_object_or_404(Doctor, user=request.user)
    report = get_object_or_404(Report, id=report_id)

    if request.method == "POST":

        report.doctor = doctor
        report.doctor_notes = request.POST.get("doctor_notes")
        report.status = "explained"
        report.save()

        messages.success(request, "Report explained successfully!")
        return redirect("doctor_app:doctor_dashboard")

    return render(request, "doctor_app/explain_report.html", {
        "report": report
    })


# ============================================================
# REQUEST PATIENT ACCESS (OTP)
# ============================================================
@login_required
def request_patient_access(request, patient_id):

    doctor = get_object_or_404(Doctor, user=request.user)
    patient = get_object_or_404(Patient, id=patient_id)

    otp = str(random.randint(100000, 999999))
    expiry_time = timezone.now() + timedelta(minutes=10)

    PatientAccess.objects.filter(
        doctor=doctor,
        patient=patient
    ).delete()

    access_obj = PatientAccess.objects.create(
        doctor=doctor,
        patient=patient,
        otp=otp,
        is_verified=False,
        expires_at=expiry_time
    )

    # Demo OTP display
    print("OTP GENERATED:", otp)

    messages.success(request, f"OTP for demo: {otp}")

    return redirect("doctor_app:verify_patient_otp", access_id=access_obj.id)

# ============================================================
# VERIFY OTP
# ============================================================
@login_required
def verify_patient_otp(request, access_id):

    access = get_object_or_404(PatientAccess, id=access_id)

    if request.method == "POST":

        entered_otp = request.POST.get("otp")

        if timezone.now() > access.expires_at:
            messages.error(request, "OTP expired.")
            return redirect("doctor_app:doctor_dashboard")

        if entered_otp == access.otp:

            access.is_verified = True
            access.save()

            messages.success(request, "OTP verified!")
            return redirect("doctor_app:doctor_dashboard")

        else:
            messages.error(request, "Invalid OTP.")

    return render(request, "doctor_app/verify_otp.html", {
        "access": access
    })


# ============================================================
# VIEW FHIR RECORDS
# ============================================================
@login_required
def view_patient_fhir_records(request, patient_id):

    doctor = get_object_or_404(Doctor, user=request.user)

    access = PatientAccess.objects.filter(
        doctor=doctor,
        patient_id=patient_id,
        is_verified=True,
        expires_at__gt=timezone.now()
    ).first()

    if not access:
        messages.error(request, "OTP verification required.")
        return redirect("doctor_app:doctor_dashboard")

    patient = get_object_or_404(Patient, id=patient_id)

    fhir_data = None

    if patient.fhir_patient_id:

        try:
            fhir_data = get_document_references(patient.fhir_patient_id)

        except Exception as e:
            print(f"[FHIR ERROR] {e}")
            messages.error(request, "FHIR fetch failed.")

    return render(request, "doctor_app/fhir_records.html", {
        "patient": patient,
        "fhir_data": fhir_data,
        "doctor": doctor,
        "current_time": timezone.now(),
    })


# ============================================================
# UPLOAD REPORT TO FHIR
# ============================================================
@login_required
def upload_patient_report_to_fhir(request, patient_id):

    doctor = get_object_or_404(Doctor, user=request.user)

    access = PatientAccess.objects.filter(
        doctor=doctor,
        patient_id=patient_id,
        is_verified=True,
        expires_at__gt=timezone.now()
    ).first()

    if not access:
        messages.error(request, "OTP verification required.")
        return redirect("doctor_app:doctor_dashboard")

    patient = get_object_or_404(Patient, id=patient_id)

    if not patient.fhir_patient_id or not check_patient_exists(patient.fhir_patient_id):

        new_fhir_id = create_fhir_patient(
            patient.user.username,
            patient.id
        )

        if not new_fhir_id:
            messages.error(request, "FHIR Patient creation failed.")
            return redirect(
                "doctor_app:view_patient_fhir_records",
                patient_id=patient.id
            )

        patient.fhir_patient_id = new_fhir_id
        patient.save()

    if request.method == "POST":

        report_file = request.FILES.get("report")

        if not report_file:
            messages.error(request, "No file selected.")
            return redirect(
                "doctor_app:view_patient_fhir_records",
                patient_id=patient.id
            )

        upload_dir = os.path.join(settings.MEDIA_ROOT, "temp_reports")
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, report_file.name)

        with open(file_path, "wb+") as destination:
            for chunk in report_file.chunks():
                destination.write(chunk)

        description_text = f"Report uploaded by Dr. {doctor.user.username}"

        status, text = upload_document_reference(
            patient.fhir_patient_id,
            file_path,
            description_text
        )

        if os.path.exists(file_path):
            os.remove(file_path)

        if status in [200, 201]:
            messages.success(request, "Report uploaded successfully!")
        else:
            messages.error(request, f"FHIR upload failed: {text}")

    return redirect(
        "doctor_app:view_patient_fhir_records",
        patient_id=patient.id
    )