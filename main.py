# Library
from fastapi import FastAPI, Form, File, Request, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from fastapi.templating import Jinja2Templates
from io import BytesIO
import numpy as np
import os
from datetime import datetime
from pydantic import BaseModel
from YOLO.model import PlateRecognizerModel
from Database.database import Database


# 
app = FastAPI()

db = Database("Database/parking-lot.db")
templates = Jinja2Templates(directory="FrontEnd")



class PlateDetection():
    def __init__(self, model, image):
        self.recognizer = PlateRecognizerModel(model, image)

class Database():
    def __init__(self, database):
        self.database = Database(database)

class Reservation(BaseModel):
    plate_number: str
    park_lot: str
    date: str
    start_time: str
    end_time: str

def time(date: str, time:str):
    return date+" "+time+":00"

# Navigating the Website
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/check-in", response_class=HTMLResponse)
async def check_in_page(request: Request):
    return templates.TemplateResponse("checkin.html", {"request": request})

@app.get("/reserve", response_class= HTMLResponse)
async def reserve_page(request: Request):
    return templates.TemplateResponse("reserve.html", {"request": request})

@app.post("/check-in")
async def upload_file(file: UploadFile = File(...)):
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)  
    temp_path = os.path.join(temp_dir, file.filename)

    contents = await file.read()
    with open(temp_path, "wb") as f:
        f.write(contents)

    plate_detector = PlateRecognizerModel("platedetection.pt", temp_path)
    recognized_plate = plate_detector.text()  

    check_AI = db.checkin(recognized_plate)
    os.remove(temp_path)



    return {"Success": check_AI}

@app.post("/reservations")
def create_reservation(reservation: Reservation):
    try:
        res_date = datetime.strptime(reservation.date, "%Y-%m-%d").date()
        start_time = datetime.strptime(reservation.start_time, "%H:%M").time()
        end_time = datetime.strptime(reservation.end_time, "%H:%M").time()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date or time format")
    
    try:
        spot_id = int(reservation.park_lot)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid park lot ID")
    
    try:
        db.reserving(reservation.plate_number, spot_id, time(reservation.date, reservation.start_time), time(reservation.date, reservation.end_time))
        return {"message": "Reservation successful!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)