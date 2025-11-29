# YouTube Creative Commons Shorts Reuploader

This project automatically finds Creative Commons vertical shorts on YouTube and reuploads them twice per day.

## Features

- Searches for Creative Commons videos on YouTube
- Filters for vertical format videos (9:16 aspect ratio)
- Downloads and reuploads videos automatically
- Runs twice per day (9:00 AM and 9:00 PM UTC) via GitHub Actions
- Tracks uploaded videos to avoid duplicates
- Fully automated with GitHub Actions

## Prerequisites

1. **Python 3.7+**
2. **FFmpeg** - Required for video dimension checking
   - Install on macOS: `brew install ffmpeg`
   - Install on Linux: `sudo apt-get install ffmpeg`
   - Install on Windows: Download from https://ffmpeg.org/

3. **YouTube API Credentials** - Already set up in this project

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install yt-dlp (if not already installed):
```bash
pip install yt-dlp
```

3. Generate OAuth token (if not already done):
```bash
python3 generate_token.py
```

## Usage

### GitHub Actions (Recommended - Automated)

The project is set up to run automatically twice per day using GitHub Actions.

**Setup Instructions:**

1. **Create a GitHub repository** and push this code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

2. **Set up GitHub Secrets:**
   - Go to your repository → Settings → Secrets and variables → Actions
   - Add the following secrets:
     - `CLIENT_SECRET_JSON`: Content of your `client_secret_*.json` file
     - `TOKEN_JSON`: Content of your `token.json` file (generate it locally first using `generate_token.py`)

3. **The workflow will automatically run:**
   - Twice per day at 9:00 AM and 9:00 PM UTC
   - You can also trigger it manually via "Actions" → "Upload Creative Commons Shorts" → "Run workflow"

### Local Usage

#### Manual Run

To run the upload script once:
```bash
python3 upload_shorts.py
```

#### Scheduled Runs (Local Scheduler)

To run the scheduler locally that automatically uploads twice per day:
```bash
python3 scheduler.py
```

The scheduler will run uploads at:
- **9:00 AM** (morning)
- **9:00 PM** (evening)

You can modify these times in `scheduler.py` by changing the `MORNING_TIME` and `EVENING_TIME` variables.

#### Running as a Background Service

To keep the scheduler running in the background:

**macOS/Linux:**
```bash
nohup python3 scheduler.py > scheduler.log 2>&1 &
```

Or use a process manager like `pm2` or `supervisord`.

## Configuration

You can customize the following in `upload_shorts.py`:

- `SEARCH_QUERY`: Change the search term (default: 'dogs')
- `MAX_RESULTS`: Number of videos to search per run (default: 10)
- `max_uploads_per_run`: Number of videos to upload per run (default: 2)

## How It Works

1. **Search**: Searches YouTube for Creative Commons videos matching your query
2. **Filter**: Checks if videos are vertical format (9:16 aspect ratio)
3. **Download**: Downloads the video using yt-dlp
4. **Upload**: Uploads to your YouTube channel
5. **Track**: Saves uploaded video IDs to avoid duplicates

## Files

- `generate_token.py` - Generates OAuth token for YouTube API
- `upload_shorts.py` - Main script to search, download, and upload videos
- `scheduler.py` - Scheduler to run uploads twice daily
- `uploaded_videos.json` - Tracks uploaded videos (created automatically)
- `downloads/` - Temporary directory for downloaded videos (created automatically)

## Notes

- Videos are automatically deleted after upload
- The script tracks uploaded videos to prevent duplicates
- Only vertical format videos (aspect ratio >= 1.5) are uploaded
- Videos must be Creative Commons licensed
- Videos must be shorts (under 60 seconds)

## Troubleshooting

**Error: "redirect_uri_mismatch"**
- Make sure you've added the redirect URI in Google Cloud Console
- Or use a Desktop app OAuth client instead of Web app

**Error: "access_denied"**
- Add yourself as a test user in Google Cloud Console OAuth consent screen

**Error: "ffprobe not found"**
- Install FFmpeg: `brew install ffmpeg` (macOS) or `sudo apt-get install ffmpeg` (Linux)

**Error: "yt-dlp not found"**
- Install yt-dlp: `pip install yt-dlp`

