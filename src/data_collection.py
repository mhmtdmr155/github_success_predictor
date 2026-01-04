"""
YouTube Data Collection Script
Collects video data from target channels using YouTube Data API v3
"""
import os
import sys
import json
import time
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import (
    YOUTUBE_API_KEY,
    TARGET_CHANNELS,
    MAX_VIDEOS_PER_CHANNEL,
    MAX_RESULTS_PER_REQUEST
)


class YouTubeDataCollector:
    """Collects video data from YouTube channels"""
    
    def __init__(self, api_key):
        """Initialize YouTube API client"""
        if not api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY in .env file")
        
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.videos_data = []
        
    def get_channel_info(self, channel_id):
        """Get channel information"""
        try:
            request = self.youtube.channels().list(
                part='snippet,statistics',
                id=channel_id
            )
            response = request.execute()
            
            # Check if response has items and is not empty
            if 'items' in response and response['items']:
                channel = response['items'][0]
                return {
                    'channel_id': channel_id,
                    'channel_name': channel['snippet']['title'],
                    'channel_subscribers': int(channel['statistics'].get('subscriberCount', 0)),
                    'channel_video_count': int(channel['statistics'].get('videoCount', 0)),
                    'channel_view_count': int(channel['statistics'].get('viewCount', 0))
                }
            else:
                # Check for errors in response
                if 'error' in response:
                    print(f"API Error for channel {channel_id}: {response['error']}")
                else:
                    print(f"No items found for channel {channel_id}")
        except HttpError as e:
            print(f"Error fetching channel info for {channel_id}: {e}")
        except KeyError as e:
            print(f"KeyError fetching channel info for {channel_id}: {e}")
            print(f"Response keys: {list(response.keys()) if 'response' in locals() else 'No response'}")
        except Exception as e:
            print(f"Unexpected error fetching channel info for {channel_id}: {e}")
        return None
    
    def get_channel_videos(self, channel_id, max_results=50):
        """Get videos from a channel"""
        videos = []
        try:
            # Get uploads playlist ID
            request = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            )
            response = request.execute()
            
            if not response['items']:
                return videos
            
            uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from playlist
            next_page_token = None
            collected = 0
            
            while collected < max_results:
                request = self.youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId=uploads_playlist_id,
                    maxResults=min(MAX_RESULTS_PER_REQUEST, max_results - collected),
                    pageToken=next_page_token
                )
                response = request.execute()
                
                video_ids = [item['contentDetails']['videoId'] for item in response['items']]
                
                # Get detailed video information
                if video_ids:
                    video_details = self.get_video_details(video_ids)
                    videos.extend(video_details)
                    collected += len(video_details)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                # Rate limiting
                time.sleep(0.1)
                
        except HttpError as e:
            print(f"Error fetching videos for channel {channel_id}: {e}")
        
        return videos[:max_results]
    
    def get_video_details(self, video_ids):
        """Get detailed information for video IDs"""
        videos = []
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)
            )
            response = request.execute()
            
            for item in response['items']:
                snippet = item['snippet']
                stats = item['statistics']
                content = item['contentDetails']
                
                # Parse duration (ISO 8601 format)
                duration_str = content.get('duration', 'PT0S')
                duration_seconds = self.parse_duration(duration_str)
                duration_minutes = duration_seconds / 60
                
                # Parse publish date
                publish_date = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                
                video_data = {
                    'video_id': item['id'],
                    'title': snippet.get('title', ''),
                    'description': snippet.get('description', ''),
                    'channel_id': snippet.get('channelId', ''),
                    'channel_name': snippet.get('channelTitle', ''),
                    'published_at': publish_date.isoformat(),
                    'publish_day': publish_date.strftime('%A'),
                    'publish_hour': publish_date.hour,
                    'category_id': snippet.get('categoryId', ''),
                    'tags': ','.join(snippet.get('tags', [])),
                    'tag_count': len(snippet.get('tags', [])),
                    'duration_seconds': duration_seconds,
                    'duration_minutes': duration_minutes,
                    'view_count': int(stats.get('viewCount', 0)),
                    'like_count': int(stats.get('likeCount', 0)),
                    'comment_count': int(stats.get('commentCount', 0)),
                    'default_language': snippet.get('defaultLanguage', ''),
                    'default_audio_language': snippet.get('defaultAudioLanguage', '')
                }
                
                videos.append(video_data)
                
        except HttpError as e:
            print(f"Error fetching video details: {e}")
        
        return videos
    
    def parse_duration(self, duration_str):
        """Parse ISO 8601 duration string to seconds"""
        import re
        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def calculate_first_week_views(self, video_data, current_date=None):
        """Calculate views in first 7 days using improved heuristics"""
        # Note: YouTube API doesn't provide historical view counts
        # Using improved heuristics based on video age and engagement patterns
        if current_date is None:
            current_date = datetime.now()
        
        # Handle both string and Timestamp formats
        published_at = video_data['published_at']
        if isinstance(published_at, str):
            publish_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        else:
            # It's already a Timestamp/datetime object
            from pandas import to_datetime
            publish_date = to_datetime(published_at).to_pydatetime()
        
        # Remove timezone for comparison
        if publish_date.tzinfo is not None:
            publish_date = publish_date.replace(tzinfo=None)
        
        days_since_publish = (current_date - publish_date).days
        
        view_count = video_data['view_count']
        
        if days_since_publish < 7:
            # If video is less than 7 days old, use current views
            return view_count
        elif days_since_publish < 30:
            # Videos 7-30 days old: first week typically 40-60% of current views
            # Newer videos get more views in first week
            ratio = 0.6 - (days_since_publish - 7) * 0.01  # Decreasing ratio
            return int(view_count * ratio)
        elif days_since_publish < 90:
            # Videos 30-90 days old: first week typically 25-40% of current views
            ratio = 0.4 - (days_since_publish - 30) * 0.002
            return int(view_count * ratio)
        elif days_since_publish < 365:
            # Videos 90-365 days old: first week typically 15-25% of current views
            ratio = 0.25 - (days_since_publish - 90) * 0.0004
            return int(view_count * ratio)
        else:
            # Older videos: first week typically 10-15% of total views
            # But adjust based on channel size and video performance
            channel_subs = video_data.get('channel_subscribers', 100000)
            
            # Larger channels tend to get more views early on
            if channel_subs > 1000000:
                base_ratio = 0.15
            elif channel_subs > 100000:
                base_ratio = 0.12
            else:
                base_ratio = 0.10
            
            # Adjust based on engagement (likes/views ratio)
            like_count = video_data.get('like_count', 0)
            if view_count > 0:
                engagement_ratio = like_count / view_count
                # Higher engagement = more early views
                if engagement_ratio > 0.05:
                    base_ratio *= 1.3
                elif engagement_ratio > 0.03:
                    base_ratio *= 1.1
            
            # Adjust based on video age (older videos have lower ratio)
            age_factor = max(0.5, 1.0 - (days_since_publish - 365) / 1000)
            final_ratio = base_ratio * age_factor
            
            return int(view_count * final_ratio)
    
    def collect_all_data(self):
        """Collect data from all target channels"""
        print("Starting data collection from YouTube API...")
        print(f"Target channels: {len(TARGET_CHANNELS)}")
        print(f"Max videos per channel: {MAX_VIDEOS_PER_CHANNEL}\n")
        
        all_videos = []
        
        for channel_id in tqdm(TARGET_CHANNELS, desc="Channels"):
            print(f"\nCollecting from channel: {channel_id}")
            
            # Get channel info
            channel_info = self.get_channel_info(channel_id)
            if not channel_info:
                print(f"  Skipping channel {channel_id} - could not fetch info")
                continue
            
            print(f"  Channel: {channel_info['channel_name']}")
            print(f"  Subscribers: {channel_info['channel_subscribers']:,}")
            
            # Get videos
            videos = self.get_channel_videos(channel_id, MAX_VIDEOS_PER_CHANNEL)
            print(f"  Collected {len(videos)} videos")
            
            # Add channel info to each video
            for video in videos:
                video.update({
                    'channel_subscribers': channel_info['channel_subscribers'],
                    'channel_video_count': channel_info['channel_video_count'],
                    'channel_view_count': channel_info['channel_view_count']
                })
                
                # Calculate first week views (simplified)
                video['target_first_week_views'] = self.calculate_first_week_views(video)
            
            all_videos.extend(videos)
            
            # Rate limiting between channels
            time.sleep(1)
        
        print(f"\n\nTotal videos collected: {len(all_videos)}")
        return all_videos
    
    def save_data(self, videos_data, output_path='raw_data/youtube_videos_raw.csv'):
        """Save collected data to CSV"""
        df = pd.DataFrame(videos_data)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\nData saved to: {output_path}")
        print(f"Shape: {df.shape}")
        return df


def main():
    """Main execution function"""
    if not YOUTUBE_API_KEY:
        print("ERROR: YOUTUBE_API_KEY not found in environment variables.")
        print("Please create a .env file with your YouTube API key.")
        print("Get your API key from: https://console.cloud.google.com/apis/credentials")
        return
    
    collector = YouTubeDataCollector(YOUTUBE_API_KEY)
    videos_data = collector.collect_all_data()
    
    if videos_data:
        df = collector.save_data(videos_data)
        print("\nData collection completed successfully!")
        print(f"\nSample data:")
        print(df.head())
    else:
        print("No data collected. Please check your API key and network connection.")


if __name__ == '__main__':
    main()


