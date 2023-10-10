from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
from pathlib import Path
import random
import pyotp
import qrcode
from io import BytesIO

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

# Shared secret key for TOTP (replace with your secret key)
totp_secret_key = "your_secret_key"

# Create a TOTP instance
totp = pyotp.TOTP(totp_secret_key)

# Define a custom dependency for TOTP authentication
def authenticate_totp(password: str = Depends(totp.verify)):
    if not password:
        raise HTTPException(status_code=401, detail="TOTP authentication failed")
    return password

@app.get("/getcode/")
async def get_current_code(password: str = Depends(authenticate_totp)):
    return {"code": current_code}

@app.post("/getfile/")
async def get_file(code: str):
    try:
        # Check if the requested file exists in the upload directory
        file_path = upload_dir / '2304.08485.pdf'
        if not file_path.exists():
            return JSONResponse(content={"error": "File not found"}, status_code=404)
        
        # Check if the provided code matches the current code
        if code == current_code:
            return FileResponse(file_path, headers={"Content-Disposition": f"attachment; filename=2304.08485.pdf"})
        else:
            return JSONResponse(content={"error": "Wrong code"}, status_code=400)
        
    except Exception as e:
        return JSONResponse(content={"error": f"An error occurred: {str(e)}"}, status_code=500)

@app.get("/setup_totp/")
async def setup_totp():
    # Generate a QR code URL
    uri = totp.provisioning_uri(name='YourApp', issuer_name='YourIssuer')

    # Create a QR code image
    img = qrcode.make(uri)

    # Convert the image to bytes
    img_bytes = BytesIO()
    img.save(img_bytes)

    # Return the QR code image as a response
    return JSONResponse(status_code=200,
                        headers={"Content-Type": "image/png"}, content=img_bytes.getvalue())
