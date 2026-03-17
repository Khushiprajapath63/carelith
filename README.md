# Carelith – Healthcare Information System

## Overview

Carelith is a secure healthcare management system built using Django.  
It provides role-based dashboards for doctors and patients, OTP-based access control, and FHIR integration for medical interoperability.

The system is designed to ensure secure medical record handling, controlled access, and interoperability with modern healthcare standards.

---

## Features

- Doctor Dashboard
- Patient Dashboard
- OTP-Based Access Control
- Time-Limited Record Access
- FHIR Integration (DocumentReference)
- Report Upload & Explanation
- Secure Authentication System
- Role-Based Access Control
- Prescription & Encounter Management

---

## Tech Stack

- **Backend:** Python, Django  
- **Frontend:** HTML, CSS, Bootstrap  
- **Database:** SQLite (Development)  
- **Interoperability:** FHIR API Integration  
- **Authentication:** Django Built-in User Model  

---

## Architecture

Carelith follows a layered architecture approach to ensure modularity, scalability, and secure healthcare data handling.

### 1. Presentation Layer (Frontend)
- Built using HTML, CSS, and Bootstrap.
- Provides responsive dashboards for Doctors and Patients.
- Handles login, OTP verification, report viewing, and file uploads.

### 2. Application Layer (Django Backend)
- Implements business logic and access control.
- Manages doctor-patient workflows.
- Handles OTP generation and verification.
- Controls report access and explanation.
- Integrates with FHIR APIs for interoperability.

### 3. Database Layer (SQLite – Development)
Stores:
- Doctor profiles
- Patient profiles
- Appointments (Encounters)
- Reports
- Prescriptions
- Access control logs

Uses Django ORM and migration system for schema management.

### 4. Interoperability Layer (FHIR Integration)
- Fetches DocumentReference resources.
- Uploads medical reports to FHIR server.
- Filters records based on authorized access.
- Ensures healthcare data standard compliance.

### 5. Security & Access Control
- OTP-based temporary access system.
- Time-bound access expiration.
- Role-based dashboard restriction.
- Secure authentication using Django.

---

## System Workflow

1. User logs into the system.
2. Role is identified (Doctor / Patient).
3. Doctor requests access to a patient.
4. OTP is generated and sent.
5. Patient verifies OTP.
6. Doctor gains time-limited access.
7. Reports can be viewed, explained, or uploaded to FHIR.

---

## Installation

1. Clone the repository  
2. Create a virtual environment  
3. Install dependencies:
4. Run migrations:
5. Start the server:
---

## Project Structure

- `doctor_app/`
- `patients/`
- `records/`
- `access_control/`
- `fhir/`
- `templates/`
- `manage.py`

---

## Future Enhancements

- PostgreSQL production deployment
- Cloud-based file storage
- ABDM Integration
- Advanced audit logging
- Deployment to GCP / AWS

---

## Developed By

Khushi Prajapath
Manasa B
Risha Rasheed P M
Diptanshu 
