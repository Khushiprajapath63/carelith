import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carelith.settings')
django.setup()

from patients.models import Patient
from hospital_app.models import Hospital
from django.contrib.auth.models import User

data = [
    ("Rohan_Mehta", "male", 28, "Mazumdar Shaw Medical Center"),
    ("Priya_Nair", "female", 24, "Apollo Hospitals"),
    ("Arjun_Das", "male", 35, "Fortis Hospital"),
    ("Sneha_Pillai", "female", 22, "AIIMS Delhi"),
    ("Karan_Verma", "male", 45, "Manipal Hospital"),
    ("Anjali_Singh", "female", 31, "Cloudnine Hospital"),
    ("Vikram_Joshi", "male", 52, "Max Healthcare"),
    ("Deepa_Iyer", "female", 19, "Rainbow Children's Hospital"),
    ("Suresh_Kumar", "male", 60, "Sterling Hospital"),
    ("Neha_Sharma", "female", 27, "Sankara Eye Hospital"),
    ("Rahul_Gupta", "male", 38, "NIMHANS"),
    ("Meena_Reddy", "female", 33, "Apollo Hospitals"),
    ("Ajay_Patel", "male", 41, "Fortis Hospital"),
    ("Pooja_Krishnan", "female", 26, "Mazumdar Shaw Medical Center"),
    ("Sanjay_Rao", "male", 55, "AIIMS Delhi"),
    ("Lakshmi_Menon", "female", 29, "Manipal Hospital"),
    ("Amit_Shah", "male", 47, "Max Healthcare"),
    ("Divya_Nambiar", "female", 23, "Cloudnine Hospital"),
    ("Prasad_Kulkarni", "male", 39, "Sterling Hospital"),
    ("Kavitha_Bhat", "female", 32, "Apollo Hospitals"),
    ("Nikhil_Shetty", "male", 25, "Fortis Hospital"),
    ("Ramya_Hegde", "female", 36, "AIIMS Delhi"),
    ("Ganesh_Naidu", "male", 43, "Manipal Hospital"),
    ("Swathi_Rao", "female", 21, "Mazumdar Shaw Medical Center"),
    ("Vinod_Pillai", "male", 58, "Max Healthcare"),
    ("Hema_Subramanian", "female", 44, "Rainbow Children's Hospital"),
    ("Arun_Nair", "male", 30, "Sterling Hospital"),
    ("Shilpa_Jain", "female", 37, "Sankara Eye Hospital"),
    ("Manoj_Tiwari", "male", 49, "NIMHANS"),
    ("Anitha_Varghese", "female", 20, "Cloudnine Hospital"),
]

for username, gender, age, hospital_name in data:
    hospital, _ = Hospital.objects.get_or_create(name=hospital_name)
    user, created = User.objects.get_or_create(username=username)
    if created:
        user.set_password("Patient@123")
        user.save()
    patient, pcreated = Patient.objects.get_or_create(
        user=user,
        defaults={
            "gender": gender,
            "age": age,
            "hospital": hospital,
        }
    )
    print(f"{'Created' if pcreated else 'Exists'}: {username}")

print("Done! All patients added.")