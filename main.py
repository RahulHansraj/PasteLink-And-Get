"""
FastAPI Backend for Media Download
Supports YouTube and Instagram video downloads with automatic platform detection.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Literal, Optional
import yt_dlp
import base64
import os
import uuid
import glob
import shutil

app = FastAPI(
    title="Media Download API",
    description="Download videos from YouTube and Instagram",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
TEMP_DIR = "temp_downloads"
COOKIES_YOUTUBE = "cookies_youtube.txt"
COOKIES_INSTAGRAM = "cookies_instagram.txt"


class DownloadRequest(BaseModel):
    """Request model - only URL field required"""
    url: str
    format: Optional[Literal['mp4', 'mp3']] = 'mp4'  # Optional: default to mp4


class DownloadResponse(BaseModel):
    """Response model with status, filename, data, and message"""
    status: Literal['success', 'error']
    filename: str
    data: str
    message: str


def detect_platform(url: str) -> str:
    """
    Automatically detect the platform based on URL.
    
    Args:
        url: The user-provided URL
        
    Returns:
        Platform name: 'youtube', 'instagram', or 'unsupported'
    """
    url_lower = url.lower()
    
    if "instagram.com" in url_lower or "/reel/" in url_lower or "/reels/" in url_lower:
        return "instagram"
    elif "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    else:
        return "unsupported"


def get_youtube_options(output_template: str, format_type: str = 'mp4') -> dict:
    """
    Get yt_dlp options for YouTube downloads.
    
    Args:
        output_template: Output file path template
        format_type: 'mp4' or 'mp3'
        
    Returns:
        Dictionary of yt_dlp options
    """
    cookie_file = os.path.join(os.getcwd(), COOKIES_YOUTUBE)
    
    if format_type == 'mp3':
        return {
            "format": "bestaudio/best",
            "outtmpl": output_template,
            "cookiefile": cookie_file if os.path.exists(cookie_file) else None,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ]
        }
    else:
        # MP4 - best video + best audio merged
        return {
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "outtmpl": output_template,
            "cookiefile": cookie_file if os.path.exists(cookie_file) else None,
            "quiet": True,
            "no_warnings": True,
            "nocheckcertificate": True,
        }


def get_instagram_options(output_template: str) -> dict:
    """
    Get yt_dlp options for Instagram downloads.
    Always downloads highest quality MP4.
    
    Args:
        output_template: Output file path template
        
    Returns:
        Dictionary of yt_dlp options
    """
    cookie_file = os.path.join(os.getcwd(), COOKIES_INSTAGRAM)
    
    return {
        "format": "best[ext=mp4]/best",
        "outtmpl": output_template,
        "cookiefile": cookie_file if os.path.exists(cookie_file) else None,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
    }


def find_downloaded_file(temp_dir: str, unique_id: str) -> Optional[str]:
    """
    Find the downloaded file in the temp directory.
    
    Args:
        temp_dir: Temporary directory path
        unique_id: Unique identifier used in filename
        
    Returns:
        Full path to downloaded file or None
    """
    pattern = os.path.join(temp_dir, f"{unique_id}.*")
    files = glob.glob(pattern)
    
    if files:
        return files[0]
    return None


def cleanup_file(filepath: str) -> None:
    """Safely remove a file."""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except Exception:
        pass


@app.get("/")
def read_root():
    """Health check endpoint."""
    return {
        "message": "Media Download Backend is running!",
        "version": "1.0.0",
        "supported_platforms": ["youtube", "instagram"]
    }


@app.post("/download", response_model=DownloadResponse)
@app.post("/download/", response_model=DownloadResponse)
def download_media(request: DownloadRequest):
    """
    Download media from YouTube or Instagram.
    
    The platform is automatically detected from the URL:
    - YouTube: youtube.com, youtu.be
    - Instagram: instagram.com, /reel/, /reels/
    
    Args:
        request: DownloadRequest with url and optional format (mp4/mp3)
        
    Returns:
        DownloadResponse with status, filename, base64 data, and message
    """
    url = request.url.strip()
    format_type = request.format or 'mp4'
    
    # Validate URL
    if not url:
        return DownloadResponse(
            status="error",
            filename="",
            data="",
            message="URL is required"
        )
    
    # Detect platform automatically
    platform = detect_platform(url)
    
    if platform == "unsupported":
        return DownloadResponse(
            status="error",
            filename="",
            data="",
            message="Unsupported URL. Only YouTube and Instagram URLs are supported."
        )
    
    # Create temp directory
    os.makedirs(TEMP_DIR, exist_ok=True)
    
    # Generate unique ID for this download
    unique_id = str(uuid.uuid4())
    output_template = os.path.join(TEMP_DIR, f"{unique_id}.%(ext)s")
    
    downloaded_file = None
    
    try:
        # Get platform-specific options
        if platform == "instagram":
            ydl_opts = get_instagram_options(output_template)
            expected_ext = "mp4"
        else:  # YouTube
            ydl_opts = get_youtube_options(output_template, format_type)
            expected_ext = "mp3" if format_type == "mp3" else "mp4"
        
        # Remove None cookiefile if cookie file doesn't exist
        if ydl_opts.get("cookiefile") is None:
            del ydl_opts["cookiefile"]
        
        # Download the media
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Get the title for filename
            title = info.get('title', 'download')
            # Clean filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title[:100]  # Limit length
        
        # Find the downloaded file
        downloaded_file = find_downloaded_file(TEMP_DIR, unique_id)
        
        if not downloaded_file or not os.path.exists(downloaded_file):
            return DownloadResponse(
                status="error",
                filename="",
                data="",
                message="Download completed but file not found"
            )
        
        # Get actual extension
        actual_ext = os.path.splitext(downloaded_file)[1].lstrip('.')
        
        # Read and encode file to Base64
        with open(downloaded_file, "rb") as f:
            file_data = f.read()
        
        base64_data = base64.b64encode(file_data).decode("utf-8")
        
        # Create final filename
        final_filename = f"{safe_title}.{actual_ext}"
        
        # Cleanup
        cleanup_file(downloaded_file)
        
        return DownloadResponse(
            status="success",
            filename=final_filename,
            data=base64_data,
            message=f"Successfully downloaded from {platform.capitalize()}"
        )
    
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e)
        if "Private video" in error_msg:
            message = "This video is private and cannot be downloaded"
        elif "Video unavailable" in error_msg:
            message = "This video is unavailable"
        elif "Sign in" in error_msg or "login" in error_msg.lower():
            message = f"Authentication required. Please ensure {COOKIES_INSTAGRAM if platform == 'instagram' else COOKIES_YOUTUBE} is properly configured."
        else:
            message = f"Download failed: {error_msg}"
        
        cleanup_file(downloaded_file)
        
        return DownloadResponse(
            status="error",
            filename="",
            data="",
            message=message
        )
    
    except Exception as e:
        cleanup_file(downloaded_file)
        
        return DownloadResponse(
            status="error",
            filename="",
            data="",
            message=f"An error occurred: {str(e)}"
        )


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    youtube_cookies_exist = os.path.exists(os.path.join(os.getcwd(), COOKIES_YOUTUBE))
    instagram_cookies_exist = os.path.exists(os.path.join(os.getcwd(), COOKIES_INSTAGRAM))
    
    return {
        "status": "healthy",
        "cookies": {
            "youtube": youtube_cookies_exist,
            "instagram": instagram_cookies_exist
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting Media Download API...")
    print(f"YouTube cookies: {COOKIES_YOUTUBE}")
    print(f"Instagram cookies: {COOKIES_INSTAGRAM}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
