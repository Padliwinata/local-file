from fastapi import FastAPI, Depends, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from pydantic import SecretStr
from datetime import datetime, timedelta
import random
from pathlib import Path  # Import the pathlib module
from enum import Enum
import shutil

app = FastAPI()

# Define the directory where files will be stored as a Path object
upload_dir = Path("uploads")

# Ensure the upload directory exists
upload_dir.mkdir(parents=True, exist_ok=True)

# Generate a random code at startup
current_code = str(random.randint(1000, 9999))

def generate_new_code():
    global current_code
    current_code = str(random.randint(1000, 9999))

# Schedule the code generation every 5 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(
    generate_new_code,
    trigger=IntervalTrigger(minutes=5),
    next_run_time=datetime.now() + timedelta(minutes=5),
)
scheduler.start()

class Matkul(str, Enum):
    webpro = "webpro"
    ppl = "ppl"
    pbo = "pbo"
    sister = "sister"
    sisop = "sisop"
    std = "std"

@app.get("/getcode/")
async def get_current_code(password: SecretStr):
    if password.get_secret_value() == "passwordaslab":
        return {"code": current_code}

@app.post("/getfile/")
async def get_file(code: str, matkul: Matkul):
    try:
        # Check if the requested file exists in the upload directory
        file_path = upload_dir / f'{matkul}.pdf'
        if not file_path.exists():
            return JSONResponse(content={"error": "File not found"}, status_code=404)
        
        # Check if the provided code matches the current code
        if code == current_code:
            return FileResponse(file_path, headers={"Content-Disposition": f"attachment; filename=2304.08485.pdf"})
        else:
            return JSONResponse(content={"error": "Wrong code"}, status_code=400)
        
    except Exception as e:
        return JSONResponse(content={"error": f"An error occurred: {str(e)}"}, status_code=500)

@app.post("/{matkul}", include_in_schema=False)
async def get_file(code: str, matkul: str):
    try:
        # Check if the requested file exists in the upload directory
        file_path = upload_dir / f'{matkul}.pdf'
        if not file_path.exists():
            return JSONResponse(content={"error": "File not found"}, status_code=404)
        
        # Check if the provided code matches the current code
        if code == current_code:
            return FileResponse(file_path, headers={"Content-Disposition": f"attachment; filename=2304.08485.pdf"})
        else:
            return JSONResponse(content={"error": "Wrong code"}, status_code=400)
        
    except Exception as e:
        return JSONResponse(content={"error": f"An error occurred: {str(e)}"}, status_code=500)

@app.post("/upload_file/")
async def upload_file(password: SecretStr, file: UploadFile, matkul: Matkul):
    try:
        # Check if the provided password is correct
        if password.get_secret_value() != "passwordaslab":  # Replace with your actual password
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Define the file path to save the uploaded file
        file_path = upload_dir / f'{matkul}.pdf'

        # Check if a file with the same name already exists and replace it
        if file_path.exists():
            file_path.unlink()

        # Save the uploaded file to the specified path
        with file_path.open("wb") as dest_file:
            shutil.copyfileobj(file.file, dest_file)

        return {"message": "File uploaded successfully"}

    except Exception as e:
        return HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
