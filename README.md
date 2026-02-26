# Carelith – Healthcare Information System

## Overview
Carelith is a secure healthcare management system built using Django. It provides role-based dashboards for doctors and patients, OTP-based access control, and FHIR integration for medical interoperability.

## Features
- Doctor Dashboard
- Patient Dashboard
- OTP-Based Access Control
- FHIR Integration
- Report Upload & Explanation
- Secure Authentication

## Tech Stack
- Python
- Django
- SQLite (Development)
- FHIR API Integration
- Bootstrap

## Installation

1. Clone repository
2. Create virtual environment
3. Install dependencies:
   pip install -r requirements.txt
4. Run migrations:
   python manage.py migrate
5. Run server:
   python manage.py runserver

## Project Structure
- doctor_app/
- patients/
- records/
- access_control/
- fhir/

## Developed By
Khushi Prajapath