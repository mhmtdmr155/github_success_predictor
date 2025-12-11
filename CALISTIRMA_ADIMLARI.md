# 🚀 Projeyi Çalıştırma Adımları

## 1️⃣ Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

## 2️⃣ YouTube API Anahtarı Ayarla (Opsiyonel - Sadece veri toplamak için gerekli)
```bash
# .env dosyası oluştur
echo YOUTUBE_API_KEY=your_api_key_here > .env
```
**Not:** Eğer sadece web uygulamasını çalıştıracaksanız ve model zaten eğitilmişse bu adımı atlayabilirsiniz.

## 3️⃣ Model Eğit (Eğer model yoksa)
```bash
# Örnek veri ile hızlı test için:
python create_sample_data.py

# Sonra modeli eğit:
python improve_model.py
```

**VEYA** gerçek veri ile:
```bash
# Veri topla (YouTube API gerekli)
cd src
python improved_data_collection.py

# Modeli eğit
python improved_model_training.py
```

## 4️⃣ Web Uygulamasını Çalıştır
```bash
python app.py
```

## 5️⃣ Tarayıcıda Aç
```
http://localhost:5000
```

---

## ⚡ Hızlı Başlangıç (Model varsa)
Eğer `models/` klasöründe model dosyaları varsa, direkt:
```bash
python app.py
```

---

## ⚠️ Önemli Notlar
- **Model yoksa:** Web uygulaması çalışır ama tahmin yapamaz
- **API anahtarı:** Sadece veri toplamak için gerekli, web uygulaması için değil
- **Port:** Varsayılan port 5000, değiştirmek için `.env` dosyasında `FLASK_PORT=8080` ekleyin

