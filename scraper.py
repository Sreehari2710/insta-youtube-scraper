from dotenv import load_dotenv
import os
import instaloader
import re
import requests

load_dotenv()

# --- Instagram ---
def fetch_instagram_data(reel_link):
    loader = instaloader.Instaloader()
    shortcode = reel_link.split("/")[-2]
    post = instaloader.Post.from_shortcode(loader.context, shortcode)
    profile = post.owner_profile

    return {
        "Platform": "Instagram",
        "ReelLink": reel_link,
        "Username": profile.username,
        "ProfileLink": f"https://instagram.com/{profile.username}",
        "Followers": profile.followers,
        "Likes": post.likes,
        "Comments": post.comments,
        "Views": post.video_view_count if post.is_video else None,
        "Shares": "N/A"
    }

# --- YouTube ---
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  
YOUTUBE_VIDEO_API = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_API = "https://www.googleapis.com/youtube/v3/channels"

def fetch_youtube_data(video_link):
    # Extract video ID
    match = re.search(r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})", video_link)
    if not match:
        return {"ReelLink": video_link, "Error": "Invalid YouTube link"}
    video_id = match.group(1)

    # Fetch video details
    video_resp = requests.get(YOUTUBE_VIDEO_API, params={
        "part": "snippet,statistics",
        "id": video_id,
        "key": YOUTUBE_API_KEY
    }).json()

    if not video_resp.get("items"):
        return {"ReelLink": video_link, "Error": "Video not found"}

    video_data = video_resp["items"][0]
    snippet = video_data["snippet"]
    stats = video_data["statistics"]

    channel_id = snippet["channelId"]

    # Fetch channel details
    channel_resp = requests.get(YOUTUBE_CHANNEL_API, params={
        "part": "snippet,statistics",
        "id": channel_id,
        "key": YOUTUBE_API_KEY
    }).json()

    channel = channel_resp["items"][0]
    channel_name = channel["snippet"]["title"]
    subscribers = channel["statistics"].get("subscriberCount", "N/A")

    return {
        "Platform": "YouTube",
        "ReelLink": video_link,
        "Username": channel_name,
        "ProfileLink": f"https://youtube.com/channel/{channel_id}",
        "Followers": subscribers,
        "Likes": stats.get("likeCount", "N/A"),
        "Comments": stats.get("commentCount", "N/A"),
        "Views": stats.get("viewCount", "N/A"),
        "Shares": "N/A"
    }

# --- Unified Handler ---
def fetch_reel_data(link):
    try:
        if "instagram.com" in link:
            return fetch_instagram_data(link)
        elif "youtube.com" in link or "youtu.be" in link:
            return fetch_youtube_data(link)
        else:
            return {"ReelLink": link, "Error": "Unsupported platform"}
    except Exception as e:
        return {"ReelLink": link, "Error": str(e)}
