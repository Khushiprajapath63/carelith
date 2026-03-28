from django.urls import path
from . import views

app_name = 'receptionist'

urlpatterns = [
    path('dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('register-patient/', views.register_patient, name='register_patient'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('generate-otp/<int:patient_id>/', views.generate_otp, name='generate_otp'),
]