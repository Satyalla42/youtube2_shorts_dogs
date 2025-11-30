#!/usr/bin/env python3
"""
Script to reupload Creative Commons vertical shorts to YouTube.
Runs twice per day, only uploads vertical format videos (9:16 aspect ratio).
"""

import os
import json
import time
import glob
import subprocess
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Configuration
SCOPES = [
    'https://www.googleapis.com/auth/youtube.upload',
    'https://www.googleapis.com/auth/youtube.readonly'
]
# Find client secret file (supports both local and GitHub Actions)
def find_client_secret_file():
    """Find the client secret JSON file."""
    # Try generic name first (for GitHub Actions)
    if os.path.exists('client_secret.json'):
        return 'client_secret.json'
    # Try to find any client_secret_*.json file (for local use)
    files = glob.glob('client_secret_*.json')
    if files:
        return files[0]
    raise FileNotFoundError("No client secret file found. Expected 'client_secret.json' or 'client_secret_*.json'")

CLIENT_SECRET_FILE = find_client_secret_file()
TOKEN_FILE = 'token.json'
DOWNLOAD_DIR = 'downloads'
UPLOADED_VIDEOS_FILE = 'uploaded_videos.json'

# YouTube API settings
MAX_RESULTS = 10  # Number of videos to search per run
SEARCH_QUERY = 'dogs'  # Search query - you can change this
VIDEO_DURATION = 'short'  # Only shorts (under 60 seconds)


def load_credentials():
    """Load or refresh OAuth credentials."""
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    
    return creds


def get_youtube_service():
    """Build and return YouTube API service."""
    creds = load_credentials()
    return build('youtube', 'v3', credentials=creds)


def search_creative_commons_videos(youtube, query=SEARCH_QUERY, max_results=MAX_RESULTS):
    """Search for Creative Commons videos on YouTube."""
    try:
        request = youtube.search().list(
            part='snippet',
            q=query,
            type='video',
            videoLicense='creativeCommon',  # Only Creative Commons
            videoDuration=VIDEO_DURATION,  # Only shorts
            maxResults=max_results,
            order='viewCount'  # Popular videos first
        )
        response = request.execute()
        return response.get('items', [])
    except HttpError as e:
        print(f'An error occurred while searching: {e}')
        return []


def get_video_details(youtube, video_id):
    """Get detailed video information including dimensions."""
    try:
        request = youtube.videos().list(
            part='contentDetails,snippet,statistics',
            id=video_id
        )
        response = request.execute()
        if response.get('items'):
            return response['items'][0]
        return None
    except HttpError as e:
        print(f'An error occurred getting video details: {e}')
        return None


def is_vertical_video(video_path):
    """Check if video is vertical (9:16 aspect ratio)."""
    try:
        # Use ffprobe to get video dimensions
        cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height', '-of', 'json',
            video_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        if 'streams' in data and len(data['streams']) > 0:
            width = data['streams'][0].get('width', 0)
            height = data['streams'][0].get('height', 0)
            
            if width > 0 and height > 0:
                aspect_ratio = height / width
                # Check if aspect ratio is approximately 16/9 (vertical) or greater
                # Vertical videos have aspect ratio >= 1.5 (typically 1.777 for 9:16)
                return aspect_ratio >= 1.5
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError) as e:
        print(f'Error checking video dimensions: {e}')
    
    return False


def ensure_cookies_file():
    """Automatically create cookies.txt from browser if it doesn't exist."""
    cookies_file = 'cookies.txt'
    
    if os.path.exists(cookies_file):
        return True  # Cookies file already exists
    
    print('⚠️  cookies.txt not found. Attempting to create it from browser...')
    
    # Try to extract cookies from browsers in order of preference
    browsers = ['chrome', 'safari', 'firefox']
    
    for browser in browsers:
        try:
            print(f'  Trying to extract cookies from {browser}...')
            # Use yt-dlp to extract cookies and save to file
            cmd = [
                'yt-dlp',
                '--cookies-from-browser', browser,
                '--cookies', cookies_file,
                'https://www.youtube.com'
            ]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30,
                check=False  # Don't fail if this doesn't work
            )
            
            if os.path.exists(cookies_file) and os.path.getsize(cookies_file) > 0:
                # Check if it contains YouTube cookies
                with open(cookies_file, 'r') as f:
                    content = f.read()
                    if 'youtube.com' in content:
                        print(f'  ✅ Successfully created cookies.txt from {browser}')
                        return True
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception) as e:
            continue  # Try next browser
    
    print('  ⚠️  Could not automatically create cookies.txt')
    print('  💡 To create it manually, run:')
    print('     yt-dlp --cookies-from-browser chrome --cookies cookies.txt "https://www.youtube.com"')
    return False


def download_video(video_url, output_path):
    """Download video using yt-dlp with cookies and bot detection bypass."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Base command options
        base_opts = [
            'yt-dlp',
            '--extractor-args', 'youtube:player_client=default',  # Avoid JS runtime requirement
            '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            '-f', 'best[height<=1080]',  # Best quality up to 1080p
            '--no-warnings',  # Reduce noise in output
            '-o', output_path,
        ]
        
        # Try different cookie methods in order of preference
        cookie_methods = [
            # Method 1: Cookies from file (for GitHub Actions)
            (['--cookies', 'cookies.txt'], os.path.exists('cookies.txt')),
            # Method 2: Cookies from Chrome browser (for local use)
            (['--cookies-from-browser', 'chrome'], True),
            # Method 3: Cookies from Safari (macOS fallback)
            (['--cookies-from-browser', 'safari'], True),
            # Method 4: No cookies (last resort)
            ([], True),
        ]
        
        for cookie_opts, should_try in cookie_methods:
            if not should_try:
                continue
            try:
                method_name = 'cookies file' if '--cookies' in cookie_opts else \
                            'Chrome browser' if 'chrome' in str(cookie_opts) else \
                            'Safari browser' if 'safari' in str(cookie_opts) else \
                            'no cookies'
                print(f'  Trying download method: {method_name}')
                
                cmd = base_opts + cookie_opts + [video_url]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=300)
                if os.path.exists(output_path):
                    print(f'  ✅ Download successful using {method_name}')
                    return True
            except subprocess.CalledProcessError as e:
                error_msg = e.stderr if e.stderr else e.stdout
                # Only show error for last method to avoid spam
                if cookie_methods[-1] == (cookie_opts, should_try):
                    print(f'  ❌ Download failed: {error_msg[:200]}')
                continue  # Try next method
            except subprocess.TimeoutExpired:
                print(f'  ⏱️  Download timeout using {method_name}')
                continue  # Try next method
        
        print(f'  ❌ All download methods failed')
        return False
    except Exception as e:
        print(f'Error downloading video: {e}')
        return False


def load_uploaded_videos():
    """Load list of already uploaded video IDs."""
    if os.path.exists(UPLOADED_VIDEOS_FILE):
        with open(UPLOADED_VIDEOS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_uploaded_video(video_id):
    """Save uploaded video ID to avoid duplicates."""
    uploaded = load_uploaded_videos()
    if video_id not in uploaded:
        uploaded.append(video_id)
        with open(UPLOADED_VIDEOS_FILE, 'w') as f:
            json.dump(uploaded, f, indent=2)
        print(f'✅ Saved video ID {video_id} to tracking list')
    else:
        print(f'⚠️  Video ID {video_id} already in tracking list')


def upload_video_to_youtube(youtube, video_path, title, description):
    """Upload video to YouTube.
    
    Returns:
        tuple: (video_id, error_type) where error_type is:
            - None if successful
            - 'uploadLimitExceeded' if upload limit reached
            - 'other' for other errors
    """
    try:
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': [
                    'shorts', 'creative commons', 'dogs', 'dog', 'puppy', 'doglover', 
                    'dogvideos', 'cutedog', 'doglife', 'doggo', 'pet', 'dogsofinstagram',
                    'dogstagram', 'funny dogs', 'cute dogs', 'dog compilation', 'dog shorts',
                    'puppies', 'dog content', 'dog videos', 'shorts dogs'
                ],
                'categoryId': '22'  # People & Blogs
            },
            'status': {
                'privacyStatus': 'public',
                'selfDeclaredMadeForKids': False
            }
        }
        
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part=','.join(body.keys()),
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f'Upload progress: {int(status.progress() * 100)}%')
        
        print(f'Video uploaded successfully! Video ID: {response["id"]}')
        return (response['id'], None)
    except HttpError as e:
        error_details = e.error_details if hasattr(e, 'error_details') else []
        error_reason = None
        
        # Check for specific error reasons
        for detail in error_details:
            if isinstance(detail, dict):
                reason = detail.get('reason', '')
                if reason == 'uploadLimitExceeded':
                    error_reason = 'uploadLimitExceeded'
                    print(f'❌ Upload limit exceeded: {detail.get("message", "The user has exceeded the number of videos they may upload.")}')
                    break
        
        if error_reason != 'uploadLimitExceeded':
            print(f'An error occurred during upload: {e}')
            error_reason = 'other'
        
        return (None, error_reason)


def process_and_upload():
    """Main function to search, download, and upload videos."""
    print(f'\n=== Starting upload process at {datetime.now()} ===')
    
    # Ensure download directory exists
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    # Ensure cookies file exists (for local use)
    ensure_cookies_file()
    
    # Load list of already uploaded videos
    uploaded_videos = load_uploaded_videos()
    
    # Get YouTube service
    youtube = get_youtube_service()
    
    # Search for Creative Commons videos
    print(f'Searching for Creative Commons shorts with query: {SEARCH_QUERY}')
    videos = search_creative_commons_videos(youtube)
    
    if not videos:
        print('No videos found.')
        return
    
    print(f'Found {len(videos)} videos. Processing...')
    
    uploaded_count = 0
    max_uploads_per_run = 2  # Upload 2 videos per run
    upload_limit_reached = False
    
    for video in videos:
        if uploaded_count >= max_uploads_per_run:
            break
        
        if upload_limit_reached:
            print(f'\n⚠️  Upload limit reached. Stopping upload attempts.')
            break
        
        video_id = video['id']['videoId']
        
        # Reload uploaded videos list to catch any just-added videos
        uploaded_videos = load_uploaded_videos()
        
        # Skip if already uploaded
        if video_id in uploaded_videos:
            print(f'Video {video_id} already uploaded, skipping...')
            continue
        
        # Get video details
        video_details = get_video_details(youtube, video_id)
        if not video_details:
            continue
        
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        video_title = video['snippet']['title']
        
        print(f'\nProcessing: {video_title} ({video_id})')
        
        # Download video
        output_path = os.path.join(DOWNLOAD_DIR, f'{video_id}.mp4')
        print(f'Downloading video...')
        if not download_video(video_url, output_path):
            print(f'Failed to download video {video_id}')
            continue
        
        # Check if vertical
        print(f'Checking if video is vertical...')
        if not is_vertical_video(output_path):
            print(f'Video {video_id} is not vertical, skipping...')
            os.remove(output_path)  # Clean up
            continue
        
        # Upload to YouTube
        # Popular dog hashtags for better discoverability
        hashtags = [
            '#dog', '#dogs', '#puppy', '#doglover', '#dogvideos', '#cutedog', 
            '#doglife', '#doggo', '#pet', '#dogsofinstagram', '#dogstagram',
            '#funnydogs', '#cutedogs', '#dogcompilation', '#dogshorts', 
            '#puppies', '#dogcontent', '#dogvideos', '#shortsdogs'
        ]
        hashtag_string = ' '.join(hashtags)
        
        description = f'''Original: {video_url}

Creative Commons License

{hashtag_string}'''
        print(f'Uploading to YouTube...')
        uploaded_video_id, error_type = upload_video_to_youtube(
            youtube, 
            output_path, 
            video_title,
            description
        )
        
        if uploaded_video_id:
            # Save immediately to prevent duplicates
            save_uploaded_video(video_id)
            # Reload list to include this video in next iteration
            uploaded_videos = load_uploaded_videos()
            uploaded_count += 1
            print(f'Successfully uploaded video {video_id} (original: {video_id}, new: {uploaded_video_id})')
        elif error_type == 'uploadLimitExceeded':
            upload_limit_reached = True
            print(f'⚠️  Upload limit exceeded. This account has reached its daily upload limit.')
            print(f'   Please wait 24 hours or check your YouTube account limits.')
        else:
            print(f'Failed to upload video {video_id}')
        
        # Clean up downloaded file
        if os.path.exists(output_path):
            os.remove(output_path)
        
        # Small delay between uploads
        time.sleep(5)
    
    print(f'\n=== Upload process completed. Uploaded {uploaded_count} video(s) ===\n')


if __name__ == '__main__':
    process_and_upload()

