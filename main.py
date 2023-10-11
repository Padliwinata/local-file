import os
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
from settings import *

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
    std_reg = 'std_reg'
    std_int = 'std_int'
    sister_reg = 'sister_reg'
    sister_int = 'sister_int'
    pbo_it = 'pbo_it'
    pbo_if_reg = 'pbo_if_reg'
    pbo_ds = 'pbo_df'
    pbo_int = 'pbo_int'
    webpro_it = 'webpro_it'
    webpro_se = 'webpro_se'
    ppl = 'ppl'
    alpro = 'alpro'

for mat in Matkul:
    Path(f'uploads/{mat}').mkdir(parents=True, exist_ok=True)

def vigenere_encrypt(plaintext, key):
    encrypted_text = ""
    key_length = len(key)

    for i in range(len(plaintext)):
        char = plaintext[i]
        if char.isalpha():
            key_char = key[i % key_length]
            key_shift = ord(key_char.lower()) - ord('a')
            if char.isupper():
                encrypted_char = chr(((ord(char) - ord('A') + key_shift) % 26) + ord('A'))
            else:
                encrypted_char = chr(((ord(char) - ord('a') + key_shift) % 26) + ord('a'))
        else:
            encrypted_char = char
        encrypted_text += encrypted_char

    return encrypted_text

def number_string_to_letters(number_string):
    result = ""
    for char in number_string:
        if char.isdigit():
            number = int(char)
            if 1 <= number <= 26:
                result += chr(ord('A') + number - 1)
            else:
                result += char
        else:
            result += char
    return result


@app.get("/getcode/")
async def get_current_code(password: SecretStr, matkul: Matkul):
    if password.get_secret_value() == SECRET_KEY:
        encrypted_code = vigenere_encrypt(current_code, matkul.value)
        return {"origin_code": current_code, "encrypted_code": encrypted_code}

@app.get("/getfile/")
async def get_file(code: str, matkul: Matkul):
    try:
        # Check if the requested file exists in the upload directory
        files = os.listdir(upload_dir / matkul.value)
        # file_path = files[0]
        file_path = upload_dir / matkul.value / files[0]
        if not file_path.exists():
            return JSONResponse(content={"error": "File not found"}, status_code=404)
        
        # Check if the provided code matches the current code
        if code == current_code:
            return FileResponse(file_path, headers={"Content-Disposition": f"inline; filename={files[0]}"})
        else:
            return JSONResponse(content={"error": "Wrong code"}, status_code=400)
        
    except Exception as e:
        return JSONResponse(content={"error": f"An error occurred: {str(e)}"}, status_code=500)

@app.post("/{matkul}", include_in_schema=False)
async def get_file(code: str, matkul: str):
    try:
        # Check if the requested file exists in the upload directory
        files = os.listdir(upload_dir)
        file_path = files[0]
        # file_path = upload_dir / f'{matkul}.pdf'
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
        if password.get_secret_value() != SECRET_KEY:  # Replace with your actual password
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Define the file path to save the uploaded file
        file_extension = file.filename.rsplit(".", 1)[-1]
        file_path = upload_dir / matkul.value / f'{matkul.value}.{file_extension}'

        # Check if a file with the same name already exists and replace it
        if file_path.exists():
            file_path.unlink()

        # Save the uploaded file to the specified path
        with file_path.open("wb") as dest_file:
            shutil.copyfileobj(file.file, dest_file)

        return {"message": "File uploaded successfully"}

    except Exception as e:
        return HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.get("/encrypt/{plain}")
async def encrypt(plain: str):
    return number_string_to_letters(plain)

