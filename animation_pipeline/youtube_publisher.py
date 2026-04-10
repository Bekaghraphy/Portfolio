"""
Step 4 — YouTube Upload using YouTube Data API v3.

Authentication: OAuth 2.0 (client_secrets.json).
First run opens a browser for authorization; token is cached in youtube_token.json.
"""

import os
import time
from typing import List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from config import config
from script_generator import VideoScript


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
API_SERVICE = "youtube"
API_VERSION = "v3"

# Resumable upload chunk size (256 KB increments, 50 MB chunks)
CHUNK_SIZE = 50 * 1024 * 1024

# Retryable HTTP status codes
RETRYABLE_STATUS_CODES = {500, 502, 503, 504}
MAX_RETRIES = 5


def _get_authenticated_service():
    """Return an authenticated YouTube API service object."""
    creds: Optional[Credentials] = None

    if os.path.exists(config.youtube_credentials_file):
        creds = Credentials.from_authorized_user_file(
            config.youtube_credentials_file, SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.youtube_client_secrets_file, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(config.youtube_credentials_file, "w") as token_file:
            token_file.write(creds.to_json())

    return build(API_SERVICE, API_VERSION, credentials=creds)


def upload_to_youtube(
    video_path: str,
    script: VideoScript,
    privacy_status: str = "private",
    thumbnail_path: Optional[str] = None,
    category_id: str = "22",     # People & Blogs (27=Education)
    made_for_kids: bool = False,
) -> str:
    """
    Upload a video to YouTube with metadata from the script.

    Args:
        video_path: path to the MP4 file
        script: VideoScript with title, description, tags
        privacy_status: 'private' | 'unlisted' | 'public'
        thumbnail_path: optional JPG/PNG thumbnail
        category_id: YouTube category ID string
        made_for_kids: YouTube COPPA compliance flag

    Returns:
        YouTube video ID of the uploaded video.
    """
    youtube = _get_authenticated_service()

    body = {
        "snippet": {
            "title": script.title,
            "description": script.youtube_description,
            "tags": script.tags,
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": made_for_kids,
        },
    }

    media = MediaFileUpload(
        video_path,
        chunksize=CHUNK_SIZE,
        resumable=True,
        mimetype="video/mp4",
    )

    print(f"[YouTube] Uploading: {script.title}")
    print(f"[YouTube] Privacy: {privacy_status}")

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    video_id = _resumable_upload(request)

    # Set thumbnail if provided
    if thumbnail_path and os.path.exists(thumbnail_path) and video_id:
        _set_thumbnail(youtube, video_id, thumbnail_path)

    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"[YouTube] Upload complete: {url}")
    return video_id


def _resumable_upload(request) -> str:
    """Execute a resumable upload with exponential-backoff retry."""
    response = None
    error = None
    retry = 0

    while response is None:
        try:
            print("[YouTube] Uploading chunk ...", end=" ", flush=True)
            status, response = request.next_chunk()
            if status:
                pct = int(status.progress() * 100)
                print(f"\r[YouTube] Progress: {pct}%    ", end="", flush=True)
        except HttpError as exc:
            if exc.resp.status in RETRYABLE_STATUS_CODES:
                error = f"HTTP {exc.resp.status}"
            else:
                raise
        except Exception as exc:
            error = str(exc)

        if error:
            retry += 1
            if retry > MAX_RETRIES:
                raise RuntimeError(f"[YouTube] Upload failed after {MAX_RETRIES} retries: {error}")
            wait = 2 ** retry
            print(f"\n[YouTube] Retry {retry}/{MAX_RETRIES} in {wait}s — {error}")
            time.sleep(wait)
            error = None

    print()
    return response["id"]


def _set_thumbnail(youtube, video_id: str, thumbnail_path: str) -> None:
    """Upload a custom thumbnail for the video."""
    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_path),
        ).execute()
        print(f"[YouTube] Thumbnail set: {thumbnail_path}")
    except Exception as exc:
        print(f"[YouTube] WARNING — thumbnail upload failed: {exc}")
