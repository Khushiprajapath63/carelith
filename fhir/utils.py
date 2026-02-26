import requests
import base64
import os
import json
from django.conf import settings

# ============================================================
# Toggle this to switch between HAPI FHIR and Local Storage
# Set USE_LOCAL_STORAGE = True if HAPI server is not running
# ============================================================
USE_LOCAL_STORAGE = True
FHIR_BASE_URL = "http://localhost:8080/fhir"

# Local storage paths
LOCAL_FHIR_DIR = os.path.join(settings.MEDIA_ROOT, "fhir_local")
LOCAL_PATIENTS_DIR = os.path.join(LOCAL_FHIR_DIR, "patients")
LOCAL_DOCUMENTS_DIR = os.path.join(LOCAL_FHIR_DIR, "documents")
LOCAL_INDEX_FILE = os.path.join(LOCAL_FHIR_DIR, "index.json")


def _ensure_dirs():
    """Make sure local storage folders exist."""
    os.makedirs(LOCAL_PATIENTS_DIR, exist_ok=True)
    os.makedirs(LOCAL_DOCUMENTS_DIR, exist_ok=True)


def _load_index():
    """Load the local document index."""
    if os.path.exists(LOCAL_INDEX_FILE):
        with open(LOCAL_INDEX_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_index(index):
    """Save the local document index."""
    _ensure_dirs()
    with open(LOCAL_INDEX_FILE, "w") as f:
        json.dump(index, f, indent=2)


# ============================================================
# CREATE FHIR PATIENT
# ============================================================
def create_fhir_patient(patient_name, patient_identifier):
    if USE_LOCAL_STORAGE:
        return _local_create_fhir_patient(patient_name, patient_identifier)

    url = f"{FHIR_BASE_URL}/Patient"
    payload = {
        "resourceType": "Patient",
        "identifier": [{"value": str(patient_identifier)}],
        "name": [{"text": patient_name}]
    }
    headers = {"Content-Type": "application/fhir+json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        if response.status_code in [200, 201]:
            return response.json().get("id")
    except Exception as e:
        print(f"[FHIR] create_fhir_patient failed: {e}")
    return None


def _local_create_fhir_patient(patient_name, patient_identifier):
    _ensure_dirs()
    # Use the patient_identifier as the local FHIR ID
    fhir_id = str(patient_identifier)
    patient_data = {
        "resourceType": "Patient",
        "id": fhir_id,
        "identifier": [{"value": fhir_id}],
        "name": [{"text": patient_name}]
    }
    file_path = os.path.join(LOCAL_PATIENTS_DIR, f"{fhir_id}.json")
    with open(file_path, "w") as f:
        json.dump(patient_data, f, indent=2)
    return fhir_id


# ============================================================
# CHECK PATIENT EXISTS
# ============================================================
def check_patient_exists(patient_fhir_id):
    if USE_LOCAL_STORAGE:
        return _local_check_patient_exists(patient_fhir_id)

    url = f"{FHIR_BASE_URL}/Patient/{patient_fhir_id}"
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"[FHIR] check_patient_exists failed: {e}")
        return False


def _local_check_patient_exists(patient_fhir_id):
    file_path = os.path.join(LOCAL_PATIENTS_DIR, f"{patient_fhir_id}.json")
    return os.path.exists(file_path)


# ============================================================
# GET DOCUMENT REFERENCES
# ============================================================
def get_document_references(patient_fhir_id):
    if USE_LOCAL_STORAGE:
        return _local_get_document_references(patient_fhir_id)

    url = f"{FHIR_BASE_URL}/DocumentReference?subject=Patient/{patient_fhir_id}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"[FHIR] get_document_references failed: {e}")
    return None


def _local_get_document_references(patient_fhir_id):
    index = _load_index()
    patient_docs = index.get(str(patient_fhir_id), [])

    entries = []
    for doc_id in patient_docs:
        doc_file = os.path.join(LOCAL_DOCUMENTS_DIR, f"{doc_id}.json")
        if os.path.exists(doc_file):
            with open(doc_file, "r") as f:
                doc_data = json.load(f)
            entries.append({"resource": doc_data})

    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": entries
    }


# ============================================================
# UPLOAD DOCUMENT REFERENCE
# ============================================================
def upload_document_reference(patient_fhir_id, file_path, description="Uploaded Report"):
    if USE_LOCAL_STORAGE:
        return _local_upload_document_reference(patient_fhir_id, file_path, description)

    url = f"{FHIR_BASE_URL}/DocumentReference"
    file_name = os.path.basename(file_path)
    ext = file_name.split(".")[-1].lower()

    content_type_map = {
        "pdf": "application/pdf",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "json": "application/json"
    }
    content_type = content_type_map.get(ext, "application/octet-stream")

    with open(file_path, "rb") as f:
        file_data = f.read()
    encoded_data = base64.b64encode(file_data).decode("utf-8")

    payload = {
        "resourceType": "DocumentReference",
        "status": "current",
        "type": {"text": "Medical Report"},
        "subject": {"reference": f"Patient/{patient_fhir_id}"},
        "description": description,
        "content": [
            {
                "attachment": {
                    "contentType": content_type,
                    "title": file_name,
                    "data": encoded_data
                }
            }
        ]
    }

    headers = {"Content-Type": "application/fhir+json"}
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.status_code, response.text
    except Exception as e:
        print(f"[FHIR] upload_document_reference failed: {e}")
        return 500, str(e)


def _local_upload_document_reference(patient_fhir_id, file_path, description):
    _ensure_dirs()

    file_name = os.path.basename(file_path)
    ext = file_name.split(".")[-1].lower()

    content_type_map = {
        "pdf": "application/pdf",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "json": "application/json"
    }
    content_type = content_type_map.get(ext, "application/octet-stream")

    # ✅ Save actual file into media/fhir_downloads/
    download_dir = os.path.join(settings.MEDIA_ROOT, "fhir_downloads")
    os.makedirs(download_dir, exist_ok=True)
    dest_path = os.path.join(download_dir, file_name)
    with open(file_path, "rb") as src, open(dest_path, "wb") as dst:
        dst.write(src.read())

    # ✅ Build file URL so doctor can view/download it
    file_url = settings.MEDIA_URL + "fhir_downloads/" + file_name

    # ✅ Generate a doc ID
    import time
    doc_id = f"{patient_fhir_id}_{int(time.time())}"

    doc_data = {
        "resourceType": "DocumentReference",
        "id": doc_id,
        "status": "current",
        "type": {"text": "Medical Report"},
        "subject": {"reference": f"Patient/{patient_fhir_id}"},
        "description": description,
        "author": [{"display": description}],
        "content": [
            {
                "attachment": {
                    "contentType": content_type,
                    "title": file_name,
                    "url": file_url   # ✅ actual viewable URL
                }
            }
        ]
    }

    # Save document JSON
    doc_file = os.path.join(LOCAL_DOCUMENTS_DIR, f"{doc_id}.json")
    with open(doc_file, "w") as f:
        json.dump(doc_data, f, indent=2)

    # Update index
    index = _load_index()
    pid = str(patient_fhir_id)
    if pid not in index:
        index[pid] = []
    index[pid].append(doc_id)
    _save_index(index)

    return 201, "Stored locally"


# ============================================================
# SAVE FHIR ATTACHMENT LOCALLY (helper)
# ============================================================
def save_fhir_attachment_locally(entry):
    """
    Takes one DocumentReference entry, extracts base64 attachment,
    saves it into media/fhir_downloads/ and returns the file URL.
    """
    try:
        attachment = entry["resource"]["content"][0]["attachment"]
        title = attachment.get("title", "report_file")

        # If it already has a URL, return it directly
        if attachment.get("url"):
            return attachment["url"]

        encoded_data = attachment.get("data")
        if not encoded_data:
            return None

        decoded_file = base64.b64decode(encoded_data)
        folder_path = os.path.join(settings.MEDIA_ROOT, "fhir_downloads")
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, title)
        with open(file_path, "wb") as f:
            f.write(decoded_file)

        return settings.MEDIA_URL + "fhir_downloads/" + title

    except Exception as e:
        print(f"[FHIR] save_fhir_attachment_locally failed: {e}")
        return None