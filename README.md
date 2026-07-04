# 🎓 AI Destekli Akıllı Sınav Hazırlama Sistemi

> **Hasan Yiğit Çontar** — Final Projesi 2  
> Google Gemini API + Streamlit + SQLite ile geliştirilmiş akıllı sınav üretim platformu.

---

## 🌐 Canlı Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

---

## 📸 Ekran Görüntüleri

| Sınav Oluşturma | Soru Listesi | Geçmiş Sınavlar |
|:-:|:-:|:-:|
| ![create](assets/screenshot_create.png) | ![questions](assets/screenshot_questions.png) | ![history](assets/screenshot_history.png) |

---

## 🚀 Özellikler

### Temel Özellikler
| Özellik | Durum |
|---------|-------|
| 🤖 Gemini API entegrasyonu | ✅ |
| 📝 Çoktan seçmeli test soruları | ✅ |
| ✍️ Klasik açık uçlu sorular | ✅ |
| 📖 Konu özeti üretimi | ✅ |
| 💡 Çalışma tavsiyesi | ✅ |
| 🔑 Cevap anahtarı (gizli/açık) | ✅ |
| 💾 SQLite veritabanı | ✅ |
| 🎨 Karanlık tema | ✅ |

### Bonus Özellikler
| Özellik | Durum |
|---------|-------|
| 📄 PDF dışa aktarma | ✅ |
| 📝 Word (.docx) dışa aktarma | ✅ |
| 📊 CSV dışa aktarma | ✅ |
| 📚 Geçmiş sınavları görüntüleme | ✅ |
| 🔍 Sınav geçmişinde arama | ✅ |
| 🤖 İki farklı AI modeli (Gemini/Groq) | ✅ |
| 🗑️ Sınav silme | ✅ |
| 📈 İstatistik paneli | ✅ |

---

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit Arayüzü (app.py)             │
│  ┌────────────┐  ┌────────────────┐  ┌────────────────┐ │
│  │ Sınav      │  │ Geçmiş Sınavlar│  │ Dışa Aktarma   │ │
│  │ Oluşturma  │  │ + Arama        │  │ PDF/Word/CSV   │ │
│  └─────┬──────┘  └───────┬────────┘  └───────┬────────┘ │
└────────┼─────────────────┼───────────────────┼──────────┘
         │                 │                   │
         ▼                 ▼                   ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────────┐
│ ai_service  │   │ database.py │   │  pdf_export.py  │
│   .py       │   │  (SQLite)   │   │  fpdf2/docx     │
├─────────────┤   ├─────────────┤   └─────────────────┘
│ Gemini API  │   │ exams.db    │
│ Groq API    │   │ CRUD ops    │
└─────────────┘   └─────────────┘
```

---

## 🗄️ Veritabanı Şeması

```sql
CREATE TABLE exams (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    konu              TEXT    NOT NULL,
    tarih             TEXT    NOT NULL,          -- ISO 8601
    soru_sayisi       INTEGER NOT NULL,
    zorluk            TEXT    NOT NULL,          -- Kolay/Orta/Zor
    ai_model          TEXT    NOT NULL,          -- Gemini/Groq + model adı
    olusturulan_sinav TEXT    NOT NULL           -- JSON formatında tam sınav
);
```

---

## 📦 Kurulum

### 1. Repoyu Klonla

```bash
git clone https://github.com/kullanici-adi/ai-sinav-hazirlayici.git
cd ai-sinav-hazirlayici
```

### 2. Sanal Ortam Oluştur (Önerilen)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Bağımlılıkları Yükle

```bash
pip install -r requirements.txt
```

### 4. API Anahtarlarını Ayarla

`.env.example` dosyasını kopyalayıp `.env` olarak kaydet:

```bash
cp .env.example .env
```

`.env` dosyasını düzenle:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here   # Opsiyonel
```

#### API Anahtarı Alma:
- **Gemini**: [Google AI Studio](https://aistudio.google.com/) → API Keys → Create API Key
- **Groq** (ücretsiz): [console.groq.com](https://console.groq.com) → API Keys

### 5. Uygulamayı Başlat

```bash
streamlit run app.py
```

Tarayıcınızda `http://localhost:8501` açılacaktır.

---

## 🎮 Kullanım

1. **Sol menüden "Yeni Sınav Oluştur"** sekmesini seçin.
2. **Konu adını** girin (örn: *"Python Listeler"*, *"I. Dünya Savaşı"*).
3. **AI modelini** seçin: Gemini veya Groq.
4. **Soru sayısını** slider ile ayarlayın (3–20).
5. **Zorluk seviyesini** seçin: Kolay / Orta / Zor.
6. **"🚀 Sınavı Hazırla"** butonuna tıklayın.
7. Sınav otomatik olarak **veritabanına kaydedilir**.
8. İstediğiniz formatta **indirebilirsiniz**: PDF / Word / CSV.

---

## 📁 Proje Yapısı

```
final-bitirme-projesi-3/
├── app.py              # Ana Streamlit uygulaması
├── ai_service.py       # Gemini & Groq API entegrasyonu
├── database.py         # SQLite veritabanı katmanı
├── pdf_export.py       # PDF, Word, CSV dışa aktarma
├── requirements.txt    # Python bağımlılıkları
├── .env.example        # Örnek ortam değişkenleri
├── .env                # Gerçek API anahtarları (git'e ekleme!)
├── README.md           # Bu dosya
└── exams.db            # SQLite veritabanı (otomatik oluşur)
```

---

## 🤖 AI Prompt Tasarımı

Sistem, yapay zekâdan **sabit bir JSON şeması** üretmesini ister:

```json
{
  "ozet": "Konunun özet açıklaması",
  "test_sorulari": [
    {
      "soru": "Soru metni",
      "secenekler": { "A": "...", "B": "...", "C": "...", "D": "..." },
      "dogru": "A"
    }
  ],
  "klasik_sorular": ["Soru 1", "Soru 2", "...", "Soru 5"],
  "calisma_onerisi": "Pratik çalışma tavsiyeleri"
}
```

Gemini API `response_mime_type='application/json'` ile yapılandırılmıştır.

---

## 🛠️ Kullanılan Teknolojiler

| Teknoloji | Sürüm | Kullanım |
|-----------|-------|---------|
| Python | 3.10+ | Ana dil |
| Streamlit | ≥1.35 | Web arayüzü |
| google-generativeai | ≥0.7 | Gemini API |
| groq | ≥0.9 | Groq API (bonus) |
| SQLite3 | stdlib | Veritabanı |
| fpdf2 | ≥2.7 | PDF üretimi |
| python-docx | ≥1.1 | Word üretimi |
| python-dotenv | ≥1.0 | Ortam değişkenleri |

---

## 📊 Değerlendirme Kriterleri

| Kriter | Puan | Durum |
|--------|------|-------|
| Arayüz Tasarımı (Streamlit) | 20 | ✅ Premium karanlık tema |
| AI Entegrasyonu | 25 | ✅ Gemini + Groq |
| Prompt Tasarımı | 15 | ✅ JSON şemalı prompt |
| SQLite Veritabanı | 15 | ✅ Tam CRUD + arama |
| Kod Düzeni | 10 | ✅ Modüler yapı |
| GitHub + README | 10 | ✅ Bu dosya |
| Bonus Özellikler | 5 | ✅ PDF/Word/CSV/Groq/Arama |

---

## 📄 Lisans

MIT License — Hasan Yiğit Çontar, 2026
