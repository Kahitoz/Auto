from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
import os
import shutil

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

    return {
        "message": "File(s) successfully uploaded",
        "subject": subject,
        "topic": topic,
        "date": date,
        "file_paths": saved_files,
    }
