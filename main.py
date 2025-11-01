"""
FastAPI Hijab Detection API (using Roboflow Hosted Model)
Counts how many hijab wearers are in the uploaded image.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os

# === Configuration ===
API_URL = "https://detect.roboflow.com/hijab-detector/1"
API_KEY = "rEw2P5EAJvuoL3G5BfTb"

# === App Setup ===
app = FastAPI(title="🧕 Hijab Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Endpoints ===

@app.get("/")
def home():
    return {"message": "🧕 Hijab Detection API is running!"}


@app.post("/detect")
async def detect_hijab(file: UploadFile = File(...)):
    try:
        # Save uploaded image temporarily
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Send image to Roboflow API
        with open(file_path, "rb") as image:
            response = requests.post(
                f"{API_URL}?api_key={API_KEY}",
                files={"file": image}
            )

        os.remove(file_path)  # clean up temp file

        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Error contacting Roboflow API")

        result = response.json()

        # Count hijab detections
        hijab_count = sum(1 for pred in result.get("predictions", []) if pred["class"].lower() == "hijab")

        return {
            "message": f"🧕 {hijab_count} hijab wearers detected",
            "count": hijab_count,
            "predictions": result.get("predictions", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
