import os
from pathlib import Path
from flask import current_app
import cloudinary.uploader
import cloudinary.api

def add_wallpaper(pic_upload, event_name):
    # Upload the image directly to Cloudinary
    # We can use the event_name as the public_id, or let Cloudinary generate one.
    # It's safer to let Cloudinary generate one to avoid collisions or invalid chars.
    
    upload_result = cloudinary.uploader.upload(
        pic_upload,
        folder="event_banners",
        transformation=[
            {'width': 700, 'height': 700, 'crop': 'limit'}
        ]
    )
    
    # Return the secure URL from Cloudinary to store in the database
    return upload_result.get('secure_url')

def delete_wallpaper(event_wallpaper_url):
    # If using default fallback, don't try to delete it
    if "res.cloudinary.com" not in event_wallpaper_url or "default" in event_wallpaper_url:
        return
        
    try:
        # Extract the public_id from the URL (e.g., event_banners/qwert12345)
        # URL format is typically: https://res.cloudinary.com/<cloud_name>/image/upload/v1234567890/<public_id>.<ext>
        public_id_with_ext = event_wallpaper_url.split('/upload/')[-1].split('/', 1)[-1]
        public_id = public_id_with_ext.rsplit('.', 1)[0]
        cloudinary.uploader.destroy(public_id)
    except Exception as e:
        print(f"Failed to delete image from Cloudinary: {e}")
