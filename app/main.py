from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
import os
import shutil
import zipfile
import json

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
        request: Request,
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
        saved_files.append({
            "Image": file.filename,
            "Path": post_dir
        })

    # Create a zip file of the uploaded files
    zip_file_path = os.path.join(BASE_IMAGE_PATH, f"{subject}_{topic}_{date}.zip")
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file_path in [os.path.join(post_dir, f["Image"]) for f in saved_files]:
            zipf.write(file_path, os.path.basename(file_path))

    # Generate the URL for the zip file
    base_url = "https://" + request.url.netloc
    zip_file_url = f"{base_url}/cdnservice/zip/{os.path.basename(zip_file_path)}"

    # Modify the saved files to include accessible URLs
    for item in saved_files:
        image_name = item['Image']
        image_path = item['Path'].strip('/')  # Remove leading/trailing slashes
        item['ImageURL'] = f"{base_url}/cdnservice/images/{image_path}/{image_name}"

    # Return the modified result as a JSON response with zip file link
    return {
        "message": "Files successfully uploaded, zipped, and URLs generated",
        "subject": subject,
        "topic": topic,
        "date": date,
        "file_data": saved_files,
        "zip_file_url": zip_file_url
    }

# Serve individual images
@app.get("/cdnservice/images/{image_path:path}/{image_name}")
async def serve_image(image_path: str, image_name: str):
    # Construct the full image path by combining base path and dynamic path
    image_full_path = os.path.join(BASE_IMAGE_PATH, image_path, image_name)

    # Check if the image exists
    if not os.path.exists(image_full_path):
        raise HTTPException(status_code=404, detail="Image not found")

    # Serve the image as a FileResponse
    return FileResponse(image_full_path)

# Serve the zip file
@app.get("/cdnservice/zip/{zip_name}")
async def serve_zip(zip_name: str):
    zip_file_path = os.path.join(BASE_IMAGE_PATH, zip_name)

    # Check if the zip file exists
    if not os.path.exists(zip_file_path):
        raise HTTPException(status_code=404, detail="Zip file not found")

    # Serve the zip file as a FileResponse
    return FileResponse(zip_file_path)
