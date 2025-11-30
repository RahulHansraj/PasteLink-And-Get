from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


from typing import Literal, Optional

class DownloadRequest(BaseModel):
	url: str
	kind: Literal['mp4', 'mp3']

class DownloadResponse(BaseModel):
	filename: str
	data: str  # Base64 encoded string
	status: Literal['success', 'error']
	message: Optional[str] = None


@app.get("/")
def read_root():
	return {"message": "Backend is running!"}

@app.post("/download/", response_model=DownloadResponse)
def download_media(request: DownloadRequest):
	import yt_dlp
	import base64
	import os
	import uuid
	from fastapi import HTTPException

	temp_dir = "temp_downloads"
	os.makedirs(temp_dir, exist_ok=True)
	unique_id = str(uuid.uuid4())
	ext = request.kind
	output_template = os.path.join(temp_dir, f"{unique_id}.%(ext)s")

	ydl_opts = {
		'format': 'bestaudio/best' if request.kind == 'mp3' else 'bestvideo+bestaudio/best',
		'outtmpl': output_template,
		'postprocessors': []
	}
	if request.kind == 'mp3':
		ydl_opts['postprocessors'].append({
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		})

	try:
		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			info = ydl.extract_info(request.url, download=True)
			if request.kind == 'mp3':
				filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
			else:
				filename = ydl.prepare_filename(info)
		with open(filename, 'rb') as f:
			file_data = f.read()
		base64_data = base64.b64encode(file_data).decode('utf-8')
		# Clean up
		os.remove(filename)
		return DownloadResponse(
			filename=os.path.basename(filename),
			data=base64_data,
			status="success",
			message="Downloaded successfully."
		)
	except Exception as e:
		return DownloadResponse(
			filename="",
			data="",
			status="error",
			message=f"Download failed: {str(e)}"
		)


if __name__ == "__main__":
	import uvicorn
	uvicorn.run(app, host="0.0.0.0", port=8000)