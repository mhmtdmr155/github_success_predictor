# 🚀 Hızlı Başlangıç Kılavuzu

## 1. Kurulum (5 dakika)

```bash
# 1. Bağımlılıkları yükle
pip install -r requirements.txt

# 2. .env dosyası oluştur
cp .env.example .env

# 3. .env dosyasını düzenle ve YouTube API anahtarını ekle
# YOUTUBE_API_KEY=your_api_key_here
```

## 2. Veri Toplama ve Model Eğitimi

### Seçenek A: Otomatik Pipeline (Önerilen)

```bash
python run_pipeline.py
```

Bu script tüm adımları otomatik olarak çalıştırır:
1. Veri toplama (YouTube API)
2. Veri ön işleme
3. Model eğitimi

### Seçenek B: Manuel Adımlar

```bash
# 1. Veri topla
cd src
python data_collection.py

# 2. Veriyi işle
python data_preprocessing.py

# 3. Modeli eğit
python model_training.py
```

## 3. Web Uygulamasını Çalıştır

```bash
# Proje kök dizininde
python app.py
```

Tarayıcıda aç: `http://localhost:5000`

## ⚠️ Önemli Notlar

1. **YouTube API Anahtarı**: 
   - [Google Cloud Console](https://console.cloud.google.com/)'dan alın
   - YouTube Data API v3'ü etkinleştirin
   - Günlük 10,000 quota limiti var

2. **İlk Çalıştırma**:
   - Veri toplama 10-30 dakika sürebilir
   - Model eğitimi 1-5 dakika sürebilir

3. **Model Yoksa**:
   - Web uygulaması çalışır ama tahmin yapamaz
   - Önce modeli eğitmeniz gerekir

## 🐛 Sorun Giderme

### "Model not loaded" hatası
- `models/` klasöründe model dosyaları var mı kontrol edin
- Model eğitimi adımını çalıştırın

### "API key not found" hatası
- `.env` dosyasının doğru yerde olduğundan emin olun
- API anahtarının doğru olduğunu kontrol edin

### Veri toplama çalışmıyor
- API quota limitini kontrol edin
- İnternet bağlantınızı kontrol edin
- API anahtarının geçerli olduğundan emin olun

## 📊 Test Verisi (Opsiyonel)

Eğer API anahtarınız yoksa veya hızlı test yapmak istiyorsanız, örnek veri dosyası kullanabilirsiniz (gelecekte eklenecek).

