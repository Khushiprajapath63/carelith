from django.urls import path
from . import views

app_name = 'fhir'

urlpatterns = [
    path('Patient/<int:patient_id>/', views.fhir_patient, name='fhir_patient'),
    path('Encounter/', views.fhir_encounter, name='fhir_encounter'),
    path('Observation/', views.fhir_observation, name='fhir_observation'),
    path('medical-history/<int:patient_id>/', views.fhir_medical_history, name='fhir_medical_history'),
    path('records/<int:patient_id>/', views.view_patient_fhir_records, name='view_patient_fhir_records'),
    path('my-records/<int:patient_id>/', views.patient_view_fhir_records, name='patient_view_fhir_records'),  # ✅ Patient ke liye
]