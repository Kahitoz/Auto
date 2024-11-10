from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List
import os
import shutil
import zipfile

app = FastAPI()

# Set the base path for file storage
BASE_FILE_PATH = "/app/personal"
os.makedirs(BASE_FILE_PATH, exist_ok=True)

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
        files: List[UploadFile] = File(...),
):
    # Use the current date for the entry
    date = datetime.now().strftime("%Y-%m-%d")

    # Create a directory for storing the files for this post
    post_dir = os.path.join(BASE_FILE_PATH, f"{subject}_{topic}_{date}")
    os.makedirs(post_dir, exist_ok=True)
    print(f"Directory created for files: {post_dir}")  # Debug

    saved_files = []

    for file in files:
        file_location = os.path.join(post_dir, file.filename)
        with open(file_location, "wb") as file_object:
            shutil.copyfileobj(file.file, file_object)
        saved_files.append({
            "File": file.filename,
            "Path": post_dir
        })
        print(f"File saved at: {file_location}")  # Debug

    # Create a zip file of the uploaded files in the base path
    zip_filename = f"{subject}_{topic}_{date}.zip"
    zip_file_path = os.path.join(BASE_FILE_PATH, zip_filename)
    with zipfile.ZipFile(zip_file_path, 'w') as zipf:
        for file_path in [os.path.join(post_dir, f["File"]) for f in saved_files]:
            zipf.write(file_path, os.path.basename(file_path))
    print(f"Zip file created at: {zip_file_path}")  # Debug

    # Generate the URL for the zip file
    base_url = "http://" + request.url.netloc
    zip_file_url = f"{base_url}/cdnservice/zip/{zip_filename}"

    # Modify the saved files to include accessible URLs
    for item in saved_files:
        file_name = item['File']
        file_path = os.path.basename(item['Path']).strip('/')
        item['FileURL'] = f"{base_url}/cdnservice/{file_path}/{file_name}"

    # Return the modified result as a JSON response with zip file link
    return {
        "message": "Files successfully uploaded, zipped, and URLs generated",
        "subject": subject,
        "topic": topic,
        "date": date,
        "file_data": saved_files,
        "zip_file_url": zip_file_url
    }

# Serve individual files
@app.get("/cdnservice/{file_path}/{file_name}")
async def serve_file(file_path: str, file_name: str):
    # Construct the full file path by combining base path and dynamic path
    file_full_path = os.path.join(BASE_FILE_PATH, file_path, file_name)
    print(f"Attempting to serve file at: {file_full_path}")  # Debug

    # Check if the file exists
    if not os.path.exists(file_full_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Serve the file as a FileResponse
    return FileResponse(file_full_path)

# Serve the zip file directly from BASE_FILE_PATH
@app.get("/cdnservice/zip/{zip_name}")
async def serve_zip(zip_name: str):
    zip_file_path = os.path.join(BASE_FILE_PATH, zip_name)
    print(f"Attempting to serve zip file at: {zip_file_path}")  # Debug

    # Check if the zip file exists
    if not os.path.exists(zip_file_path):
        raise HTTPException(status_code=404, detail="Zip file not found")

    # Serve the zip file as a FileResponse
    return FileResponse(zip_file_path)


BASE_DIR = os.path.dirname(__file__)


@app.get("/download-zip/{zip_name}")
async def download_zip(zip_name: str):
    zip_path = os.path.join(BASE_DIR, "personal", zip_name)
    # Check if the file exists before trying to serve it
    if not os.path.isfile(zip_path):
        return {"error": zip_path}

    # Serve the ZIP file
    return FileResponse(zip_path, filename="Desktop.zip", media_type="application/zip")