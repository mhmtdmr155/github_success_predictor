# 📝 Adım Adım: Mevcut Veriye Yeni Veri Ekleme

## 🎯 Hedef
Mevcut verinize yeni YouTube video verileri ekleyerek toplam veri sayısını 1000+ video'ya çıkarmak.

---

## ✅ Adım 1: Mevcut Veriyi Kontrol Et

### 1.1. Mevcut Veri Dosyasını Bul
Terminal'de şu komutu çalıştır:

```bash
python -c "import os; files = ['raw_data/youtube_videos_improved.csv', 'raw_data/youtube_videos_raw.csv']; found = [f for f in files if os.path.exists(f)]; print('Mevcut veri dosyaları:'); [print(f'  ✓ {f}') for f in found] if found else print('  ⚠ Veri dosyası bulunamadı (ilk kez veri toplayacaksınız)')"
```

**Beklenen Sonuç:**
- `raw_data/youtube_videos_improved.csv` varsa → Bu dosyayı kullanacak
- `raw_data/youtube_videos_raw.csv` varsa → Bu dosyayı kullanacak
- Hiçbiri yoksa → İlk kez veri toplama modunda çalışacak

### 1.2. Mevcut Veri Sayısını Öğren
```bash
python -c "import pandas as pd; import os; files = ['raw_data/youtube_videos_improved.csv', 'raw_data/youtube_videos_raw.csv']; for f in files: 
    if os.path.exists(f): 
        df = pd.read_csv(f); 
        print(f'{f}: {len(df)} video'); 
        break"
```

**Örnek Çıktı:**
```
raw_data/youtube_videos_improved.csv: 500 video
```

---

## ✅ Adım 2: YouTube API Anahtarını Kontrol Et

### 2.1. .env Dosyasını Kontrol Et
```bash
# Windows PowerShell
if (Test-Path .env) { Get-Content .env | Select-String "YOUTUBE_API_KEY" } else { Write-Host ".env dosyası bulunamadı" }
```

**Eğer API anahtarı yoksa:**

1. Google Cloud Console'a git: https://console.cloud.google.com/
2. YouTube Data API v3'ü etkinleştir
3. API anahtarı oluştur
4. `.env` dosyası oluştur:
   ```bash
   echo YOUTUBE_API_KEY=your_api_key_here > .env
   ```
   (Windows'ta: `notepad .env` ile açıp içine yazabilirsiniz)

---

## ✅ Adım 3: Daha Fazla Kanal Ekle

### 3.1. Config Dosyasını Aç
`src/config.py` dosyasını açın (Cursor'da veya notepad ile)

### 3.2. Kanal Listesini Güncelle

**Mevcut:**
```python
TARGET_CHANNELS = [
    'UC8butISFwT-Wl7EV0hUK0BQ',  # freeCodeCamp.org
    'UCWv7vMbMWH4-V0ZXdmDpPBA',  # Programming with Mosh
    # ... mevcut kanallar
]
```

**Güncelle (Daha fazla kanal ekle):**
```python
TARGET_CHANNELS = [
    # Mevcut kanallarınız...
    'UC8butISFwT-Wl7EV0hUK0BQ',  # freeCodeCamp.org
    'UCWv7vMbMWH4-V0ZXdmDpPBA',  # Programming with Mosh
    'UCW5YeuERMmlnqo4oq8vwDeg',  # The Net Ninja
    'UCsBjURrPoezykLs9EqgamOA',  # Fireship
    'UC29ju8bIPu5jQf3bi3d67Zw',  # Traversy Media
    'UC8A0M0eDttdB11MHxX58vXQ',  # Corey Schafer
    'UCu1xbgCV5o48h_BYCQD7K1g',  # Sentdex
    'UCJ0-OtVpF0wOKEqT2Z1HEtA',  # Derek Banas
    
    # YENİ KANALLAR EKLEYİN (15-20 kanal önerilir)
    'UCBJycsmduvYEL83R_U4JriQ',  # Marques Brownlee (MKBHD)
    'UCXuqSBlHAE6Xw-yeJA0Tunw',  # Linus Tech Tips
    # ... daha fazla kanal ID'si ekleyin
]
```

**Kanal ID'si Nasıl Bulunur?**
1. YouTube'da kanal sayfasına git
2. Sayfa kaynağını görüntüle (Ctrl+U)
3. `"channelId"` ara
4. Veya: https://commentpicker.com/youtube-channel-id.php

### 3.3. Video Sayısını Artır

Aynı dosyada şu satırı bul:
```python
MAX_VIDEOS_PER_CHANNEL = 50
```

Şöyle değiştir:
```python
MAX_VIDEOS_PER_CHANNEL = 100  # Her kanaldan 100 video
```

**Hesaplama:**
- 10 kanal × 100 video = 1,000 video
- 15 kanal × 100 video = 1,500 video
- 20 kanal × 100 video = 2,000 video

**Dosyayı kaydet!**

---

## ✅ Adım 4: Yeni Veri Topla ve Ekle

### 4.1. Script'i Çalıştır

```bash
python add_more_data.py
```

### 4.2. Ne Olacak?

1. **Mevcut veri yüklenecek:**
   ```
   ✓ Mevcut veri yüklendi: 500 video
   ```

2. **İstatistikler gösterilecek:**
   ```
   📊 Mevcut Veri İstatistikleri:
      Toplam video: 500
      Ortalama görüntülenme: 244,998
   ```

3. **Onay isteyecek:**
   ```
   ⚠ Bu işlem 15-30 dakika sürebilir...
      Devam etmek için Enter'a basın (Ctrl+C ile iptal)
   ```
   → **Enter'a bas**

4. **Veri toplama başlayacak:**
   ```
   Starting IMPROVED data collection from YouTube API...
   Target channels: 20
   Max videos per channel: 100
   
   Collecting from channel: UC8butISFwT-Wl7EV0hUK0BQ
     Channel: freeCodeCamp.org
     Subscribers: 8,500,000
     Collected 100 videos
     After quality filter: 95 videos
   ...
   ```

5. **Veriler birleştirilecek:**
   ```
   ============================================================
   VERI BIRLESTIRME
   ============================================================
     Mevcut veri: 500 video
     Yeni toplanan: 1500 video
     ⚠ Duplicate video bulundu: 50 adet
     ✓ Duplicate'ler kaldırıldı, yeni eklenen: 1450 video
   
   ✓ Birleştirilmiş veri kaydedildi
     Toplam video: 1950
   ```

### 4.3. Süre
- **1000 video:** ~15-30 dakika
- **2000 video:** ~30-60 dakika

**Sabırlı ol!** API rate limiting nedeniyle yavaş olabilir.

---

## ✅ Adım 5: Veriyi İşle

### 5.1. Veri Ön İşleme

```bash
python run_preprocessing.py
```

**Ne yapar?**
- Veriyi temizler
- Özellikler oluşturur
- `processed_data/youtube_videos_processed.csv` dosyasına kaydeder

**Beklenen Çıktı:**
```
============================================================
DATA PREPROCESSING PIPELINE
============================================================
Loaded data: (1950, 22)

=== Data Cleaning ===
After removing duplicates: (1950, 22)
...
Final dataset: (1900, 50)
```

---

## ✅ Adım 6: Modeli Eğit

### 6.1. Model Eğitimi

```bash
python run_training.py
```

**Ne yapar?**
- Modeli yeni veri ile eğitir
- Performans metriklerini gösterir
- Modeli `models/` klasörüne kaydeder

**Beklenen Çıktı:**
```
============================================================
MODEL TRAINING
============================================================

Training Linear Regression...
Training Random Forest...
Training XGBoost...

[Best Model] Random Forest (R² = 0.65)  ← Daha iyi olmalı!

Model saved to: models\best_model.pkl
```

**Performans Karşılaştırması:**
- **Önceki (500 video):** R² = 0.1086
- **Yeni (1000+ video):** R² > 0.50 (hedef: >0.85)

---

## ✅ Adım 7: Flask Uygulamasını Yeniden Başlat

### 7.1. Eski Uygulamayı Durdur
Eğer çalışıyorsa, terminal'de `Ctrl+C` ile durdur.

### 7.2. Yeni Model ile Başlat

```bash
python app.py
```

**Beklenen Çıktı:**
```
Loading model...
Model loaded successfully!
Starting Flask server...
 * Running on http://0.0.0.0:5000
```

### 7.3. Test Et

Tarayıcıda aç: http://localhost:5000

Yeni model ile tahmin yap ve sonuçları gör!

---

## 📊 Adım 8: Sonuçları Kontrol Et

### 8.1. Final Veri Sayısı

```bash
python -c "import pandas as pd; df = pd.read_csv('raw_data/youtube_videos_improved.csv'); print(f'Toplam video: {len(df)}'); print(f'Geçerli veri: {df[\"target_first_week_views\"].notna().sum()}')"
```

### 8.2. Model Performansı

Model eğitimi sırasında gösterilen R² skorunu kontrol et:
- **Hedef:** R² > 0.50 (1000+ video ile)
- **İdeal:** R² > 0.85 (2000+ video ile)

---

## ⚠️ Sorun Giderme

### Problem 1: "API key not found"
**Çözüm:**
```bash
# .env dosyasını kontrol et
notepad .env
# İçinde YOUTUBE_API_KEY=your_key_here olmalı
```

### Problem 2: "Quota exceeded"
**Çözüm:**
- API quota limiti aşıldı
- Ertesi gün tekrar dene
- Veya daha az video topla (MAX_VIDEOS_PER_CHANNEL = 50)

### Problem 3: "Duplicate'ler çok fazla"
**Çözüm:**
- Normal! Aynı kanallardan tekrar veri topluyorsanız duplicate olur
- Script otomatik kaldırır, sorun değil

### Problem 4: "Veri toplama çok yavaş"
**Çözüm:**
- Normal! API rate limiting nedeniyle yavaş
- Sabırlı ol, 15-30 dakika bekleyebilir

---

## ✅ Başarı Kontrol Listesi

- [ ] Mevcut veri kontrol edildi
- [ ] API anahtarı `.env` dosyasında mevcut
- [ ] `src/config.py` güncellendi (daha fazla kanal eklendi)
- [ ] `MAX_VIDEOS_PER_CHANNEL = 100` yapıldı
- [ ] `python add_more_data.py` çalıştırıldı
- [ ] 1000+ toplam video hedefine ulaşıldı
- [ ] `python run_preprocessing.py` çalıştırıldı
- [ ] `python run_training.py` çalıştırıldı
- [ ] Model performansı iyileşti (R² arttı)
- [ ] Flask uygulaması yeniden başlatıldı

---

## 🎉 Özet Komutlar (Hızlı Referans)

```bash
# 1. Mevcut veriyi kontrol et
python -c "import pandas as pd; import os; f='raw_data/youtube_videos_improved.csv'; print(f'{len(pd.read_csv(f))} video' if os.path.exists(f) else 'Veri yok')"

# 2. Config dosyasını düzenle (manuel)
notepad src/config.py

# 3. Yeni veri ekle
python add_more_data.py

# 4. Veriyi işle
python run_preprocessing.py

# 5. Modeli eğit
python run_training.py

# 6. Flask'ı başlat
python app.py
```

---

**Hazırsın! Adım adım takip et ve başarılı ol! 🚀**

