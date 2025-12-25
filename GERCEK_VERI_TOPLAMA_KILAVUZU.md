# 🎯 Gerçek YouTube API Verisi ile 1000+ Video Toplama Kılavuzu

## 📋 Özet
Bu kılavuz, **mevcut verinize yeni veriler ekleyerek** YouTube Data API v3 ile 1000+ video toplayıp model performansını artırmak için adım adım talimatlar içerir.

**🎯 Önemli:** 
- Bu kılavuz, **daha önce veri toplamış** ve şimdi mevcut veriye ekleme yapmak isteyenler için hazırlanmıştır
- `add_more_data.py` scripti otomatik olarak mevcut veriyi bulur, yeni veri toplar ve birleştirir
- Duplicate'ler (aynı video_id) otomatik olarak kaldırılır
- İlk kez veri topluyorsanız da kullanabilirsiniz (script otomatik algılar)

---

## 🚀 Adım 1: YouTube API Anahtarı Alma

### 1.1. Google Cloud Console'a Giriş
1. **Google Cloud Console**'a gidin: https://console.cloud.google.com/
2. Google hesabınızla giriş yapın

### 1.2. Yeni Proje Oluşturma
1. Üst menüden **"Select a project"** > **"New Project"** tıklayın
2. Proje adı: `YouTube Success Predictor` (veya istediğiniz isim)
3. **"Create"** butonuna tıklayın
4. Oluşturulan projeyi seçin

### 1.3. YouTube Data API v3'ü Etkinleştirme
1. Sol menüden **"APIs & Services"** > **"Library"** seçin
2. Arama kutusuna **"YouTube Data API v3"** yazın
3. **"YouTube Data API v3"** seçeneğine tıklayın
4. **"Enable"** butonuna tıklayın

### 1.4. API Anahtarı Oluşturma
1. Sol menüden **"APIs & Services"** > **"Credentials"** seçin
2. Üstte **"+ CREATE CREDENTIALS"** butonuna tıklayın
3. **"API key"** seçeneğini seçin
4. Oluşturulan API anahtarını **kopyalayın**
5. **(Önemli)** API anahtarını kısıtlamak için:
   - Oluşturulan anahtarın yanındaki **kalem ikonuna** tıklayın
   - **"API restrictions"** bölümünde **"Restrict key"** seçin
   - **"YouTube Data API v3"** seçeneğini işaretleyin
   - **"Save"** butonuna tıklayın

### 1.5. API Anahtarını Projeye Ekleme
1. Proje klasörünüzde `.env` dosyası oluşturun (yoksa)
2. `.env` dosyasına şunu ekleyin:
   ```env
   YOUTUBE_API_KEY=your_api_key_here
   ```
3. `your_api_key_here` yerine kopyaladığınız API anahtarını yapıştırın
4. Dosyayı kaydedin

**⚠️ Önemli:** `.env` dosyasını asla GitHub'a commit etmeyin! (`.gitignore`'da olmalı)

---

## 📊 Adım 2: Daha Fazla Kanal Ekleme

### 2.1. Kanal ID'lerini Bulma
YouTube kanal ID'sini bulmak için:

**Yöntem 1: Kanal Sayfasından**
1. YouTube'da kanal sayfasına gidin
2. Sayfa kaynağını görüntüleyin (`Ctrl+U`)
3. `"channelId"` veya `"externalId"` arayın

**Yöntem 2: Online Araçlar**
- https://commentpicker.com/youtube-channel-id.php
- Kanal URL'sini yapıştırın, ID'yi alın

**Yöntem 3: YouTube Studio**
1. YouTube Studio'ya gidin
2. Ayarlar > Kanal > Gelişmiş ayarlar
3. Kanal ID'si orada görünür

### 2.2. Popüler Teknoloji Kanalları (Örnek)
İşte 1000+ video toplamak için önerilen kanallar:

```python
# Teknoloji/Programlama Kanalları
TARGET_CHANNELS = [
    'UC8butISFwT-Wl7EV0hUK0BQ',  # freeCodeCamp.org (1M+ abone)
    'UCWv7vMbMWH4-V0ZXdmDpPBA',  # Programming with Mosh (2M+ abone)
    'UCW5YeuERMmlnqo4oq8vwDeg',  # The Net Ninja (1M+ abone)
    'UCsBjURrPoezykLs9EqgamOA',  # Fireship (2M+ abone)
    'UC29ju8bIPu5jQf3bi3d67Zw',  # Traversy Media (2M+ abone)
    'UC8A0M0eDttdB11MHxX58vXQ',  # Corey Schafer (1M+ abone)
    'UCu1xbgCV5o48h_BYCQD7K1g',  # Sentdex (1M+ abone)
    'UCJ0-OtVpF0wOKEqT2Z1HEtA',  # Derek Banas (1M+ abone)
    'UCsBjURrPoezykLs9EqgamOA',  # Web Dev Simplified (1M+ abone)
    'UC8butISFwT-Wl7EV0hUK0BQ',  # TechWorld with Nana (500K+ abone)
    # Daha fazla kanal ekleyebilirsiniz...
]
```

### 2.3. Config Dosyasını Güncelleme
`src/config.py` dosyasını açın ve kanalları güncelleyin:

```python
# Daha fazla kanal ekleyin (20-30 kanal önerilir)
TARGET_CHANNELS = [
    # Mevcut kanallar...
    # Yeni kanallar ekleyin
    'YENI_KANAL_ID_1',
    'YENI_KANAL_ID_2',
    # ... daha fazla
]

# Her kanaldan daha fazla video toplamak için
MAX_VIDEOS_PER_CHANNEL = 100  # 50'den 100'e çıkarın (veya daha fazla)
```

---

## 🔧 Adım 3: Veri Toplama Ayarlarını Optimize Etme

### 3.1. Config Dosyasını Güncelleme
`src/config.py` dosyasını düzenleyin:

```python
# Data Collection Settings
MAX_VIDEOS_PER_CHANNEL = 100  # Her kanaldan 100 video (önceden 50)
MAX_RESULTS_PER_REQUEST = 50  # API limiti (değiştirmeyin)
```

**Hesaplama:**
- 20 kanal × 100 video = 2000 video (hedef: 1000+)
- 15 kanal × 100 video = 1500 video
- 10 kanal × 100 video = 1000 video

### 3.2. API Quota Limitleri
**Önemli Bilgiler:**
- YouTube Data API v3 günlük quota: **10,000 birim**
- Her video detayı çekme: **1 birim**
- Her kanal bilgisi: **1 birim**
- Her playlist item: **1 birim**

**Hesaplama:**
- 1000 video toplamak için: ~2000-3000 birim (güvenli)
- Günlük limit: 10,000 birim
- **Sonuç:** Tek seferde 1000+ video toplayabilirsiniz

---

## 📥 Adım 4: Mevcut Veriye Yeni Veri Ekleme

### 4.1. Mevcut Veriyi Kontrol Etme

Önce mevcut verinizi kontrol edin:

```bash
python -c "import pandas as pd; df = pd.read_csv('raw_data/youtube_videos_improved.csv'); print(f'Mevcut veri: {len(df)} video')"
```

**Not:** Eğer `youtube_videos_improved.csv` yoksa, `youtube_videos_raw.csv` dosyasını kontrol edin.

### 4.2. Mevcut Veriye Yeni Veri Ekleme (ÖNERİLEN)

**Otomatik Script (En Kolay):**
```bash
python add_more_data.py
```

Bu script:
- ✅ Mevcut veriyi otomatik bulur ve yükler
- ✅ Yeni veri toplar
- ✅ Duplicate'leri otomatik kaldırır
- ✅ Verileri birleştirir ve kaydeder
- ✅ İstatistikleri gösterir

### 4.3. Manuel Veri Toplama (Alternatif)

Eğer sıfırdan başlamak istiyorsanız:

```bash
cd src
python improved_data_collection.py
```

**Veya kök dizinden:**
```bash
python -m src.improved_data_collection
```

### 4.4. Veri Toplama Süreci

**add_more_data.py scripti şunları yapar:**
1. ✅ Mevcut veriyi yükler (`youtube_videos_improved.csv` veya `youtube_videos_raw.csv`)
2. ✅ Mevcut video ID'lerini kaydeder (duplicate kontrolü için)
3. ✅ Her kanaldan kanal bilgilerini çeker
4. ✅ Her kanaldan belirtilen sayıda video çeker
5. ✅ Video detaylarını toplar (başlık, süre, görüntülenme, vb.)
6. ✅ İlk hafta görüntülenme sayısını hesaplar
7. ✅ Kalite filtreleme yapar
8. ✅ **Duplicate'leri otomatik kaldırır** (aynı video_id varsa)
9. ✅ Yeni veriyi mevcut veriye ekler
10. ✅ Birleştirilmiş veriyi `raw_data/youtube_videos_improved.csv` dosyasına kaydeder

**Süre Tahmini:**
- 1000 video: ~15-30 dakika
- 2000 video: ~30-60 dakika
- (API rate limiting nedeniyle)

### 4.5. Veri Toplama Kontrolü

**add_more_data.py çalıştırıldığında şunları göreceksiniz:**

```
============================================================
MEVCUT VERIYE YENI VERI EKLEME
============================================================
✓ Mevcut veri yüklendi: 500 video

📊 Mevcut Veri İstatistikleri:
   Toplam video: 500
   Ortalama görüntülenme: 244,998
   Kanal sayısı: 10

============================================================
YENI VERI TOPLAMA BASLATILIYOR
============================================================
   Hedef kanallar: 20
   Her kanaldan: 100 video
   Tahmini yeni veri: 2000 video

Starting IMPROVED data collection from YouTube API...
Target channels: 20
Max videos per channel: 100

Collecting from channel: UC8butISFwT-Wl7EV0hUK0BQ
  Channel: freeCodeCamp.org
  Subscribers: 8,500,000
  Collected 100 videos
  After quality filter: 95 videos
  ...

============================================================
VERI BIRLESTIRME
============================================================
  Mevcut veri: 500 video
  Yeni toplanan: 1500 video
  ⚠ Duplicate video bulundu: 50 adet
  ✓ Duplicate'ler kaldırıldı, yeni eklenen: 1450 video

✓ Birleştirilmiş veri kaydedildi: raw_data/youtube_videos_improved.csv
  Toplam video: 1950
  Eski: 500, Yeni eklenen: 1450, Toplam: 1950
```

**Önemli:** Script otomatik olarak duplicate'leri (aynı video_id) kaldırır, böylece aynı video birden fazla kez eklenmez.

---

## 🔄 Adım 5: Veri Ön İşleme ve Model Eğitimi

### 5.1. Veri Ön İşleme
Toplanan veriyi işlemek için:

```bash
python run_preprocessing.py
```

**Not:** Script otomatik olarak `raw_data/youtube_videos_improved.csv` dosyasını bulacaktır.

### 5.2. Model Eğitimi
İşlenmiş veri ile modeli eğitin:

```bash
python run_training.py
```

**Veya geliştirilmiş model için:**
```bash
python improve_model.py
```

### 5.3. Performans Karşılaştırması
Eğitim sonrası performans metriklerini karşılaştırın:

**Örnek Veri (500 video):**
- R² Score: 0.1086
- MAE: 151,135

**Gerçek Veri (1000+ video) - Beklenen:**
- R² Score: >0.50 (hedef: >0.85)
- MAE: <100,000 (hedef: <50,000)

---

## 🎯 Adım 6: Daha Fazla Veri Toplama Stratejileri

### 6.1. Farklı Kategorilerden Kanal Ekleme
Sadece teknoloji değil, farklı kategorilerden de kanal ekleyin:

- **Eğitim:** Khan Academy, Crash Course
- **Oyun:** Markiplier, PewDiePie
- **Müzik:** Müzik kanalları
- **Eğlence:** Komedi kanalları

**Not:** Farklı kategoriler modelin genelleştirme yeteneğini artırır.

### 6.2. Zaman Aralığı Stratejisi
Farklı zamanlarda veri toplayın:
- İlk toplama: Bugün
- İkinci toplama: 1 hafta sonra (yeni videolar)
- Üçüncü toplama: 1 ay sonra

Bu şekilde zaman içinde veri setinizi büyütebilirsiniz.

### 6.3. Batch Toplama
API quota'sını aşmamak için:

```python
# Gün 1: 500 video
MAX_VIDEOS_PER_CHANNEL = 50
# 10 kanal × 50 = 500 video

# Gün 2: 500 video daha
# Toplam: 1000 video
```

---

## ⚠️ Önemli Notlar ve Sorun Giderme

### API Quota Aşımı
**Problem:** "Quota exceeded" hatası

**Çözüm:**
1. Google Cloud Console'da quota'yı kontrol edin
2. Günlük limit: 10,000 birim
3. Ertesi gün tekrar deneyin
4. Veya daha az video toplayın

### Kanal Bulunamadı
**Problem:** "Channel not found" hatası

**Çözüm:**
1. Kanal ID'sinin doğru olduğundan emin olun
2. Kanalın public olduğundan emin olun
3. Kanalın silinmediğinden emin olun

### Yavaş Veri Toplama
**Problem:** Veri toplama çok yavaş

**Çözüm:**
1. Bu normaldir (API rate limiting)
2. 1000 video için 15-30 dakika bekleyin
3. İnternet bağlantınızı kontrol edin

### İlk Hafta Görüntülenme Hesaplama
**Problem:** Bazı videolarda ilk hafta görüntülenme 0

**Çözüm:**
1. Bu normaldir (eski videolar için)
2. Script otomatik olarak filtreler
3. Sadece son 3 yılın videolarını toplar

---

## 📊 Veri Toplama Sonrası Kontrol

### Veri Kalitesi Kontrolü
```bash
python -c "import pandas as pd; df = pd.read_csv('raw_data/youtube_videos_improved.csv'); print(f'Toplam video: {len(df)}'); print(f'Geçerli veri: {df[\"target_first_week_views\"].notna().sum()}'); print(f'Ortalama görüntülenme: {df[\"target_first_week_views\"].mean():,.0f}')"
```

### Veri İstatistikleri
- Toplam video sayısı
- Geçerli veri sayısı (NaN olmayan)
- Ortalama ilk hafta görüntülenme
- Minimum/Maksimum değerler

---

## 🎉 Başarı Kriterleri

### Minimum Hedefler
- ✅ 1000+ video toplandı
- ✅ Geçerli veri: 900+ (NaN olmayan)
- ✅ Model R² > 0.50
- ✅ Model MAE < 100,000

### İdeal Hedefler
- ✅ 2000+ video toplandı
- ✅ Geçerli veri: 1800+
- ✅ Model R² > 0.85
- ✅ Model MAE < 50,000

---

## 📝 Özet Checklist (Mevcut Veriye Ekleme)

- [ ] Mevcut veri kontrol edildi (`raw_data/youtube_videos_improved.csv` veya `youtube_videos_raw.csv`)
- [ ] YouTube API anahtarı `.env` dosyasında mevcut
- [ ] `src/config.py` dosyasında kanallar güncellendi (daha fazla kanal eklendi)
- [ ] `MAX_VIDEOS_PER_CHANNEL` 100'e çıkarıldı (veya daha fazla)
- [ ] `python add_more_data.py` çalıştırıldı (mevcut veriye ekleme)
- [ ] 1000+ toplam video hedefine ulaşıldı
- [ ] `python run_preprocessing.py` çalıştırıldı (yeni veri ile)
- [ ] `python run_training.py` çalıştırıldı (yeni veri ile)
- [ ] Model performansı kontrol edildi (iyileşme görüldü mü?)
- [ ] Flask uygulaması yeniden başlatıldı

### İlk Kez Veri Topluyorsanız:

- [ ] YouTube API anahtarı alındı ve `.env` dosyasına eklendi
- [ ] `python -m src.improved_data_collection` çalıştırıldı
- [ ] Yukarıdaki checklist'i takip edin

---

## 🚀 Hızlı Başlangıç Komutları (Mevcut Veriye Ekleme)

```bash
# 1. API anahtarını kontrol edin (.env dosyasında olmalı)
# Eğer yoksa: echo YOUTUBE_API_KEY=your_key_here > .env

# 2. Config dosyasını güncelleyin (daha fazla kanal ekleyin)
# src/config.py dosyasında TARGET_CHANNELS listesine yeni kanallar ekleyin
# MAX_VIDEOS_PER_CHANNEL = 100 (veya daha fazla)

# 3. Mevcut veriye yeni veri ekleyin (ÖNERİLEN)
python add_more_data.py

# 4. Veriyi işleyin
python run_preprocessing.py

# 5. Modeli eğitin
python run_training.py

# 6. Flask uygulamasını başlatın
python app.py
```

### İlk Kez Veri Topluyorsanız:

```bash
# Sıfırdan veri toplama
python -m src.improved_data_collection

# Sonra yukarıdaki adımları takip edin
```

---

**Son Güncelleme:** 2025-01-27
**Hedef:** 1000+ video ile %85+ R² score

