from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Laboratory
from records.models import Report
from patients.models import Patient


@login_required
def lab_dashboard(request):
    # ✅ Ensure logged-in user is a Laboratory
    try:
        lab = Laboratory.objects.get(user=request.user)
    except Laboratory.DoesNotExist:
        return render(request, 'errors/not_a_laboratory.html')

    # ✅ Reports uploaded by this lab
    reports = Report.objects.filter(laboratory=lab)

    # ✅ Handle report upload
    if request.method == "POST":
        patient_id = request.POST.get("patient")
        title = request.POST.get("title")
        file = request.FILES.get("file")

        if patient_id and title and file:
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return render(request, 'laboratory/dashboard.html', {
                    'lab': lab,
                    'patients': Patient.objects.all(),
                    'reports': reports,
                    'error': 'Invalid patient selected'
                })

            Report.objects.create(
                patient=patient,
                laboratory=lab,
                title=title,
                file=file
            )

            return redirect('lab_dashboard')

    patients = Patient.objects.all()

    return render(request, 'laboratory/dashboard.html', {
        'lab': lab,
        'patients': patients,
        'reports': reports
    })
