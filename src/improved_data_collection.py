"""
Improved Data Collection with Better Quality Control
Collects more data and filters for quality
"""
import os
import sys
import time
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collection import YouTubeDataCollector
from src.config import YOUTUBE_API_KEY, TARGET_CHANNELS, MAX_VIDEOS_PER_CHANNEL


class ImprovedDataCollector(YouTubeDataCollector):
    """Improved data collector with better filtering and quality control"""
    
    def filter_quality_videos(self, videos):
        """Filter videos for quality - remove low-quality or outlier videos"""
        if not videos:
            return videos
        
        df = pd.DataFrame(videos)
        
        # Filter out videos with suspicious metrics
        # Very high view count but low engagement might be bot traffic
        if 'like_count' in df.columns and 'view_count' in df.columns:
            df['engagement_ratio'] = df['like_count'] / (df['view_count'] + 1)
            # Remove videos with suspiciously low engagement (< 0.1% like rate)
            df = df[df['engagement_ratio'] > 0.001]
        
        # Remove videos that are too old (might have different patterns)
        if 'published_at' in df.columns:
            df['published_at'] = pd.to_datetime(df['published_at'])
            # Ensure timezone-aware comparison
            if df['published_at'].dt.tz is not None:
                # If published_at is timezone-aware, make cutoff_date timezone-aware too
                from datetime import timezone
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=1095)  # Last 3 years
            else:
                # If published_at is timezone-naive, keep cutoff_date naive
                cutoff_date = datetime.now() - timedelta(days=1095)  # Last 3 years
            df = df[df['published_at'] >= cutoff_date]
        
        # Remove videos with extreme durations
        if 'duration_minutes' in df.columns:
            df = df[(df['duration_minutes'] >= 0.5) & (df['duration_minutes'] <= 180)]
        
        return df.to_dict('records')
    
    def collect_all_data(self):
        """Collect data with improved quality control"""
        print("Starting IMPROVED data collection from YouTube API...")
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
            
            # Filter for quality
            videos = self.filter_quality_videos(videos)
            print(f"  After quality filter: {len(videos)} videos")
            
            # Add channel info to each video
            for video in videos:
                video.update({
                    'channel_subscribers': channel_info['channel_subscribers'],
                    'channel_video_count': channel_info['channel_video_count'],
                    'channel_view_count': channel_info['channel_view_count']
                })
                
                # Calculate first week views (improved method)
                video['target_first_week_views'] = self.calculate_first_week_views(video)
            
            all_videos.extend(videos)
            
            # Rate limiting between channels
            time.sleep(1)
        
        print(f"\n\nTotal videos collected: {len(all_videos)}")
        return all_videos


def main():
    """Main execution function"""
    if not YOUTUBE_API_KEY:
        print("ERROR: YOUTUBE_API_KEY not found in environment variables.")
        print("Please create a .env file with your YouTube API key.")
        return
    
    collector = ImprovedDataCollector(YOUTUBE_API_KEY)
    videos_data = collector.collect_all_data()
    
    if videos_data:
        df = collector.save_data(videos_data, 'raw_data/youtube_videos_raw.csv')
        print("\nImproved data collection completed successfully!")
        print(f"\nSample data:")
        print(df[['title', 'duration_minutes', 'channel_subscribers', 'target_first_week_views']].head(10))
        print(f"\nData quality statistics:")
        print(f"  Average first week views: {df['target_first_week_views'].mean():,.0f}")
        print(f"  Median first week views: {df['target_first_week_views'].median():,.0f}")
        print(f"  Std first week views: {df['target_first_week_views'].std():,.0f}")
    else:
        print("No data collected. Please check your API key and network connection.")


if __name__ == '__main__':
    main()

