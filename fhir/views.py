from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone

from patients.models import Patient
from records.models import Encounter, Observation


# ─────────────────────────────────────────
# Helper: Fetch DocumentReference from FHIR server
# ─────────────────────────────────────────

def get_document_references(fhir_patient_id):
    import requests
    from django.conf import settings

    try:
        url = f"{settings.FHIR_SERVER_URL}/DocumentReference?patient={fhir_patient_id}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            return response.json()

        return {}

    except Exception as e:
        print(f"[FHIR ERROR] get_document_references: {e}")
        return {}


# ─────────────────────────────────────────
# FHIR Patient
# ─────────────────────────────────────────

def fhir_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)

    data = {
        "resourceType": "Patient",
        "id": str(patient.id),
        "name": [{
            "use": "official",
            "text": str(patient),
        }],
        "gender": getattr(patient, "gender", "unknown"),
        "birthDate": str(patient.date_of_birth) if getattr(patient, "date_of_birth", None) else None,
    }

    return JsonResponse(data)


# ─────────────────────────────────────────
# FHIR Encounter
# ─────────────────────────────────────────

def fhir_encounter(request):
    patient_id = request.GET.get("patient")

    if patient_id:
        encounters = Encounter.objects.filter(patient_id=patient_id)
    else:
        encounters = Encounter.objects.all()

    entries = []

    for enc in encounters:
        entries.append({
            "resource": {
                "resourceType": "Encounter",
                "id": str(enc.id),
                "status": "finished",
                "subject": {"reference": f"Patient/{enc.patient_id}"},
                "period": {
                    "start": str(enc.started_at) if enc.started_at else None,
                },
                "reasonCode": [{
                    "text": enc.reason
                }]
            }
        })

    return JsonResponse({
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(entries),
        "entry": entries
    })


# ─────────────────────────────────────────
# FHIR Observation
# ─────────────────────────────────────────

def fhir_observation(request):
    patient_id = request.GET.get("patient")

    if patient_id:
        observations = Observation.objects.filter(encounter__patient_id=patient_id)
    else:
        observations = Observation.objects.all()

    entries = []

    for obs in observations:
        entries.append({
            "resource": {
                "resourceType": "Observation",
                "id": str(obs.id),
                "status": "final",
                "subject": {"reference": f"Patient/{obs.encounter.patient_id}"},
                "code": {
                    "text": obs.code
                },
                "valueString": str(obs.value),
                "effectiveDateTime": str(obs.recorded_at)
            }
        })

    return JsonResponse({
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(entries),
        "entry": entries
    })


# ─────────────────────────────────────────
# Build Records From FHIR Data
# ─────────────────────────────────────────

def _build_records(fhir_data, username=None):

    all_records = []
    my_records = []
    other_records = []

    if not fhir_data or "entry" not in fhir_data:
        return all_records, my_records, other_records

    for entry in fhir_data["entry"]:

        resource = entry.get("resource", {})
        description = resource.get("description", "Medical Report")

        # Author
        author_name = "Unknown"
        if resource.get("author"):
            author_name = resource["author"][0].get("display", "Unknown")

        # File
        file_url = None
        content_type = "N/A"

        if resource.get("content"):
            attachment = resource["content"][0].get("attachment", {})
            file_url = attachment.get("url")
            content_type = attachment.get("contentType", "N/A")

        # Category detection
        category = "Document"

        if "lab" in description.lower() or "blood" in description.lower():
            category = "Lab"

        elif "mri" in description.lower() or "xray" in description.lower():
            category = "Radiology"

        # Ownership
        is_mine = False
        if username and author_name == username:
            is_mine = True

        record = {
            "description": description,
            "author_name": author_name,
            "content_type": content_type,
            "file_url": file_url,
            "category": category,
            "is_mine": is_mine
        }

        all_records.append(record)

        if is_mine:
            my_records.append(record)
        else:
            other_records.append(record)

    return all_records, my_records, other_records


# ─────────────────────────────────────────
# Doctor View FHIR Records (OTP Protected)
# ─────────────────────────────────────────

@login_required
def view_patient_fhir_records(request, patient_id):

    from doctor_app.models import Doctor
    from access_control.models import PatientAccess

    doctor = get_object_or_404(Doctor, user=request.user)

    access = PatientAccess.objects.filter(
        doctor=doctor,
        patient_id=patient_id,
        is_verified=True,
        expires_at__gt=timezone.now()
    ).first()

    if not access:
        messages.error(request, "OTP verification required before viewing FHIR records.")
        return redirect("doctor_app:doctor_dashboard")

    patient = get_object_or_404(Patient, id=patient_id)

    all_records = []
    my_records = []
    other_records = []

    if patient.fhir_patient_id:
        try:
            fhir_data = get_document_references(patient.fhir_patient_id)

            all_records, my_records, other_records = _build_records(
                fhir_data,
                doctor.user.username
            )

        except Exception as e:
            print(f"[FHIR ERROR] view_patient_fhir_records: {e}")
            messages.error(request, "Could not fetch FHIR records.")

    return render(request, "doctor_app/fhir_records.html", {
        "patient": patient,
        "doctor": doctor,
        "all_records": all_records,
        "my_records": my_records,
        "other_records": other_records,
        "current_time": timezone.now()
    })


# ─────────────────────────────────────────
# Patient View FHIR Records
# ─────────────────────────────────────────

@login_required
def patient_view_fhir_records(request, patient_id):

    patient = get_object_or_404(Patient, id=patient_id)

    if patient.user != request.user:
        messages.error(request, "You are not authorized to view these records.")
        return redirect("patient_dashboard")

    all_records = []
    my_records = []
    other_records = []

    if patient.fhir_patient_id:

        try:
            fhir_data = get_document_references(patient.fhir_patient_id)
            all_records, my_records, other_records = _build_records(fhir_data)

        except Exception as e:
            print(f"[FHIR ERROR] patient_view_fhir_records: {e}")
            messages.error(request, "Could not fetch FHIR records.")

    return render(request, "doctor_app/fhir_records.html", {
        "patient": patient,
        "doctor": None,
        "all_records": all_records,
        "my_records": my_records,
        "other_records": other_records,
        "current_time": timezone.now()
    })