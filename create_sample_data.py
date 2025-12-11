"""
Create Sample Data for Testing - Standalone Script
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random


def create_sample_data(num_videos=500):
    """Create sample YouTube video data"""
    print(f"Creating {num_videos} sample videos...")
    
    channels = [
        'freeCodeCamp.org', 'Programming with Mosh', 'The Net Ninja',
        'Fireship', 'Traversy Media', 'Corey Schafer', 'Sentdex',
        'Derek Banas', 'TechWorld with Nana', 'Web Dev Simplified'
    ]
    
    title_templates = [
        "Python {} Tutorial - {}",
        "Learn {} in {} Minutes",
        "{} for Beginners - Complete Guide",
        "{} Explained - {} Tips",
        "How to {} in {} Steps",
    ]
    
    topics = ['JavaScript', 'Python', 'React', 'Node.js', 'Django', 'Flask',
              'Machine Learning', 'Web Development', 'Data Science', 'AI']
    
    videos = []
    
    for i in range(num_videos):
        channel_name = random.choice(channels)
        channel_subscribers = random.randint(10000, 5000000)
        channel_video_count = random.randint(50, 1000)
        channel_view_count = channel_subscribers * random.randint(10, 100)
        
        template = random.choice(title_templates)
        topic1 = random.choice(topics)
        topic2 = random.choice(topics)
        num = random.randint(5, 30)
        title = template.format(topic1, num if '{}' in template else topic2)
        
        if random.random() < 0.3:
            emojis = ['🔥', '💡', '🚀', '⚡']
            title = f"{random.choice(emojis)} {title}"
        
        if random.random() < 0.4 and '{}' not in template:
            title = f"{random.randint(5, 20)} {title}"
        
        duration_minutes = random.choice([
            random.uniform(3, 8),
            random.uniform(8, 15),
            random.uniform(15, 30),
            random.uniform(30, 60),
        ])
        duration_seconds = duration_minutes * 60
        
        days_ago = random.randint(1, 730)
        publish_date = datetime.now() - timedelta(days=days_ago)
        publish_day = publish_date.strftime('%A')
        publish_hour = random.randint(0, 23)
        
        tag_count = random.randint(3, 15)
        tags = ','.join(random.sample(topics, min(tag_count, len(topics))))
        
        description = f"This is a tutorial about {topic1}. " * 20
        
        base_views = channel_subscribers * random.uniform(0.01, 0.5)
        
        if 18 <= publish_hour <= 21:
            base_views *= 1.25
        
        title_len = len(title)
        if 50 <= title_len <= 60:
            base_views *= 1.18
        elif title_len > 70:
            base_views *= 0.9
        
        if 10 <= duration_minutes <= 15:
            base_views *= 1.15
        elif duration_minutes > 30:
            base_views *= 0.85
        
        if publish_date.weekday() >= 5:
            base_views *= 0.95
        
        view_count = int(base_views * random.uniform(0.5, 1.5))
        view_count = max(100, view_count)
        
        first_week_ratio = random.uniform(0.3, 0.5)
        if days_ago < 7:
            first_week_views = view_count
        else:
            first_week_views = int(view_count * first_week_ratio)
        
        like_count = int(view_count * random.uniform(0.02, 0.05))
        comment_count = int(view_count * random.uniform(0.001, 0.005))
        
        video_data = {
            'video_id': f'video_{i:04d}',
            'title': title,
            'description': description,
            'channel_id': f'channel_{channels.index(channel_name)}',
            'channel_name': channel_name,
            'published_at': publish_date.isoformat(),
            'publish_day': publish_day,
            'publish_hour': publish_hour,
            'category_id': '27',
            'tags': tags,
            'tag_count': tag_count,
            'duration_seconds': int(duration_seconds),
            'duration_minutes': round(duration_minutes, 2),
            'view_count': view_count,
            'like_count': like_count,
            'comment_count': comment_count,
            'default_language': 'en',
            'default_audio_language': 'en',
            'channel_subscribers': channel_subscribers,
            'channel_video_count': channel_video_count,
            'channel_view_count': channel_view_count,
            'target_first_week_views': first_week_views
        }
        
        videos.append(video_data)
    
    df = pd.DataFrame(videos)
    return df


if __name__ == '__main__':
    print("=" * 60)
    print("CREATING SAMPLE DATA FOR TESTING")
    print("=" * 60)
    
    df = create_sample_data(num_videos=500)
    
    output_path = 'raw_data/youtube_videos_raw.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"\n[OK] Sample data created: {output_path}")
    print(f"   Shape: {df.shape}")
    print(f"\nSample statistics:")
    print(f"   Average first week views: {df['target_first_week_views'].mean():,.0f}")
    print(f"   Min: {df['target_first_week_views'].min():,.0f}")
    print(f"   Max: {df['target_first_week_views'].max():,.0f}")
    print(f"   Average duration: {df['duration_minutes'].mean():.1f} minutes")
    print(f"   Average subscribers: {df['channel_subscribers'].mean():,.0f}")
    print("\n[OK] Next step: Run data_preprocessing.py")

