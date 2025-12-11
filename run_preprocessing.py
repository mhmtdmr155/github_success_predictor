"""Run data preprocessing"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_preprocessing import DataPreprocessor

if __name__ == '__main__':
    preprocessor = DataPreprocessor()
    df = preprocessor.preprocess('raw_data/youtube_videos_raw.csv')
    X, y = preprocessor.select_features(df)
    print(f"\nFinal dataset: {X.shape}")
    print(f"Target stats: mean={y.mean():,.0f}, min={y.min():,.0f}, max={y.max():,.0f}")

