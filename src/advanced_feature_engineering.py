"""
Advanced Feature Engineering
Creates more sophisticated features for better model performance
"""
import pandas as pd
import numpy as np
import re
from datetime import datetime
from pandas.api.types import is_numeric_dtype


class AdvancedFeatureEngineer:
    """Advanced feature engineering for YouTube video success prediction"""
    
    def __init__(self):
        pass

    def _sanitize_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Replace inf with NaN and fill NaN with 0 ONLY for numeric columns.
        (Categorical columns like 'channel_size' cannot accept fillna(0).)
        """
        df = df.copy()
        df = df.replace([np.inf, -np.inf], np.nan)
        numeric_cols = [c for c in df.columns if is_numeric_dtype(df[c])]
        if numeric_cols:
            df[numeric_cols] = df[numeric_cols].fillna(0)
        return df
    
    def create_interaction_features(self, df):
        """Create interaction features between important variables"""
        df = self._sanitize_numeric(df)
        
        # Title length × Channel subscribers (bigger channels benefit more from good titles)
        df['title_length_x_subscribers'] = df['title_length'] * np.log1p(df['channel_subscribers'])
        
        # Duration × Prime time (prime time + optimal duration)
        df['duration_x_prime_time'] = df['duration_minutes'] * df['is_prime_time']
        
        # Title quality × Channel size (quality matters more for smaller channels)
        title_quality = (
            pd.to_numeric(df.get('title_is_tutorial', 0), errors='coerce').fillna(0).astype(int)
            + pd.to_numeric(df.get('title_has_number', 0), errors='coerce').fillna(0).astype(int)
            + pd.to_numeric(df.get('title_is_question', 0), errors='coerce').fillna(0).astype(int)
        )
        df['title_quality_x_channel_size'] = title_quality * np.log1p(df['channel_subscribers'])
        
        # Weekend × Prime time (weekend prime time might be different)
        df['weekend_x_prime_time'] = df['is_weekend'] * df['is_prime_time']
        
        # Duration × Channel subscribers (optimal duration might vary by channel size)
        df['duration_x_channel_size'] = df['duration_minutes'] * np.log1p(df['channel_subscribers'])
        
        # Tag count × Title length (more tags + longer title = better SEO)
        df['tag_count_x_title_length'] = df['tag_count'] * df['title_length']
        
        # Description length × Tag count (comprehensive content)
        df['description_length_x_tags'] = df['description_length'] * df['tag_count']
        
        return df
    
    def create_polynomial_features(self, df):
        """Create polynomial features for non-linear relationships"""
        df = self._sanitize_numeric(df)
        
        # Square of important features
        df['title_length_squared'] = df['title_length'] ** 2
        df['duration_minutes_squared'] = df['duration_minutes'] ** 2
        df['channel_subscribers_log'] = np.log1p(df['channel_subscribers'])
        df['channel_subscribers_sqrt'] = np.sqrt(df['channel_subscribers'])
        
        # Cube root for highly skewed features
        df['channel_subscribers_cbrt'] = np.cbrt(df['channel_subscribers'])
        
        return df
    
    def create_ratio_features(self, df):
        """Create ratio features"""
        df = self._sanitize_numeric(df)
        
        # Title length to word count ratio (word density)
        df['title_length_to_words'] = df['title_length'] / (df['title_word_count'] + 1)
        
        # Description to title length ratio
        df['description_to_title_ratio'] = df['description_length'] / (df['title_length'] + 1)
        
        # Tag count to title length ratio
        df['tags_to_title_ratio'] = df['tag_count'] / (df['title_length'] + 1)
        
        # Video count to subscribers ratio (content frequency)
        df['video_frequency'] = df['channel_video_count'] / (np.log1p(df['channel_subscribers']) + 1)
        
        return df
    
    def create_time_features(self, df):
        """Create advanced time-based features"""
        df = self._sanitize_numeric(df)
        
        # Convert publish date to datetime if not already
        if 'published_at' in df.columns:
            df['published_at'] = pd.to_datetime(df['published_at'])
            
            # Day of month
            df['publish_day_of_month'] = df['published_at'].dt.day
            
            # Week of year
            df['publish_week_of_year'] = df['published_at'].dt.isocalendar().week
            
            # Quarter
            df['publish_quarter'] = df['published_at'].dt.quarter
            
            # Is month end (videos at month end might perform differently)
            df['is_month_end'] = (df['published_at'].dt.day > 25).astype(int)
            
            # Is month start
            df['is_month_start'] = (df['published_at'].dt.day <= 7).astype(int)
        
        # Hour squared (non-linear relationship with hour)
        df['publish_hour_squared'] = df['publish_hour'] ** 2
        
        # Sin/Cos encoding for cyclical time features
        df['publish_hour_sin'] = np.sin(2 * np.pi * df['publish_hour'] / 24)
        df['publish_hour_cos'] = np.cos(2 * np.pi * df['publish_hour'] / 24)
        df['publish_day_of_week_sin'] = np.sin(2 * np.pi * df['publish_day_of_week'] / 7)
        df['publish_day_of_week_cos'] = np.cos(2 * np.pi * df['publish_day_of_week'] / 7)
        
        return df
    
    def create_title_advanced_features(self, df):
        """Create advanced title analysis features"""
        df = self._sanitize_numeric(df)
        
        # Title sentiment indicators
        positive_words = ['best', 'top', 'amazing', 'awesome', 'great', 'ultimate', 'complete', 'perfect']
        negative_words = ['worst', 'bad', 'terrible', 'avoid', 'never', 'don\'t', 'stop']
        
        df['title_positive_words'] = df['title'].apply(
            lambda x: sum(1 for word in positive_words if word in str(x).lower())
        )
        df['title_negative_words'] = df['title'].apply(
            lambda x: sum(1 for word in negative_words if word in str(x).lower())
        )
        
        # Title contains power words
        power_words = ['secret', 'hack', 'trick', 'method', 'system', 'guide', 'tutorial', 'learn', 'master']
        df['title_power_words'] = df['title'].apply(
            lambda x: sum(1 for word in power_words if word in str(x).lower())
        )
        
        # Title contains numbers in different formats
        df['title_has_digit'] = df['title'].apply(lambda x: 1 if re.search(r'\d', str(x)) else 0)
        df['title_number_count'] = df['title'].apply(lambda x: len(re.findall(r'\d+', str(x))))
        
        # Title capitalization patterns
        df['title_starts_with_capital'] = df['title'].apply(
            lambda x: 1 if len(str(x)) > 0 and str(x)[0].isupper() else 0
        )
        
        # Title has colon (common in tutorial videos)
        df['title_has_colon'] = df['title'].apply(lambda x: 1 if ':' in str(x) else 0)
        
        # Title has dash or pipe
        df['title_has_dash'] = df['title'].apply(lambda x: 1 if '-' in str(x) or '|' in str(x) else 0)
        
        return df
    
    def create_channel_advanced_features(self, df):
        """Create advanced channel features"""
        df = self._sanitize_numeric(df)
        
        # Channel age (estimated from video count and upload frequency)
        # Assuming average upload frequency
        df['estimated_channel_age_months'] = df['channel_video_count'] / 4  # ~4 videos per month
        
        # Channel growth rate (subscribers per video)
        df['subscriber_growth_rate'] = df['channel_subscribers'] / (df['channel_video_count'] + 1)
        
        # Channel engagement rate (estimated)
        df['estimated_engagement_rate'] = df['channel_view_count'] / (df['channel_subscribers'] + 1)
        
        # Channel size category (numeric)
        df['channel_size_numeric'] = pd.cut(
            df['channel_subscribers'],
            bins=[0, 10000, 100000, 1000000, float('inf')],
            labels=[1, 2, 3, 4]
        ).astype(float)
        
        return df
    
    def create_content_quality_features(self, df):
        """Create content quality indicators"""
        df = self._sanitize_numeric(df)
        
        # Content completeness score
        completeness = (
            (df['description_length'] > 100).astype(int) * 0.3 +
            (df['tag_count'] >= 5).astype(int) * 0.3 +
            (df['title_length'] >= 40).astype(int) * 0.2 +
            (df['title_is_tutorial'] == 1).astype(int) * 0.2
        )
        df['content_completeness_score'] = completeness
        
        # SEO score
        seo_score = (
            (df['title_length'].between(50, 60)).astype(int) * 0.3 +
            (df['tag_count'].between(8, 12)).astype(int) * 0.2 +
            (df['description_length'] > 200).astype(int) * 0.2 +
            (df['title_has_number'] == 1).astype(int) * 0.15 +
            (df['title_is_question'] == 1).astype(int) * 0.15
        )
        df['seo_score'] = seo_score
        
        # Engagement potential score
        engagement_score = (
            (df['is_prime_time'] == 1).astype(int) * 0.3 +
            (df['duration_minutes'].between(10, 15)).astype(int) * 0.3 +
            (df['title_is_tutorial'] == 1).astype(int) * 0.2 +
            (df['title_has_emoji'] == 1).astype(int) * 0.1 +
            (df['is_weekend'] == 0).astype(int) * 0.1
        )
        df['engagement_potential_score'] = engagement_score
        
        return df
    
    def engineer_all_features(self, df):
        """Apply all advanced feature engineering"""
        print("\n=== Advanced Feature Engineering ===")
        
        print("Creating interaction features...")
        df = self.create_interaction_features(df)
        
        print("Creating polynomial features...")
        df = self.create_polynomial_features(df)
        
        print("Creating ratio features...")
        df = self.create_ratio_features(df)
        
        print("Creating advanced time features...")
        df = self.create_time_features(df)
        
        print("Creating advanced title features...")
        df = self.create_title_advanced_features(df)
        
        print("Creating advanced channel features...")
        df = self.create_channel_advanced_features(df)
        
        print("Creating content quality features...")
        df = self.create_content_quality_features(df)
        
        # Final cleanup: sanitize numeric columns only (categoricals can't accept fillna(0))
        df = self._sanitize_numeric(df)
        df = df.replace([np.inf, -np.inf], 0)
        
        print(f"Total features after advanced engineering: {df.shape[1]}")
        
        return df

