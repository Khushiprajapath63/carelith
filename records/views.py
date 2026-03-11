from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Report
from records.models import AuditLog
from doctor_app.models import Doctor
from notifications.models import Notification


# =========================
# Get Client IP Address
# =========================
def get_client_ip(request):

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")

    return ip


# =========================
# Explain Report
# =========================
@login_required
def explain_report(request, report_id):

    report = get_object_or_404(Report, id=report_id)

    # ensure only doctors access
    doctor = get_object_or_404(Doctor, user=request.user)

    # ⭐ Log when doctor views the report page
    AuditLog.objects.create(
        doctor=doctor,
        patient=report.patient,
        report=report,
        action="Viewed Patient Report",
        ip_address=get_client_ip(request)
    )

    if request.method == "POST":

        report.doctor_notes = request.POST.get("doctor_notes")
        report.doctor = doctor
        report.status = "explained"
        report.save()

        # ⭐ Log explanation action
        AuditLog.objects.create(
            doctor=doctor,
            patient=report.patient,
            report=report,
            action="Explained Patient Report",
            ip_address=get_client_ip(request)
        )

        # 🔔 Notify patient
        Notification.objects.create(
            user=report.patient.user,
            message=f"Doctor has explained your report: {report.title}"
        )

        return redirect("doctor_dashboard")

    return render(
        request,
        "doctor_app/explain_report.html",
        {"report": report}
    )