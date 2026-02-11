from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Report
from doctor_app.models import Doctor
from notifications.models import Notification


@login_required
def explain_report(request, report_id):
    report = get_object_or_404(Report, id=report_id)

    # ensure only doctors can explain
    doctor = get_object_or_404(Doctor, user=request.user)

    if request.method == "POST":
        report.doctor_notes = request.POST.get("doctor_notes")
        report.doctor = doctor
        report.status = "explained"
        report.save()

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
