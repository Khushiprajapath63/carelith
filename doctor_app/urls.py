from django.urls import path
from . import views

app_name = "doctor_app"

urlpatterns = [
    path(
        "dashboard/",
        views.doctor_dashboard,
        name="doctor_dashboard"
    ),

    path(
        "report/<int:report_id>/explain/",
        views.explain_report,
        name="explain_report"
    ),

    path(
        "request-access/<int:patient_id>/",
        views.request_patient_access,
        name="request_patient_access"
    ),

    path(
        "verify-otp/<int:access_id>/",
        views.verify_patient_otp,
        name="verify_patient_otp"
    ),
]
