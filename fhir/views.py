from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone
from patients.models import Patient
from records.models import Encounter, Observation


# ─── Helper ───────────────────────────────────────────────────────────────────

def get_document_references(fhir_patient_id):
    import requests
    from django.conf import settings
    try:
        url = f"{settings.FHIR_SERVER_URL}/DocumentReference?patient={fhir_patient_id}"
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        print(f"[FHIR ERROR] get_document_references: {e}")
        return {}


# ─── FHIR Patient ─────────────────────────────────────────────────────────────

def fhir_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    data = {
        "resourceType": "Patient",
        "id": str(patient.id),
        "name": [
            {
                "use": "official",
                "text": f"{patient.first_name} {patient.last_name}" if hasattr(patient, 'first_name') else str(patient),
            }
        ],
        "gender": getattr(patient, 'gender', 'unknown'),
        "birthDate": str(patient.date_of_birth) if hasattr(patient, 'date_of_birth') and patient.date_of_birth else None,
        "telecom": [
            {"system": "phone", "value": str(patient.phone)} if hasattr(patient, 'phone') and patient.phone else {}
        ],
    }
    return JsonResponse(data)


# ─── FHIR Encounter ───────────────────────────────────────────────────────────

def fhir_encounter(request):
    patient_id = request.GET.get('patient')
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
                "status": getattr(enc, 'status', 'finished'),
                "subject": {"reference": f"Patient/{enc.patient_id}"},
                "period": {
                    "start": str(enc.date) if hasattr(enc, 'date') and enc.date else None,
                },
                "reasonCode": [{"text": getattr(enc, 'reason', '')}],
            }
        })

    return JsonResponse({
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(entries),
        "entry": entries,
    })


# ─── FHIR Observation ─────────────────────────────────────────────────────────

def fhir_observation(request):
    patient_id = request.GET.get('patient')
    if patient_id:
        observations = Observation.objects.filter(patient_id=patient_id)
    else:
        observations = Observation.objects.all()

    entries = []
    for obs in observations:
        entries.append({
            "resource": {
                "resourceType": "Observation",
                "id": str(obs.id),
                "status": getattr(obs, 'status', 'final'),
                "subject": {"reference": f"Patient/{obs.patient_id}"},
                "code": {
                    "text": getattr(obs, 'observation_type', getattr(obs, 'code', 'Unknown')),
                },
                "valueString": str(getattr(obs, 'value', '')),
                "effectiveDateTime": str(obs.date) if hasattr(obs, 'date') and obs.date else None,
            }
        })

    return JsonResponse({
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(entries),
        "entry": entries,
    })


# ─── FHIR Medical History ─────────────────────────────────────────────────────

def fhir_medical_history(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    encounters = Encounter.objects.filter(patient=patient)
    observations = Observation.objects.filter(patient=patient)

    encounter_entries = []
    for enc in encounters:
        encounter_entries.append({
            "resource": {
                "resourceType": "Encounter",
                "id": str(enc.id),
                "status": getattr(enc, 'status', 'finished'),
                "subject": {"reference": f"Patient/{patient_id}"},
                "period": {
                    "start": str(enc.date) if hasattr(enc, 'date') and enc.date else None,
                },
                "reasonCode": [{"text": getattr(enc, 'reason', '')}],
            }
        })

    observation_entries = []
    for obs in observations:
        observation_entries.append({
            "resource": {
                "resourceType": "Observation",
                "id": str(obs.id),
                "status": getattr(obs, 'status', 'final'),
                "subject": {"reference": f"Patient/{patient_id}"},
                "code": {
                    "text": getattr(obs, 'observation_type', getattr(obs, 'code', 'Unknown')),
                },
                "valueString": str(getattr(obs, 'value', '')),
                "effectiveDateTime": str(obs.date) if hasattr(obs, 'date') and obs.date else None,
            }
        })

    return JsonResponse({
        "resourceType": "Bundle",
        "type": "searchset",
        "patient": {
            "reference": f"Patient/{patient_id}",
            "display": str(patient),
        },
        "total": len(encounter_entries) + len(observation_entries),
        "entry": encounter_entries + observation_entries,
    })


# ─── Shared helper to build records list from FHIR data ───────────────────────

def _build_records(fhir_data, username=None):
    all_records, my_records, other_records = [], [], []

    if fhir_data and "entry" in fhir_data:
        for entry in fhir_data["entry"]:
            resource = entry.get("resource", {})
            description = resource.get("description", "Medical Report")

            author_name = "Unknown"
            hospital_name = "Unknown Hospital"
            if "uploaded by Dr." in description:
                try:
                    after = description.split("uploaded by Dr.")[1].strip()
                    if "(" in after and ")" in after:
                        author_name = after.split("(")[0].strip()
                        hospital_name = after.split("(")[1].replace(")", "").strip()
                    else:
                        author_name = after.strip()
                except Exception:
                    pass
            elif resource.get("author"):
                author_name = resource["author"][0].get("display", "Unknown")

            file_url = None
            content_type = "N/A"
            if resource.get("content"):
                attachment = resource["content"][0].get("attachment", {})
                file_url = attachment.get("url")
                content_type = attachment.get("contentType", "N/A")
                if not file_url and attachment.get("data"):
                    try:
                        from fhir.utils import save_fhir_attachment_locally
                        file_url = save_fhir_attachment_locally(entry)
                    except Exception:
                        pass

            is_mine = bool(username and (username in description or username == author_name))

            rec = {
                "description": description,
                "author_name": author_name,
                "hospital_name": hospital_name,
                "content_type": content_type,
                "file_url": file_url,
                "is_mine": is_mine,
            }
            all_records.append(rec)
            (my_records if is_mine else other_records).append(rec)

    return all_records, my_records, other_records


# ─── View Patient FHIR Records (Doctor UI — OTP protected) ───────────────────

@login_required
def view_patient_fhir_records(request, patient_id):
    from doctor_app.models import Doctor
    from access_control.models import PatientAccess  # ✅ Fixed import

    try:
        from fhir.utils import get_document_references as _get_doc_refs
        _fetch = _get_doc_refs
    except ImportError:
        _fetch = get_document_references

    doctor = get_object_or_404(Doctor, user=request.user)

    access = PatientAccess.objects.filter(
        doctor=doctor, patient_id=patient_id,
        is_verified=True, expires_at__gt=timezone.now()
    ).first()

    if not access:
        messages.error(request, "OTP verification required before viewing FHIR records!")
        return redirect("doctor_app:doctor_dashboard")

    patient = get_object_or_404(Patient, id=patient_id)

    qualifications = []
    if hasattr(doctor, 'qualification') and doctor.qualification:
        qualifications = [q.strip() for q in doctor.qualification.split(",") if q.strip()]

    all_records, my_records, other_records = [], [], []

    if patient.fhir_patient_id:
        try:
            fhir_data = _fetch(patient.fhir_patient_id)
            all_records, my_records, other_records = _build_records(fhir_data, doctor.user.username)
        except Exception as e:
            print(f"[FHIR ERROR] view_patient_fhir_records: {e}")
            messages.error(request, "Could not fetch FHIR records at this time.")

    return render(request, "doctor_app/fhir_records.html", {
        "patient": patient,
        "doctor": doctor,
        "qualifications": qualifications,
        "all_records": all_records,
        "my_records": my_records,
        "other_records": other_records,
        "current_time": timezone.now(),
    })


# ─── View Patient FHIR Records (Patient UI — no OTP needed) ──────────────────

@login_required
def patient_view_fhir_records(request, patient_id):
    """Patient apne khud ke FHIR records dekh sakta hai — no OTP needed."""

    patient = get_object_or_404(Patient, id=patient_id)

    # Sirf apne records dekh sakta hai
    if patient.user != request.user:
        messages.error(request, "You are not authorized to view these records.")
        return redirect("patient_dashboard")

    try:
        from fhir.utils import get_document_references as _get_doc_refs
        _fetch = _get_doc_refs
    except ImportError:
        _fetch = get_document_references

    all_records, my_records, other_records = [], [], []

    if patient.fhir_patient_id:
        try:
            fhir_data = _fetch(patient.fhir_patient_id)
            all_records, my_records, other_records = _build_records(fhir_data)
        except Exception as e:
            print(f"[FHIR ERROR] patient_view_fhir_records: {e}")
            messages.error(request, "Could not fetch FHIR records at this time.")

    return render(request, "doctor_app/fhir_records.html", {
        "patient": patient,
        "doctor": None,
        "qualifications": [],
        "all_records": all_records,
        "my_records": my_records,
        "other_records": other_records,
        "current_time": timezone.now(),
    })