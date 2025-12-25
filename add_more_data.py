"""
Mevcut Veriye Yeni Veri Ekleme Scripti
Daha önce toplanmış veriye yeni veriler ekler, duplicate'leri kaldırır
"""
import os
import pandas as pd
from datetime import datetime
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.improved_data_collection import ImprovedDataCollector
from src.config import YOUTUBE_API_KEY, TARGET_CHANNELS, MAX_VIDEOS_PER_CHANNEL


def load_existing_data(filepath='raw_data/youtube_videos_improved.csv'):
    """Mevcut veriyi yükle"""
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        print(f"✓ Mevcut veri yüklendi: {len(df)} video")
        return df
    else:
        print(f"⚠ Mevcut veri dosyası bulunamadı: {filepath}")
        print("   Yeni veri toplama modunda devam ediliyor...")
        return None


def get_existing_video_ids(df):
    """Mevcut verideki video ID'lerini al (duplicate kontrolü için)"""
    if df is not None and 'video_id' in df.columns:
        return set(df['video_id'].tolist())
    return set()


def merge_data(existing_df, new_df, output_path='raw_data/youtube_videos_improved.csv'):
    """Yeni veriyi mevcut veriye ekle ve duplicate'leri kaldır"""
    if existing_df is None:
        # İlk veri toplama
        print("\n" + "="*60)
        print("ILK VERI TOPLAMA")
        print("="*60)
        new_df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"✓ Veri kaydedildi: {output_path}")
        print(f"  Toplam video: {len(new_df)}")
        return new_df
    
    # Mevcut veri var, birleştir
    print("\n" + "="*60)
    print("VERI BIRLESTIRME")
    print("="*60)
    
    existing_ids = get_existing_video_ids(existing_df)
    print(f"  Mevcut veri: {len(existing_df)} video")
    print(f"  Yeni toplanan: {len(new_df)} video")
    
    # Duplicate kontrolü
    if 'video_id' in new_df.columns:
        new_ids = set(new_df['video_id'].tolist())
        duplicates = existing_ids.intersection(new_ids)
        
        if duplicates:
            print(f"  ⚠ Duplicate video bulundu: {len(duplicates)} adet")
            # Duplicate'leri yeni veriden çıkar
            new_df = new_df[~new_df['video_id'].isin(duplicates)]
            print(f"  ✓ Duplicate'ler kaldırıldı, yeni eklenen: {len(new_df)} video")
        else:
            print(f"  ✓ Duplicate yok, tüm yeni veriler eklenecek")
    
    # Birleştir
    merged_df = pd.concat([existing_df, new_df], ignore_index=True)
    
    # Tekrar duplicate kontrolü (güvenlik için)
    if 'video_id' in merged_df.columns:
        before_dedup = len(merged_df)
        merged_df = merged_df.drop_duplicates(subset=['video_id'], keep='first')
        after_dedup = len(merged_df)
        if before_dedup != after_dedup:
            print(f"  ⚠ Ek duplicate temizleme: {before_dedup - after_dedup} video kaldırıldı")
    
    # Kaydet
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    merged_df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"\n✓ Birleştirilmiş veri kaydedildi: {output_path}")
    print(f"  Toplam video: {len(merged_df)}")
    print(f"  Eski: {len(existing_df)}, Yeni eklenen: {len(new_df)}, Toplam: {len(merged_df)}")
    
    return merged_df


def main():
    """Ana fonksiyon"""
    print("="*60)
    print("MEVCUT VERIYE YENI VERI EKLEME")
    print("="*60)
    
    # API anahtarı kontrolü
    if not YOUTUBE_API_KEY:
        print("\n❌ HATA: YOUTUBE_API_KEY bulunamadı!")
        print("   Lütfen .env dosyasına API anahtarınızı ekleyin:")
        print("   YOUTUBE_API_KEY=your_api_key_here")
        return
    
    # Mevcut veriyi yükle
    existing_df = load_existing_data('raw_data/youtube_videos_improved.csv')
    
    # Alternatif dosya yollarını kontrol et
    if existing_df is None:
        existing_df = load_existing_data('raw_data/youtube_videos_raw.csv')
    
    if existing_df is not None:
        print(f"\n📊 Mevcut Veri İstatistikleri:")
        print(f"   Toplam video: {len(existing_df)}")
        if 'target_first_week_views' in existing_df.columns:
            print(f"   Ortalama görüntülenme: {existing_df['target_first_week_views'].mean():,.0f}")
        print(f"   Kanal sayısı: {existing_df['channel_name'].nunique() if 'channel_name' in existing_df.columns else 'N/A'}")
    
    # Yeni veri toplama
    print("\n" + "="*60)
    print("YENI VERI TOPLAMA BASLATILIYOR")
    print("="*60)
    print(f"   Hedef kanallar: {len(TARGET_CHANNELS)}")
    print(f"   Her kanaldan: {MAX_VIDEOS_PER_CHANNEL} video")
    print(f"   Tahmini yeni veri: {len(TARGET_CHANNELS) * MAX_VIDEOS_PER_CHANNEL} video")
    print("\n⚠ Bu işlem 15-30 dakika sürebilir...")
    print("   Devam etmek için Enter'a basın (Ctrl+C ile iptal)")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n❌ İptal edildi.")
        return
    
    # Veri topla
    print("\n🔄 Veri toplama başlatılıyor...\n")
    collector = ImprovedDataCollector(YOUTUBE_API_KEY)
    new_videos = collector.collect_all_data()
    
    if not new_videos:
        print("\n❌ Veri toplanamadı. API anahtarınızı ve internet bağlantınızı kontrol edin.")
        return
    
    # DataFrame'e çevir
    new_df = pd.DataFrame(new_videos)
    print(f"\n✓ Yeni veri toplandı: {len(new_df)} video")
    
    # Birleştir ve kaydet
    merged_df = merge_data(existing_df, new_df, 'raw_data/youtube_videos_improved.csv')
    
    # Özet
    print("\n" + "="*60)
    print("BASARIYLA TAMAMLANDI!")
    print("="*60)
    print(f"\n📊 Final İstatistikler:")
    print(f"   Toplam video: {len(merged_df)}")
    if 'target_first_week_views' in merged_df.columns:
        print(f"   Ortalama görüntülenme: {merged_df['target_first_week_views'].mean():,.0f}")
        print(f"   Min: {merged_df['target_first_week_views'].min():,.0f}")
        print(f"   Max: {merged_df['target_first_week_views'].max():,.0f}")
    
    print(f"\n📁 Dosya: raw_data/youtube_videos_improved.csv")
    print(f"\n✅ Sonraki adımlar:")
    print(f"   1. python run_preprocessing.py  (veri ön işleme)")
    print(f"   2. python run_training.py       (model eğitimi)")


if __name__ == '__main__':
    main()


