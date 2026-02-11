from django.urls import path
from .views import patient_dashboard, secure_patient_view

urlpatterns = [
    path('dashboard/', patient_dashboard, name='patient_dashboard'),
    path('secure/<int:access_id>/', secure_patient_view, name='secure_patient_view'),
]