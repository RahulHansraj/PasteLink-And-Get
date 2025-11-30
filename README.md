# PasteLink And Get

A mobile-first liquid-glass web app to download MP4/MP3 from social platforms.

## Architecture
- **Frontend**: React, TypeScript, Tailwind CSS.
- **Backend**: FastAPI (Python), yt-dlp, ffmpeg.

## Prerequisites
1. Node.js (v18+)
2. Python (v3.9+)
3. FFmpeg installed on your system and added to your system's PATH. (Crucial for audio conversion).

## Installation & Running

### 1. Backend (FastAPI)

Open a terminal in the project root:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server is now running at `http://localhost:8000`.

### 2. Frontend (React)

Open a **NEW** terminal in the project root:

```bash
# This project uses a pre-configured Vite-like environment.
# You just need to install dependencies.
npm install

# Start dev server
npm run dev
```

The frontend will be running on the port provided by the development environment (e.g., `http://localhost:5173`).

## Usage
1. Open the frontend URL on your phone or desktop.
2. Paste a link (YouTube, TikTok, Instagram).
3. Click "Download MP4" or "Download MP3".
4. The backend downloads the file, processes it, and sends it back as Base64.
5. The browser automatically triggers the native "Save File" dialog.

## Deployment

### Frontend (Vercel/Netlify/Cloudflare Pages)
1. Commit code to a Git repository (GitHub, GitLab, etc.).
2. Import the repository to your chosen hosting provider.
3. Build command: `npm run build` (or similar, check provider docs).
4. Output directory: `dist`.
5. **Important**: You must update `constants.ts` in your frontend code to point to your deployed Backend URL (HTTPS is required for production).

### Backend (Render/Railway)
1. These platforms are recommended as they support Python/FastAPI and can install system dependencies.
2. **Crucial**: You must use a Dockerfile or a buildpack that installs **FFmpeg**. Without FFmpeg, MP3 conversion will fail.
3. For Render: Use the "Web Service" type. The start command should be `uvicorn main:app --host 0.0.0.0 --port $PORT`.

## Note on "Backend in Frontend"
The prompt requested the backend to run "directly in the frontend". This is technically impossible for this use case because `yt-dlp` and `ffmpeg` are powerful command-line tools that require a Python runtime and system binaries, which browsers do not support for security reasons. This project provides a standard, robust monorepo structure where the frontend (in the browser) communicates with a separate backend (on a server) to achieve the desired result safely and effectively.