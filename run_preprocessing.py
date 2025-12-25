"""Run data preprocessing"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_preprocessing import DataPreprocessor

if __name__ == '__main__':
    preprocessor = DataPreprocessor()
    
    # Önce yeni dosyayı kontrol et, yoksa eski dosyayı kullan
    input_file = 'raw_data/youtube_videos_improved.csv'
    if not os.path.exists(input_file):
        input_file = 'raw_data/youtube_videos_raw.csv'
        print(f"⚠ youtube_videos_improved.csv bulunamadı, {input_file} kullanılıyor")
    else:
        print(f"✓ {input_file} kullanılıyor")
    
    df = preprocessor.preprocess(input_file)
    X, y = preprocessor.select_features(df)
    print(f"\nFinal dataset: {X.shape}")
    print(f"Target stats: mean={y.mean():,.0f}, min={y.min():,.0f}, max={y.max():,.0f}")

