# 🔗 Cursor'u GitHub'a Bağlama Kılavuzu

## 📋 Ön Gereksinimler

1. ✅ GitHub hesabınız olmalı (https://github.com)
2. ✅ Cursor uygulaması yüklü olmalı
3. ✅ İnternet bağlantınız olmalı

---

## 🚀 Adım Adım Bağlantı

### Adım 1: Cursor'da GitHub Ayarlarını Açma

1. **Cursor uygulamasını açın**
2. **Settings (Ayarlar) menüsüne gidin:**
   - **Windows/Linux:** `Ctrl + ,` (virgül tuşu) veya `File > Preferences > Settings`
   - **Mac:** `Cmd + ,` (virgül tuşu) veya `Cursor > Preferences > Settings`
3. **Arama kutusuna** `github` yazın
4. **"GitHub"** veya **"Git: GitHub"** ayarlarını bulun

---

### Adım 2: GitHub Authentication (Kimlik Doğrulama)

#### Yöntem A: Cursor Settings Üzerinden

1. **Settings** sayfasında **"GitHub"** bölümünü bulun
2. **"Sign in with GitHub"** veya **"Connect GitHub Account"** butonuna tıklayın
3. Tarayıcınız açılacak ve GitHub giriş sayfasına yönlendirileceksiniz
4. GitHub hesabınızla giriş yapın
5. **"Authorize Cursor"** veya **"Authorize application"** butonuna tıklayın
6. Cursor'a dönün, bağlantı başarılı olacaktır

#### Yöntem B: Command Palette Üzerinden

1. **Command Palette'i açın:**
   - **Windows/Linux:** `Ctrl + Shift + P`
   - **Mac:** `Cmd + Shift + P`
2. **"GitHub: Sign in"** veya **"GitHub: Connect"** yazın ve seçin
3. Tarayıcıda GitHub giriş sayfası açılacak
4. GitHub hesabınızla giriş yapın
5. İzinleri onaylayın
6. Cursor'a dönün

---

### Adım 3: GitHub Token Oluşturma (Alternatif Yöntem)

Eğer yukarıdaki yöntemler çalışmazsa, manuel token oluşturabilirsiniz:

#### 3.1. GitHub'da Personal Access Token Oluşturma

1. **GitHub'a giriş yapın:** https://github.com
2. **Profil fotoğrafınıza tıklayın** (sağ üst köşe)
3. **"Settings"** seçeneğine tıklayın
4. Sol menüden **"Developer settings"** seçin
5. **"Personal access tokens"** > **"Tokens (classic)"** seçin
6. **"Generate new token"** > **"Generate new token (classic)"** tıklayın
7. **Token ayarlarını yapın:**
   - **Note:** "Cursor IDE Access" (açıklama)
   - **Expiration:** İstediğiniz süre (örn: 90 days, 1 year)
   - **Scopes (İzinler):** Şunları işaretleyin:
     - ✅ `repo` (Tüm repository'ler)
     - ✅ `workflow` (GitHub Actions)
     - ✅ `read:org` (Organizasyon okuma - opsiyonel)
8. **"Generate token"** butonuna tıklayın
9. **Token'ı kopyalayın** (bir daha gösterilmeyecek!)

#### 3.2. Token'ı Cursor'a Ekleme

1. **Cursor'da Command Palette'i açın:** `Ctrl + Shift + P` (veya `Cmd + Shift + P`)
2. **"GitHub: Set Personal Access Token"** yazın ve seçin
3. Kopyaladığınız token'ı yapıştırın
4. Enter'a basın

---

### Adım 4: Git Kullanıcı Bilgilerini Ayarlama

Cursor'da Git kullanıcı bilgilerinizi ayarlayın:

1. **Command Palette'i açın:** `Ctrl + Shift + P`
2. **"Git: Open Settings"** yazın
3. Veya **Settings** > **"Git"** bölümüne gidin
4. Şu ayarları yapın:
   - **Git: User Name:** GitHub kullanıcı adınız
   - **Git: User Email:** GitHub email adresiniz

**Terminal üzerinden de yapabilirsiniz:**
```bash
git config --global user.name "mhmtdmr155"
git config --global user.email "your-email@example.com"
```

---

### Adım 5: Bağlantıyı Test Etme

1. **Cursor'da bir terminal açın:**
   - `Ctrl + ~` (tilde tuşu) veya `View > Terminal`
2. **Git durumunu kontrol edin:**
   ```bash
   git status
   ```
3. **GitHub repository'nizi kontrol edin:**
   ```bash
   git remote -v
   ```
4. **Test commit yapın:**
   ```bash
   git add .
   git commit -m "Test: Cursor GitHub bağlantısı testi"
   git push origin main
   ```

---

## 🔍 Sorun Giderme

### Problem 1: "Authentication failed" Hatası

**Çözüm:**
1. GitHub token'ınızın süresi dolmuş olabilir
2. Yeni bir token oluşturun (Adım 3)
3. Cursor'da token'ı güncelleyin

### Problem 2: "Permission denied" Hatası

**Çözüm:**
1. Token'ınızda `repo` izninin olduğundan emin olun
2. Repository'nin private/public durumunu kontrol edin
3. Token'ı yeniden oluşturun

### Problem 3: Cursor GitHub ayarlarını bulamıyorum

**Çözüm:**
1. Cursor'u en son sürüme güncelleyin
2. Command Palette'de `GitHub` yazarak tüm GitHub komutlarını görün
3. Settings'de `@github` yazarak GitHub ile ilgili tüm ayarları görün

### Problem 4: Git push çalışmıyor

**Çözüm:**
1. Git kullanıcı bilgilerinizi kontrol edin:
   ```bash
   git config --global user.name
   git config --global user.email
   ```
2. Remote repository'yi kontrol edin:
   ```bash
   git remote -v
   ```
3. SSH yerine HTTPS kullanıyorsanız, token ile authentication yapın

---

## ✅ Başarı Kontrol Listesi

- [ ] GitHub hesabına giriş yapıldı
- [ ] Cursor'da GitHub authentication tamamlandı
- [ ] Git kullanıcı bilgileri ayarlandı
- [ ] `git status` komutu çalışıyor
- [ ] `git push` komutu başarılı
- [ ] GitHub'da değişiklikler görünüyor

---

## 🎯 Cursor GitHub Özellikleri

Cursor GitHub'a bağlandıktan sonra şu özellikleri kullanabilirsiniz:

1. **GitHub Copilot** (eğer aboneliğiniz varsa)
2. **Repository yönetimi** doğrudan Cursor'dan
3. **Pull Request oluşturma ve yönetme**
4. **Issue tracking**
5. **GitHub Actions entegrasyonu**
6. **Code review** özellikleri

---

## 📚 Ek Kaynaklar

- **Cursor Dokümantasyonu:** https://cursor.sh/docs
- **GitHub Personal Access Tokens:** https://github.com/settings/tokens
- **Git Dokümantasyonu:** https://git-scm.com/doc

---

## 💡 İpuçları

1. **Token güvenliği:** Token'ınızı asla paylaşmayın ve public repository'lere commit etmeyin
2. **Token süresi:** Uzun süreli projeler için 1 yıl veya daha uzun süre seçin
3. **İzinler:** Sadece ihtiyacınız olan izinleri verin (principle of least privilege)
4. **2FA:** GitHub hesabınızda 2FA (Two-Factor Authentication) aktifse, token oluşturmanız gerekir

---

**Son Güncelleme:** 2025-01-27
**Cursor Versiyonu:** En son sürüm önerilir

