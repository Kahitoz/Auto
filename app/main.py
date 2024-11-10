from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
import os
import shutil
import zipfile

app = FastAPI()

# Set the base path for file storage
BASE_IMAGE_PATH = "/app/personal"
os.makedirs(BASE_IMAGE_PATH, exist_ok=True)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify only allowed domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/post_vid_file")
async def post_vid_file(
        subject: str = Form(...),
        topic: str = Form(...),
        files: List[UploadFile] = File(...),  # Accepts any type of file, not just video
):
    # Use the current date for the entry
    date = datetime.now().strftime("%Y-%m-%d")

    # Create a directory for storing the files for this post
    post_dir = os.path.join(BASE_IMAGE_PATH, f"{subject}_{topic}_{date}")
    os.makedirs(post_dir, exist_ok=True)

    saved_files = []

    for file in files:
        file_location = os.path.join(post_dir, file.filename)
        with open(file_location, "wb") as file_object:
            shutil.copyfileobj(file.file, file_object)
        saved_files.append(file_location)

    # Create a zip file of the uploaded files
    zip_file_path = os.path.join(BASE_IMAGE_PATH, f"{subject}_{topic}_{date}.zip")
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file_path in saved_files:
            zipf.write(file_path, os.path.basename(file_path))

    # Generate the URL for downloading the zip file
    # (Assuming you have NGINX or another service to serve files from BASE_IMAGE_PATH)
    download_url = f"http://192.168.1.2:30008//{os.path.basename(zip_file_path)}"

    return {
        "message": "File(s) successfully uploaded and zipped",
        "subject": subject,
        "topic": topic,
        "date": date,
        "file_paths": saved_files,
        "zip_file_url": download_url,
    }
