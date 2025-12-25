"""
1000+ Video Toplama Scripti
Gerçek YouTube API verisi ile daha fazla veri toplamak için optimize edilmiş script
"""
import os
import sys

# Config dosyasını güncelle
def update_config():
    """Config dosyasını daha fazla veri toplamak için güncelle"""
    config_path = 'src/config.py'
    
    print("="*60)
    print("CONFIG DOSYASI GUNCELLENIYOR")
    print("="*60)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # MAX_VIDEOS_PER_CHANNEL değerini güncelle
    if 'MAX_VIDEOS_PER_CHANNEL = 50' in content:
        content = content.replace('MAX_VIDEOS_PER_CHANNEL = 50', 'MAX_VIDEOS_PER_CHANNEL = 100')
        print("✓ MAX_VIDEOS_PER_CHANNEL: 50 -> 100 güncellendi")
    elif 'MAX_VIDEOS_PER_CHANNEL = 100' in content:
        print("✓ MAX_VIDEOS_PER_CHANNEL zaten 100")
    else:
        print("⚠ MAX_VIDEOS_PER_CHANNEL değeri bulunamadı, manuel kontrol edin")
    
    # Daha fazla kanal önerisi ekle (yorum olarak)
    if '# Daha fazla kanal ekleyebilirsiniz' not in content:
        kanal_ornekleri = """
# Daha fazla kanal eklemek için aşağıdaki örnekleri kullanabilirsiniz:
# Popüler Teknoloji Kanalları:
# 'UCBJycsmduvYEL83R_U4JriQ',  # Marques Brownlee (MKBHD)
# 'UCXuqSBlHAE6Xw-yeJA0Tunw',  # Linus Tech Tips
# 'UC8butISFwT-Wl7EV0hUK0BQ',  # freeCodeCamp.org
# 'UCWv7vMbMWH4-V0ZXdmDpPBA',  # Programming with Mosh
# 'UCW5YeuERMmlnqo4oq8vwDeg',  # The Net Ninja
# 'UCsBjURrPoezykLs9EqgamOA',  # Fireship
# 'UC29ju8bIPu5jQf3bi3d67Zw',  # Traversy Media
# 'UC8A0M0eDttdB11MHxX58vXQ',  # Corey Schafer
# 'UCu1xbgCV5o48h_BYCQD7K1g',  # Sentdex
# 'UCJ0-OtVpF0wOKEqT2Z1HEtA',  # Derek Banas
# 
# 1000+ video için önerilen: 15-20 kanal × 100 video = 1500-2000 video
"""
        # TARGET_CHANNELS listesinden sonra ekle
        if 'TARGET_CHANNELS = [' in content:
            # Son kanal ID'sinden sonra ekle
            lines = content.split('\n')
            new_lines = []
            added = False
            for i, line in enumerate(lines):
                new_lines.append(line)
                if ']' in line and 'TARGET_CHANNELS' in lines[max(0, i-5):i+1] and not added:
                    # Kanal listesinin sonunu bulduk
                    new_lines.append(kanal_ornekleri)
                    added = True
            content = '\n'.join(new_lines)
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✓ Config dosyası güncellendi")
    print("\n⚠ ÖNEMLI: src/config.py dosyasını açıp TARGET_CHANNELS listesine")
    print("   daha fazla kanal ID'si eklemeyi unutmayın!")
    print("   Hedef: 15-20 kanal × 100 video = 1500-2000 video")


def check_api_key():
    """API anahtarını kontrol et"""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('YOUTUBE_API_KEY', '')
    
    if not api_key:
        print("\n" + "="*60)
        print("HATA: YOUTUBE_API_KEY bulunamadı!")
        print("="*60)
        print("\nLütfen .env dosyası oluşturup API anahtarınızı ekleyin:")
        print("  echo YOUTUBE_API_KEY=your_api_key_here > .env")
        print("\nAPI anahtarı alma: GERCEK_VERI_TOPLAMA_KILAVUZU.md dosyasına bakın")
        return False
    
    print("\n✓ API anahtarı bulundu")
    return True


def main():
    """Ana fonksiyon"""
    print("="*60)
    print("1000+ VIDEO TOPLAMA HAZIRLIK")
    print("="*60)
    
    # 1. Config güncelle
    update_config()
    
    # 2. API anahtarı kontrol
    if not check_api_key():
        return
    
    # 3. Veri toplama başlat
    print("\n" + "="*60)
    print("VERI TOPLAMA BASLATILIYOR")
    print("="*60)
    print("\n⚠ UYARI: Bu işlem 15-30 dakika sürebilir")
    print("   (1000+ video toplamak için)")
    print("\nDevam etmek için Enter'a basın (Ctrl+C ile iptal)...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nİptal edildi.")
        return
    
    # Veri toplama scriptini çalıştır
    print("\nVeri toplama başlatılıyor...")
    print("="*60)
    
    try:
        from src.improved_data_collection import main as collect_main
        collect_main()
    except Exception as e:
        print(f"\nHata: {e}")
        print("\nManuel olarak çalıştırmak için:")
        print("  python -m src.improved_data_collection")


if __name__ == '__main__':
    main()

