Disease Management API

This is a FastAPI-based backend for a disease management application. It provides endpoints for users to log medication and mood, get personalized health tips, and scan images to identify medicines using the Google Cloud Vision API.

Features
User Management: Register new users with a medical condition.
Medication Logging: Log medication intake and retrieve history using Firebase Realtime Database.
Mood Tracking: Log daily moods and retrieve mood history using Firebase Realtime Database.
Health Tips: Get personalized health tips based on a user's condition from a CSV file.
AI Drug Scanner: Use the Google Cloud Vision API to identify medicines or read text from prescriptions.

Setup and Installation
Clone the Repository
Create and Activate a Virtual Environment
Bash
# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
# On Windows
python -m venv venv
.\venv\Scripts\activate
Install Dependencies
Bash
pip install -r requirements.txt
Configuration
This project relies on two cloud services: Firebase and Google Cloud. You must configure both before running the application.
1. Firebase Service Account
To connect to your Firebase Realtime Database, you need a service account JSON file.
Go to your Firebase Console > Project Settings > Service accounts.
Click "Generate New Private Key" and download the JSON file.
Place this file in your project directory and rename it to firebase-service-key.json.
SECURITY WARNING: NEVER upload this file to Git. It has been added to the .gitignore file to prevent this.
In your code (e.g., in main.py), make sure your Firebase initialization points to this file:
Python
cred = credentials.Certificate("firebase-service-key.json")
2. Google Cloud Vision API Credentials
For the /scan/drug endpoint, you need to provide your Google Cloud service account credentials.
Go to Google Cloud Console > IAM & Admin > Service Accounts.
Find your service account, click the three-dot menu under "Actions," and select "Manage keys".
Click "Add Key" > "Create new key" and choose JSON.
Download the JSON file.
Export the Environment Variable: Set the GOOGLE_APPLICATION_CREDENTIALS environment variable to the path of your downloaded JSON file.
On macOS/Linux (for the current session):
Bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/google-cloud-key.json"
On Windows (for the current session in PowerShell):
PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\google-cloud-key.json"
 Tip: For a permanent setup on Windows, use [System.Environment]::SetEnvironmentVariable(...).
Running the API
Once all dependencies are installed and configuration is complete, you can run the application with Uvicorn.
Bash
uvicorn main:app --reload
Available at http://127.0.0.1:8000
Interactive documentation at http://127.0.0.1:8000/docs
