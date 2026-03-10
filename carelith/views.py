from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from doctor_app.models import Doctor
from patients.models import Patient


def home(request):
    return render(request, "home.html")


def post_login_redirect(request):
    user = request.user

    if user.is_superuser:
        return redirect('/admin/')

    if Doctor.objects.filter(user=user).exists():
        return redirect('/doctor/dashboard/')

    if Patient.objects.filter(user=user).exists():
        return redirect('/patients/dashboard/')

    # fallback safety
    return redirect('/accounts/login/')