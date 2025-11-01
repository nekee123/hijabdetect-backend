
"""
FastAPI Hijab Detection API (using Roboflow Hosted Model)
Counts how many hijab wearers are in the uploaded image.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

# Mount static folder for CSS/images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates folder
templates = Jinja2Templates(directory="templates")

# === Endpoints ===

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})


@app.post("/detect", response_class=HTMLResponse)
async def detect_hijab_web(request: Request, file: UploadFile = File(...)):
    try:
        # Save uploaded image temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        # Send image to Roboflow API
        with open(temp_path, "rb") as image_file:
            response = requests.post(
                f"{API_URL}?api_key={API_KEY}",
                files={"file": image_file}
            )

        if response.status_code != 200:
            os.remove(temp_path)
            raise HTTPException(status_code=500, detail="Error contacting Roboflow API")

        result_json = response.json()
        hijab_count = sum(1 for pred in result_json.get("predictions", []) if pred["class"].lower() == "hijab")

        # Save the uploaded image directly, NO green boxes
        import uuid, shutil
        output_image_path = f"static/{uuid.uuid4().hex}_{file.filename}"
        shutil.copy(temp_path, output_image_path)
        os.remove(temp_path)  # clean up temp file

        # Return hijab count and image path
        result = {
            "message": f"🧕 {hijab_count} hijab wearers detected"
        }

        return templates.TemplateResponse("index.html", {
            "request": request,
            "result": result,
            "image_path": output_image_path
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
