'''
from fastapi import FastAPI, Depends, HTTPException, APIRouter
from routers import ai, medication, mood, tips, uploads

app = FastAPI(title="Disease Management API")

app.include_router(ai.router)
app.include_router(medication.router)
app.include_router(mood.router)
app.include_router(tips.router)
app.include_router(uploads.router)

@app.get('/')
def root():
    return {"message":"API is working"}
'''

from fastapi import FastAPI, UploadFile, File, HTTPException
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import uuid
from firebase_config import ref
from google.cloud import vision
from io import BytesIO
import pandas as pd


app = FastAPI(title="Disease Management API")


# Fake database
users_db = {}
medication_logs = []
mood_logs = []
health_tips_db = {
    "Diabetes": ["Check blood sugar regularly", "Exercise 30 mins daily"],
    "hiv": ["Take meds same time daily", "Stay hydrated"]
}

# Data models
class User(BaseModel):
    id: str
    name: str
    condition: str  

class MedicationLog(BaseModel):
    user_id: str
    medication_name: str
    dosage: str
    taken_at: str = None
    

class MoodLog(BaseModel):
    user_id: str
    mood: str  
    notes: Optional[str] = None
    logged_at: datetime

class HealthTip(BaseModel):
    tip: str
    condition: str

class ChatMessage(BaseModel):
    message: str

# User routes
@app.post("/signup")
async def signup(name: str, condition: str):
    """Register a new patient"""
    user_id = str(uuid.uuid4())
    users_db[user_id] = User(id=user_id, name=name, condition=condition)
    return {"message": "User created", "user_id": user_id}

# Medication routes
'''
@app.post("/medication/log")
async def log_medication(user_id: str, medication_name: str, dosage: str):
    """Record when a medicine is taken"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    log = MedicationLog(
        user_id=user_id,
        medication_name=medication_name,
        taken_at=datetime.now(),
        dosage=dosage
    )
    medication_logs.append(log)
    return {"message": "Medication logged"}
'''
@app.post("/medication/log")
async def log_medication(log: MedicationLog):
    try:
        log_data = {
            "user_id": log.user_id,
            "medication_name": log.medication_name,
            "dosage": log.dosage,
            "taken_at": str(datetime.now()),
            "status": "taken"
        }
        new_log_ref = ref.child('medication_logs').push(log_data)

        return {
            "message": "Medication logged successfully",
            "log_id": new_log_ref.key
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''
@app.get("/medication/progress")
async def get_progress(user_id: str):
    """Get medication history"""
    user_logs = [log for log in medication_logs if log.user_id == user_id]
    return {"logs": user_logs}
'''
@app.get("/medication/history/{user_id}")
async def get_medication_history(user_id: str):
    """Retrieve medication logs from Firebase"""
    try:
        # Query logs for the specific user
        logs = ref.child('medication_logs') \
                 .order_by_child("user_id") \
                 .equal_to(user_id) \
                 .get()
        
        if not logs:
            return {"logs": []}
        
        # Convert Firebase data to list
        logs_list = [
            {"log_id": key, **value} 
            for key, value in logs.items()
        ]        
        return {"logs": logs_list}     
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Mood routes
'''
@app.post("/mood/log")
async def log_mood(user_id: str, mood: str, notes: str = None):
    """Record patient mood"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    log = MoodLog(
        user_id=user_id,
        mood=mood,
        notes=notes,
        logged_at=datetime.now()
    )
    mood_logs.append(log)
    return {"message": "Mood logged"}
'''
@app.post("/mood/log")
async def log_mood(log: MoodLog):
    try:
        log_MoodData = {
            "user_id": log.user_id,
            "mood": log.mood,
            "notes": log.notes
        }
        new_Moodlog_ref = ref.child('mood_logs').push(log_MoodData)

        return {
            "message": "Mood logged",
            "log_id": new_Moodlog_ref.key
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

'''
@app.get("/mood/history")
async def mood_history(user_id: str):
    """Get mood history"""
    user_logs = [log for log in mood_logs if log.user_id == user_id]
    return {"mood_history": user_logs}

'''
@app.get("/mood/history/{user_id}")
async def get_mood_history(user_id: str):
    """Retrieve mood logs from Firebase"""
    try:
        # Query logs for the specific user
        mood_logs = ref.child('mood_logs') \
                 .order_by_child("user_id") \
                 .equal_to(user_id) \
                 .get()
        
        if not mood_logs:
            return {"logs": []}
        
        # Convert Firebase data to list
        mood_logs_list = [
            {"log_id": key, **value} 
            for key, value in mood_logs.items()
        ]        
        return {"logs": mood_logs_list}     
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))    

# Drug scanner route
'''
@app.post("/scan/drug")
async def scan_drug(file: UploadFile = File(...)):
    """Identify medicine from photo"""
    # In real app, you'd call an image recognition API here
    return {
        "message": "Medicine identified",
        "result": "Paracetamol 500mg",
        "details": "Take 1 tablet every 6 hours as needed"
    }
'''

#google Cloud vision client
client = vision.ImageAnnotatorClient()

@app.post("/scan/drug")
async def scan_drug_with_ocr(file: UploadFile = File(...)):
    #identify medicine from a photo using Google CLoud Vision API(generic label detection)
    try:
        contents = await file.read()
        #image object for the vision API
        image = vision.Image(content=contents)
        response = client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            full_text = texts[0].description

            return {
                "message": "Text identified from the image",
                "result": "Prescription text",
                "details": full_text
            }
        else:
            return{
                "message": "No text could be identified",
                "result": "No text found",
                "details": "ensure the photo is clear"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
#$env:GOOGLE_APPLICATION_CREDENTIALS="google_serviceAccountKey.json"    


# Health tips routes
'''
@app.get("/tips")
async def get_tips(user_id: str):
    """Get personalized health tips"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_condition = users_db[user_id].condition
    tips = health_tips_db.get(user_condition, [])
    return {"tips": tips}
'''
try: 
    tips_df = pd.read_csv("health_precautions.csv")
    print("Health tips loaded successfully.")
except FileNotFoundError:
    tips_df = pd.DataFrame(columns=['Disease', 'Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4'])
    print("health_precautions.csv not found. No tips will be available.")

@app.get("/tips/{user_id}")
async def get_tips(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    
    user_disease = users_db[user_id].condition.lower()
    
    disease_row = tips_df[tips_df['Disease'].str.lower() == user_disease]
    
    if disease_row.empty:
        return {"tips": ["No specific tips available for your condition yet."]}

    precautions_list = []
    for col in disease_row.columns:
        if col.startswith('Precaution_'):
            tip = disease_row[col].iloc[0]
            if pd.notna(tip):  # Exclude empty/NaN cells
                precautions_list.append(tip)
    
    return {"tips": precautions_list}

# AI chatbot route
@app.post("/ai/chat")
async def chat(message: ChatMessage):
    """AI health assistant"""
    # Simple mock responses - in real app, connect to an AI service
    responses = {
        "side effects": "Common side effects include nausea and dizziness. Contact your doctor if severe.",
        "diet": "For your condition, recommend low-sugar, high-fiber foods.",
        "default": "I'm your health assistant. How can I help you today?"
    }
    
    reply = responses["default"]
    for keyword in responses:
        if keyword in message.message.lower():
            reply = responses[keyword]
            break
    
    return {"response": reply}

# Root route
@app.get("/")
async def root():
    return {"message": "Disease Management API is working"}
