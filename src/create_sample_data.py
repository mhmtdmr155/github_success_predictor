"""
Create Sample Data for Testing
Creates synthetic YouTube video data for model training without API
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_sample_data(num_videos=500):
    """Create sample YouTube video data"""
    print(f"Creating {num_videos} sample videos...")
    
    # Channel names
    channels = [
        'freeCodeCamp.org', 'Programming with Mosh', 'The Net Ninja',
        'Fireship', 'Traversy Media', 'Corey Schafer', 'Sentdex',
        'Derek Banas', 'TechWorld with Nana', 'Web Dev Simplified'
    ]
    
    # Video categories
    categories = ['Education', 'Technology', 'Programming', 'Tutorial']
    
    # Sample titles
    title_templates = [
        "Python {} Tutorial - {}",
        "Learn {} in {} Minutes",
        "{} for Beginners - Complete Guide",
        "{} Explained - {} Tips",
        "How to {} in {} Steps",
        "{} Masterclass - {}",
        "{} Crash Course - {}",
        "{} Best Practices - {}",
        "{} vs {} - Comparison",
        "{} Advanced Techniques - {}"
    ]
    
    topics = ['JavaScript', 'Python', 'React', 'Node.js', 'Django', 'Flask',
              'Machine Learning', 'Web Development', 'Data Science', 'AI']
    
    videos = []
    
    for i in range(num_videos):
        # Channel info
        channel_name = random.choice(channels)
        channel_subscribers = random.randint(10000, 5000000)
        channel_video_count = random.randint(50, 1000)
        channel_view_count = channel_subscribers * random.randint(10, 100)
        
        # Video title
        template = random.choice(title_templates)
        topic1 = random.choice(topics)
        topic2 = random.choice(topics)
        num = random.randint(5, 30)
        title = template.format(topic1, num if '{}' in template else topic2)
        
        # Add emoji sometimes
        if random.random() < 0.3:
            emojis = ['🔥', '💡', '🚀', '⚡', '⭐', '🎯']
            title = f"{random.choice(emojis)} {title}"
        
        # Add number sometimes
        if random.random() < 0.4 and '{}' not in template:
            title = f"{random.randint(5, 20)} {title}"
        
        # Video duration
        duration_minutes = random.choice([
            random.uniform(3, 8),      # Short
            random.uniform(8, 15),     # Medium
            random.uniform(15, 30),    # Long
            random.uniform(30, 60),    # Very long
            random.uniform(60, 120)    # Extended
        ])
        duration_seconds = duration_minutes * 60
        
        # Publish date (random date in last 2 years)
        days_ago = random.randint(1, 730)
        publish_date = datetime.now() - timedelta(days=days_ago)
        publish_day = publish_date.strftime('%A')
        publish_hour = random.randint(0, 23)
        
        # Tags
        tag_count = random.randint(3, 15)
        tags = ','.join(random.sample(topics, min(tag_count, len(topics))))
        
        # Description
        description_length = random.randint(100, 1000)
        description = f"This is a tutorial about {topic1}. " * (description_length // 30)
        
        # Engagement metrics (based on subscribers and other factors)
        base_views = channel_subscribers * random.uniform(0.01, 0.5)
        
        # Factor in prime time
        if 18 <= publish_hour <= 21:
            base_views *= 1.25
        
        # Factor in title length (optimal 50-60 chars)
        title_len = len(title)
        if 50 <= title_len <= 60:
            base_views *= 1.18
        elif title_len > 70:
            base_views *= 0.9
        
        # Factor in duration (optimal 10-15 min)
        if 10 <= duration_minutes <= 15:
            base_views *= 1.15
        elif duration_minutes > 30:
            base_views *= 0.85
        
        # Factor in weekend
        if publish_date.weekday() >= 5:
            base_views *= 0.95
        
        # Add randomness
        view_count = int(base_views * random.uniform(0.5, 1.5))
        view_count = max(100, view_count)  # Minimum 100 views
        
        # First week views (typically 30-50% of total)
        first_week_ratio = random.uniform(0.3, 0.5)
        if days_ago < 7:
            first_week_views = view_count
        else:
            first_week_views = int(view_count * first_week_ratio)
        
        # Engagement metrics
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
            'category_id': '27',  # Education
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


def main():
    """Main function"""
    print("=" * 60)
    print("CREATING SAMPLE DATA FOR TESTING")
    print("=" * 60)
    
    # Create sample data
    df = create_sample_data(num_videos=500)
    
    # Save to CSV
    output_path = 'raw_data/youtube_videos_raw.csv'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"\n✅ Sample data created: {output_path}")
    print(f"   Shape: {df.shape}")
    print(f"\nSample data:")
    print(df[['title', 'duration_minutes', 'channel_subscribers', 'target_first_week_views']].head())
    print(f"\n📊 Statistics:")
    print(f"   Average first week views: {df['target_first_week_views'].mean():,.0f}")
    print(f"   Min first week views: {df['target_first_week_views'].min():,.0f}")
    print(f"   Max first week views: {df['target_first_week_views'].max():,.0f}")
    print("\n✅ Next step: Run data_preprocessing.py")


if __name__ == '__main__':
    main()

