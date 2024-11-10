from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from datetime import datetime
from typing import List
import os
import zipfile
from io import BytesIO

app = FastAPI()

# Set the base path for file storage
BASE_FILE_PATH = "/app/personal"
os.makedirs(BASE_FILE_PATH, exist_ok=True)


@app.post("/upload_and_zip")
async def upload_and_zip(
        request: Request,
        subject: str = Form(...),
        topic: str = Form(...),
        files: List[UploadFile] = File(...),
):
    # Use the current date for the entry
    date = datetime.now().strftime("%Y-%m-%d")

    # Define the zip file path and name based on subject, topic, and date
    zip_filename = f"{subject}_{topic}_{date}.zip"
    zip_file_path = os.path.join(BASE_FILE_PATH, zip_filename)

    # Create a zip file in memory
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file in files:
            # Read file content and write it directly to the zip archive
            file_content = await file.read()
            zipf.writestr(file.filename, file_content)

    # Generate the URL for the zip file
    base_url = "http://" + request.url.netloc
    zip_file_url = f"{base_url}/download-zip/{zip_filename}"

    return {
        "message": "Files successfully uploaded and zipped",
        "zip_file_url": zip_file_url
    }


# Endpoint to download the created zip file
@app.get("/download-zip/{zip_name}")
async def download_zip(zip_name: str):
    zip_path = os.path.join(BASE_FILE_PATH, zip_name)

    # Check if the file exists before serving
    if not os.path.isfile(zip_path):
        raise HTTPException(status_code=404, detail="Zip file not found")

    # Serve the ZIP file
    return FileResponse(zip_path, filename=zip_name, media_type="application/zip")
