"""
URL configuration for carelith project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import post_login_redirect
from django.http import HttpResponse
from .views import home, post_login_redirect

def home(request):
    return HttpResponse("Carelith server is running successfully 🚀")


urlpatterns = [
    path('', home, name='home'),   # ✅ ROOT URL FIX

    path('admin/', admin.site.urls),
    path('redirect/', post_login_redirect, name='post_login_redirect'),

    path('patients/', include('patients.urls')),
    path('doctor/', include('doctor_app.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('lab/', include('laboratory.urls')),
    path('records/', include('records.urls')),
    # path('access/', include('access_control.urls')),
    path('fhir/', include('fhir.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )