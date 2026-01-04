"""
Data Preprocessing and Feature Engineering
Cleans raw data and creates 45+ features for model training
"""
import os
import sys
import pandas as pd
import numpy as np
import re
from datetime import datetime
import joblib
from pandas.api.types import is_numeric_dtype

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class DataPreprocessor:
    """Preprocesses and engineers features from raw YouTube data"""
    
    def __init__(self):
        self.feature_names = None
        
    def load_data(self, filepath):
        """Load raw data from CSV"""
        df = pd.read_csv(filepath)
        print(f"Loaded data: {df.shape}")
        return df
    
    def clean_data(self, df):
        """Clean raw data: handle missing values, outliers, etc."""
        print("\n=== Data Cleaning ===")
        original_shape = df.shape
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['video_id'], keep='first')
        print(f"After removing duplicates: {df.shape}")
        
        # Filter outliers: video duration (more lenient for real data)
        df = df[(df['duration_minutes'] >= 0.5) & (df['duration_minutes'] <= 480)]
        print(f"After filtering duration (0.5-180 min): {df.shape}")
        
        # Filter videos with zero views (likely errors or private videos)
        df = df[df['view_count'] > 0]
        print(f"After filtering zero views: {df.shape}")
        
        # Filter videos with zero first week views
        df = df[df['target_first_week_views'] > 0]
        print(f"After filtering zero first week views: {df.shape}")
        
        # Remove extreme outliers in target variable (using IQR method)
        if 'target_first_week_views' in df.columns:
            Q1 = df['target_first_week_views'].quantile(0.25)
            Q3 = df['target_first_week_views'].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 3 * IQR  # More lenient (3*IQR instead of 1.5*IQR)
            upper_bound = Q3 + 3 * IQR
            before_outlier = len(df)
            df = df[(df['target_first_week_views'] >= lower_bound) & 
                   (df['target_first_week_views'] <= upper_bound)]
            print(f"After removing extreme outliers in target: {df.shape} (removed {before_outlier - len(df)} rows)")
        
        # Handle missing values
        # Fill missing tags with empty string
        df['tags'] = df['tags'].fillna('')
        df['tag_count'] = df['tag_count'].fillna(0)
        
        # Fill missing description with empty string
        df['description'] = df['description'].fillna('')
        
        # Fill missing channel info with median (more robust)
        if 'channel_subscribers' in df.columns:
            median_subs = df['channel_subscribers'].median()
            df['channel_subscribers'] = df['channel_subscribers'].fillna(median_subs)
            # Cap extreme values
            p99 = df['channel_subscribers'].quantile(0.99)
            df['channel_subscribers'] = df['channel_subscribers'].clip(upper=p99 * 2)
        
        if 'channel_video_count' in df.columns:
            median_videos = df['channel_video_count'].median()
            df['channel_video_count'] = df['channel_video_count'].fillna(median_videos)
        
        if 'channel_view_count' in df.columns:
            median_views = df['channel_view_count'].median()
            df['channel_view_count'] = df['channel_view_count'].fillna(median_views)
        
        print(f"Final shape: {df.shape} (removed {original_shape[0] - df.shape[0]} rows)")
        return df
    
    def extract_title_features(self, title):
        """Extract features from video title"""
        if pd.isna(title) or title == '':
            title = ''
        
        title = str(title)
        
        features = {
            'title_length': len(title),
            'title_word_count': len(title.split()),
            'title_has_number': 1 if re.search(r'\d', title) else 0,
            'title_has_emoji': 1 if self._has_emoji(title) else 0,
            'title_has_question': 1 if '?' in title else 0,
            'title_has_exclamation': 1 if '!' in title else 0,
            'title_special_char_count': len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', title)),
            'title_is_tutorial': 1 if any(word in title.lower() for word in ['tutorial', 'how to', 'learn', 'guide', 'course']) else 0,
            'title_is_question': 1 if any(word in title.lower() for word in ['what', 'why', 'how', 'when', 'where', '?']) else 0,
            'title_uppercase_ratio': sum(1 for c in title if c.isupper()) / len(title) if len(title) > 0 else 0
        }
        
        return features
    
    def _has_emoji(self, text):
        """Check if text contains emoji"""
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE
        )
        return bool(emoji_pattern.search(text))
    
    def extract_time_features(self, df):
        """Extract time-based features"""
        df = df.copy()
        
        # Convert publish date to datetime (handle mixed formats & timezones)
        df['published_at'] = pd.to_datetime(
            df['published_at'],
            format='mixed',
            errors='coerce',
            utc=True
        )
        # Drop rows where conversion failed
        df = df.dropna(subset=['published_at'])
        
        # Day of week (0=Monday, 6=Sunday)
        df['publish_day_of_week'] = df['published_at'].dt.dayofweek
        
        # Is weekend
        df['is_weekend'] = (df['publish_day_of_week'] >= 5).astype(int)
        
        # Prime time (18:00-21:00)
        df['is_prime_time'] = ((df['publish_hour'] >= 18) & (df['publish_hour'] <= 21)).astype(int)
        
        # Time of day categories
        df['time_of_day'] = pd.cut(
            df['publish_hour'],
            bins=[-1, 6, 12, 18, 24],
            labels=['night', 'morning', 'afternoon', 'evening']
        )
        
        # Month
        df['publish_month'] = df['published_at'].dt.month
        
        return df
    
    def extract_duration_features(self, df):
        """Extract duration-based features"""
        df = df.copy()
        
        # Duration categories
        df['duration_category'] = pd.cut(
            df['duration_minutes'],
            bins=[0, 5, 10, 15, 30, 60, 480],
            labels=['very_short', 'short', 'medium', 'long', 'very_long', 'extended']
        )
        
        # Is short video (< 5 min)
        df['is_short_video'] = (df['duration_minutes'] < 5).astype(int)
        
        # Is medium video (5-15 min)
        df['is_medium_video'] = ((df['duration_minutes'] >= 5) & (df['duration_minutes'] <= 15)).astype(int)
        
        # Is long video (> 15 min)
        df['is_long_video'] = (df['duration_minutes'] > 15).astype(int)
        
        return df
    
    def extract_channel_features(self, df):
        """Extract channel-based features"""
        df = df.copy()
        
        # Channel size categories
        df['channel_size'] = pd.cut(
            df['channel_subscribers'],
            bins=[0, 10000, 100000, 1000000, float('inf')],
            labels=['small', 'medium', 'large', 'mega']
        )
        
        # Subscriber per video ratio
        df['subscribers_per_video'] = df['channel_subscribers'] / (df['channel_video_count'] + 1)
        
        # Engagement metrics (per 1000 views)
        df['likes_per_1k_views'] = (df['like_count'] / (df['view_count'] + 1)) * 1000
        df['comments_per_1k_views'] = (df['comment_count'] / (df['view_count'] + 1)) * 1000
        
        return df
    
    def extract_description_features(self, df):
        """Extract features from video description"""
        df = df.copy()
        
        df['description_length'] = df['description'].apply(lambda x: len(str(x)) if pd.notna(x) else 0)
        df['description_word_count'] = df['description'].apply(lambda x: len(str(x).split()) if pd.notna(x) else 0)
        df['description_has_url'] = df['description'].apply(lambda x: 1 if 'http' in str(x).lower() else 0)
        
        return df
    
    def engineer_features(self, df):
        """Main feature engineering function"""
        print("\n=== Feature Engineering ===")

        # Ensure stable, aligned indices before any concat/apply operations
        df = df.reset_index(drop=True).copy()
        
        # Extract title features
        print("Extracting title features...")
        title_features = df['title'].apply(self.extract_title_features)
        title_df = pd.DataFrame(list(title_features)).reset_index(drop=True)
        df = pd.concat([df, title_df], axis=1)
        
        # Time features
        print("Extracting time features...")
        df = self.extract_time_features(df)
        
        # Duration features
        print("Extracting duration features...")
        df = self.extract_duration_features(df)
        
        # Channel features
        print("Extracting channel features...")
        df = self.extract_channel_features(df)
        
        # Description features
        print("Extracting description features...")
        df = self.extract_description_features(df)
        
        print(f"Total features after basic engineering: {df.shape[1]}")
        
        # Apply advanced feature engineering
        try:
            from src.advanced_feature_engineering import AdvancedFeatureEngineer
            print("\nApplying advanced feature engineering...")
            advanced_engineer = AdvancedFeatureEngineer()
            df = advanced_engineer.engineer_all_features(df)
        except Exception as e:
            print(f"Warning: Advanced feature engineering failed: {e}")
            print("Continuing with basic features only...")
        
        print(f"Total features after all engineering: {df.shape[1]}")
        return df
    
    def encode_categorical_features(self, df):
        """One-hot encode categorical features"""
        print("\n=== Encoding Categorical Features ===")
        
        categorical_cols = ['publish_day', 'time_of_day', 'duration_category', 'channel_size']
        
        # Only encode columns that exist
        categorical_cols = [col for col in categorical_cols if col in df.columns]
        
        # One-hot encoding
        df_encoded = pd.get_dummies(df, columns=categorical_cols, prefix=categorical_cols, drop_first=True)
        
        print(f"Features after encoding: {df_encoded.shape[1]}")
        return df_encoded
    
    def select_features(self, df, target_col='target_first_week_views'):
        """Select features for model training"""
        print("\n=== Feature Selection ===")
        
        # Exclude non-feature columns
        exclude_cols = [
            'video_id', 'title', 'description', 'channel_id', 'channel_name',
            'published_at', 'category_id', 'tags', 'default_language',
            'default_audio_language', 'publish_day', 'time_of_day',
            'duration_category', 'channel_size', target_col
        ]
        
        # Keep all numeric features (including uint8 from one-hot encoding)
        feature_cols = [
            col for col in df.columns
            if col not in exclude_cols and is_numeric_dtype(df[col])
        ]
        
        # Ensure target is included
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in dataframe")
        
        X = df[feature_cols]
        y = df[target_col]
        
        # Remove any columns with all NaN values
        X = X.dropna(axis=1, how='all')
        
        # Fill remaining NaN with 0
        X = X.fillna(0)
        
        print(f"Selected {len(X.columns)} features")
        print(f"Feature names: {list(X.columns)}")
        
        self.feature_names = list(X.columns)
        
        return X, y
    
    def preprocess(self, input_path, output_path='processed_data/youtube_videos_processed.csv'):
        """Complete preprocessing pipeline"""
        print("=" * 60)
        print("DATA PREPROCESSING PIPELINE")
        print("=" * 60)
        
        # Load data
        df = self.load_data(input_path)
        
        # Clean data
        df = self.clean_data(df)
        
        # Engineer features
        df = self.engineer_features(df)
        
        # Encode categorical
        df = self.encode_categorical_features(df)
        
        # Save processed data
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\nProcessed data saved to: {output_path}")
        
        return df


def main():
    """Main execution function"""
    preprocessor = DataPreprocessor()
    
    input_path = 'raw_data/youtube_videos_raw.csv'
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        print("Please run data_collection.py first to collect data.")
        return
    
    df = preprocessor.preprocess(input_path)
    
    # Select features for model
    X, y = preprocessor.select_features(df)
    
    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETE")
    print("=" * 60)
    print(f"Final dataset shape: {X.shape}")
    print(f"Target statistics:")
    print(y.describe())


if __name__ == '__main__':
    main()


