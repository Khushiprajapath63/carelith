from django.http import JsonResponse
from patients.models import Patient
from records.models import Encounter
from records.models import Observation
from django.shortcuts import render

def fhir_patient(request, patient_id):
    patient = Patient.objects.get(id=patient_id)

    data = {
        "resourceType": "Patient",
        "id": patient.id,
        "name": [
            {
                "text": patient.user.get_full_name() or patient.user.username
            }
        ],
        "gender": patient.gender,
        "telecom": [
            {
                "system": "phone",
                "value": patient.phone_number
            }
        ]
    }

    return JsonResponse(data)


def fhir_encounter(request):
    encounters = Encounter.objects.all()
    bundle = []

    for e in encounters:
        bundle.append({
            "resourceType": "Encounter",
            "id": e.id,
            "status": "finished",
            "subject": {
                "reference": f"Patient/{e.patient.id}"
            },
            "period": {
                "start": e.started_at.isoformat(),
                "end": e.ended_at.isoformat() if e.ended_at else None
            }
        })

    return JsonResponse({
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": bundle
    })

def fhir_observation(request):
    observations = Observation.objects.all()
    bundle = []

    for o in observations:
        bundle.append({
            "resourceType": "Observation",
            "id": o.id,
            "status": "final",
            "code": {
                "text": o.code
            },
            "subject": {
                "reference": f"Patient/{o.encounter.patient.id}"
            },
            "encounter": {
                "reference": f"Encounter/{o.encounter.id}"
            },
            "valueQuantity": {
                "value": o.value,
                "unit": o.unit
            },
            "performer": [
                {
                    "display": o.doctor.user.username if o.doctor else "Unknown"
                }
            ],
            "effectiveDateTime": o.recorded_at.isoformat()
        })

    return JsonResponse({
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": bundle
    })    

def fhir_medical_history(request, patient_id):
    encounters = Encounter.objects.filter(
        patient_id=patient_id
    ).prefetch_related("observations", "hospital")

    return render(
        request,
        "fhir/medical_history.html",
        {"encounters": encounters}
    )
