from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import FileResponse
import uvicorn
import os

app = FastAPI()

# Directory containing shared files
shared_files_directory = "D:\proj\fastapi\local-file\soal"

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    # You can replace "your_username" and "your_password" with your desired username and password.
    if credentials.username == "your_username" and credentials.password == "your_password":
        return credentials
    raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/download/{filename}")
async def download_file(filename: str, credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    file_path = os.path.join(shared_files_directory, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
