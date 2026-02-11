from django.urls import path
from . import views

urlpatterns = [
    path('Patient/<int:patient_id>/', views.fhir_patient),
    path('Encounter/', views.fhir_encounter),
    path('Observation/', views.fhir_observation),
    path(
    'medical-history/<int:patient_id>/',
    views.fhir_medical_history,
    name='fhir_medical_history'
),
]
