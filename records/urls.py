from django.urls import path
from . import views

urlpatterns = [
    path('report/<int:report_id>/explain/', views.explain_report, name='explain_report'),
]
