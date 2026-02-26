from django.urls import path
from . import views

app_name = "doctor_app"

urlpatterns = [
    path("dashboard/", views.doctor_dashboard, name="doctor_dashboard"),
    path("report/<int:report_id>/explain/", views.explain_report, name="explain_report"),

    path("patient/<int:patient_id>/request-access/", views.request_patient_access, name="request_patient_access"),
    path("verify-otp/<int:access_id>/", views.verify_patient_otp, name="verify_patient_otp"),

    # ✅ FHIR URLs
    path("patient/<int:patient_id>/fhir-records/", views.view_patient_fhir_records, name="view_patient_fhir_records"),
    path("patient/<int:patient_id>/upload-fhir-report/", views.upload_patient_report_to_fhir, name="upload_patient_report_to_fhir"),
]