"""
YouTube Title Stats Updater
----------------------------
Automatically updates a YouTube video title every 10 minutes with:
- View count
- Like count
- Comment count

Uses OAuth 2.0 authentication and respects YouTube API quota limits.
Designed to run 24/7 on Render.com with Keep‑Alive via cron-job.org.
"""

import os
import time
import pickle
import threading
from datetime import datetime
from flask import Flask
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ==================== CONFIGURATION ====================
# Replace with your own video ID (the part after ?v= in the URL)
VIDEO_ID = 'YOUR_VIDEO_ID_HERE'

# OAuth 2.0 credentials file (download from Google Cloud Console)
CLIENT_SECRETS_FILE = 'client_secrets.json'

# Where to store the authentication token after first login
TOKEN_PICKLE_FILE = 'token.pickle'

# Scopes required for reading stats and updating titles
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

# Update interval in minutes.
# Each run costs ~51 quota units (1 for fetch + 50 for update).
# With 10‑minute intervals: 144 runs/day → 7,344 units/day (within 10,000 free quota)
UPDATE_INTERVAL_MINUTES = 10
# ======================================================

app = Flask(__name__)


def authenticate_youtube():
    """
    Authenticate using OAuth 2.0 and return a YouTube API service object.
    Saves the token locally so you don't have to log in every time.
    """
    creds = None
    # Load existing token if present
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, let the user log in via browser
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for next run
        with open(TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return build('youtube', 'v3', credentials=creds)


def get_video_stats(youtube, video_id):
    """
    Fetch current view count, like count, and comment count for the video.
    Returns a tuple (views, likes, comments) or (None, None, None) on error.
    """
    try:
        request = youtube.videos().list(
            part='statistics',
            id=video_id
        )
        response = request.execute()

        if response['items']:
            stats = response['items'][0]['statistics']
            views = int(stats.get('viewCount', 0))
            likes = int(stats.get('likeCount', 0))
            comments = int(stats.get('commentCount', 0))
            return views, likes, comments
        else:
            print(f"⚠️ Video with ID '{video_id}' not found.")
            return None, None, None

    except HttpError as e:
        print(f"❌ API error while fetching stats: {e}")
        return None, None, None


def update_video_title(youtube, video_id, views, likes, comments):
    """
    Update the video title with the latest stats.
    Preserves the original description, category, and tags.
    """
    try:
        # First, get the current snippet to keep description, tags, etc.
        video_info = youtube.videos().list(
            part='snippet',
            id=video_id
        ).execute()

        if not video_info['items']:
            print("❌ Could not retrieve current video snippet.")
            return

        snippet = video_info['items'][0]['snippet']

        # Build the new title
        new_title = (
            f"🎬 Views: {views:,} | ❤️ Likes: {likes:,} | 💬 Comments: {comments:,}"
        )

        # Prepare the update request
        update_body = {
            'id': video_id,
            'snippet': {
                'title': new_title,
                'description': snippet.get('description', ''),
                'categoryId': snippet.get('categoryId', '22'),
                'tags': snippet.get('tags', [])
            }
        }

        # Execute the update
        youtube.videos().update(
            part='snippet',
            body=update_body
        ).execute()

        # Log the successful update
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_msg = (f"{timestamp} ✅ Updated: views={views:,}, "
                   f"likes={likes:,}, comments={comments:,}")
        print(log_msg)

        # Also write to a log file (optional)
        with open('update_log.txt', 'a', encoding='utf-8') as log_file:
            log_file.write(log_msg + '\n')

    except HttpError as e:
        print(f"❌ API error while updating title: {e}")


def update_job():
    """
    Main background job: runs every UPDATE_INTERVAL_MINUTES minutes.
    Fetches stats and updates the video title.
    """
    # Authenticate once and reuse the service
    youtube = authenticate_youtube()
    print("✅ Authentication successful. Starting update loop...")

    while True:
        try:
            views, likes, comments = get_video_stats(youtube, VIDEO_ID)
            if views is not None:
                update_video_title(youtube, VIDEO_ID, views, likes, comments)
            else:
                print("⚠️ Skipping update because stats could not be fetched.")
        except Exception as e:
            print(f"⚠️ Unexpected error in update loop: {e}")

        # Wait for the next interval
        time.sleep(UPDATE_INTERVAL_MINUTES * 60)


@app.route('/')
def home():
    """
    Health check endpoint for Render / cron-job.org.
    Returns a simple status message.
    """
    return "✅ YouTube Title Updater is running!"


if __name__ == '__main__':
    # Start the update loop in a background thread
    # This allows the Flask web server to run concurrently
    thread = threading.Thread(target=update_job)
    thread.daemon = True
    thread.start()

    # Start the Flask web server (required for Render)
    # Render expects the app to listen on 0.0.0.0 and port 10000
    app.run(host='0.0.0.0', port=10000)
