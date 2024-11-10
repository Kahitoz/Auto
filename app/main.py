from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from datetime import datetime
from typing import List, Optional
import os
import zipfile
import pywhatkit
import asyncio  # for asynchronous delay
from io import BytesIO

app = FastAPI()

# Set the base path for file storage
BASE_FILE_PATH = "/app/personal"
os.makedirs(BASE_FILE_PATH, exist_ok=True)


# Function to send WhatsApp message to a number or group
async def send_whatsapp_message(recipient: str, message: str, is_group: bool = False):
    now = datetime.now()
    hour = now.hour
    minute = now.minute + 2  # Schedule the message 2 minutes from now to allow for async execution

    if is_group:
        # Sending message to a WhatsApp group
        pywhatkit.sendwhatmsg_to_group(recipient, message, hour, minute)
    else:
        # Sending message to an individual number
        pywhatkit.sendwhatmsg(recipient, message, hour, minute)


@app.post("/upload_and_zip")
async def upload_and_zip(
        request: Request,
        subject: str = Form(...),
        topic: str = Form(...),
        files: List[UploadFile] = File(...),
        recipient: str = Form(...),  # Phone number or group ID
        is_group: Optional[bool] = Form(False)  # Specify if recipient is a group
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

    # Prepare the message
    message = f"Your files have been successfully uploaded and zipped. You can download them here: {zip_file_url}"

    # Send WhatsApp message to the specified recipient (individual or group)
    await send_whatsapp_message(recipient, message, is_group)

    return {
        "message": "Files successfully uploaded, zipped, and WhatsApp message sent",
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
