from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Laboratory
from records.models import Report
from patients.models import Patient


@login_required
def lab_dashboard(request):
    try:
        lab = Laboratory.objects.get(user=request.user)
    except Laboratory.DoesNotExist:
        messages.error(request, "No laboratory profile found.")
        return redirect('/accounts/login/')

    reports = Report.objects.filter(laboratory=lab).select_related('patient').order_by('-uploaded_at')
    patients = Patient.objects.all().select_related('user')

    if request.method == "POST":
        patient_id = request.POST.get("patient")
        title = request.POST.get("title")
        file = request.FILES.get("file")

        if not patient_id or not title or not file:
            messages.error(request, "All fields are required.")
        else:
            try:
                patient = Patient.objects.get(id=patient_id)
                Report.objects.create(
                    patient=patient,
                    laboratory=lab,
                    title=title,
                    file=file,
                    status="pending"
                )
                messages.success(request, f"Report '{title}' uploaded successfully!")
                return redirect('lab_dashboard')
            except Patient.DoesNotExist:
                messages.error(request, "Invalid patient selected.")

    return render(request, 'laboratory/dashboard.html', {
        'lab': lab,
        'patients': patients,
        'reports': reports,
        'total_reports': reports.count(),
        'pending_reports': reports.filter(status='pending').count(),
        'explained_reports': reports.filter(status='explained').count(),
    })