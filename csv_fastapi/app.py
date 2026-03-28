from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session  
import pandas as pd
from sqlalchemy import text
from models import Student
import models
from database import engine, Base, SessionLocal

# -----------------------------
# DB Setup
# -----------------------------
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Loading file
try:
    df = pd.read_csv("students_complete.csv").fillna("")
  
except Exception as e:
    df = pd.DataFrame()
    print("Error loading CSV:", e)

# -----------------------------
# Dependency for DB Session
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1st endpoint
@app.get("/")
def home():
    return {"message": "Welcome to FastAPI🚀"}


# -----------------------------
# ✅ HEALTH CHECK ENDPOINT
# -----------------------------
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        # ✅ FIXED LINE
        db.execute(text("SELECT 1"))

        data_status = "loaded" if not df.empty else "not loaded"

        return {
            "status": "healthy",
            "database": "connected",
            "dataframe": data_status
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

# Get data endpoint 2nd
@app.get("/data")
def get_all_data():
    return df.to_dict(orient="records")

# Get data by ID
@app.get("/data/{item_id}")
def get_data_by_id(item_id: str):
    result = df[df["student_id"] == item_id]
    
    if result.empty:
        raise HTTPException(status_code=404, detail="Item not found")
    
    return result.to_dict(orient="records")[0]

    # -----------------------------
# Get All Students (DB)
# -----------------------------
@app.get("/students")
def get_students(db: Session = Depends(get_db)):
    students = db.query(models.Student).all()
    return students
