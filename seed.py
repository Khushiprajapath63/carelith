import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carelith.settings')
django.setup()

from doctor_app.models import Doctor
from hospital_app.models import Hospital
from django.contrib.auth.models import User

data = [
    ("Anil_Kumar_R", "Cardiology", "MBBS, MD, DM Cardiology", "9123456780", "Apollo Hospitals"),
    ("Priya_Sharma", "Dermatology", "MBBS, MD Dermatology", "9876543210", "Fortis Hospital"),
    ("Rahul_Verma", "Neurology", "MBBS, MD, DM Neurology", "9012345678", "AIIMS Delhi"),
    ("Sneha_Reddy", "Pediatrics", "MBBS, MD Pediatrics", "9988776655", "Rainbow Children's Hospital"),
    ("Karthik_Iyer", "Orthopaedics", "MBBS, MS Orthopaedics", "9090909090", "Manipal Hospital"),
    ("Meera_Nair", "Gynecology", "MBBS, MD Obstetrics & Gynecology", "9812345678", "Cloudnine Hospital"),
    ("Arjun_Patel", "General Surgery", "MBBS, MS General Surgery", "9765432109", "Sterling Hospital"),
    ("Neha_Gupta", "Ophthalmology", "MBBS, MS Ophthalmology", "9345678123", "Sankara Eye Hospital"),
    ("Vikram_Singh", "ENT", "MBBS, MS ENT", "9234567812", "Max Healthcare"),
    ("Pooja_Menon", "Psychiatry", "MBBS, MD Psychiatry", "9456123789", "NIMHANS"),
]

for username, spec, qual, contact, hospital_name in data:
    user, _ = User.objects.get_or_create(username=username)
    hospital, _ = Hospital.objects.get_or_create(name=hospital_name)
    doctor, created = Doctor.objects.get_or_create(
        user=user,
        defaults={
            "specialization": spec,
            "qualification": qual,
            "contact_number": contact,
            "hospital": hospital
        }
    )
    print(f"{'Created' if created else 'Exists'}: Dr. {username}")

print("Done!")